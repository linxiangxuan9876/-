from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import timedelta
import pandas as pd
import os
import uuid
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.core import get_db, create_access_token, verify_password, get_current_store_user
from app.core.config import settings
from app.models import User, Document, QA_Item, QAStatus, DocStatus, DocumentQA
from app.schemas import QAItemCreate, QAItemResponse, BatchQAResponse

router = APIRouter(prefix="/store", tags=["门店端接口"])

executor = ThreadPoolExecutor(max_workers=10)

@router.get("/info")
async def get_store_info(
    current_user: User = Depends(get_current_store_user)
):
    """获取当前门店用户信息"""
    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "store_id": current_user.store_id,
        "store_name": current_user.store_name,
        "role": current_user.role.value
    }

@router.post("/add_qa", response_model=QAItemResponse)
async def add_qa(
    qa_data: QAItemCreate,
    current_user: User = Depends(get_current_store_user),
    db: Session = Depends(get_db)
):
    from app.services.auto_classify import auto_classify

    classification = await auto_classify(qa_data.question)

    db_qa = QA_Item(
        store_id=current_user.store_id,
        main_category=classification["main_category"],
        sub_category=classification["sub_category"],
        question=qa_data.question,
        answer=qa_data.answer,
        status=QAStatus.pending_review
    )

    db.add(db_qa)
    db.commit()
    db.refresh(db_qa)

    return db_qa

@router.post("/upload_qa_batch", response_model=BatchQAResponse)
async def upload_qa_batch(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_store_user),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith('.xlsx'):
        raise HTTPException(status_code=400, detail="只支持 .xlsx 格式的Excel文件")

    temp_path = os.path.join(settings.QA_UPLOAD_DIR, f"temp_{uuid.uuid4().hex}_{file.filename}")

    try:
        os.makedirs(settings.QA_UPLOAD_DIR, exist_ok=True)

        content = await file.read()
        with open(temp_path, "wb") as f:
            f.write(content)

        df = pd.read_excel(temp_path, engine='openpyxl')

        if '问题' not in df.columns or '答案' not in df.columns:
            raise HTTPException(status_code=400, detail="Excel文件必须包含【问题】和【答案】两列")

        questions = df['问题'].tolist()
        answers = df['答案'].tolist()

        # 定义需要跳过的示例数据关键词
        skip_keywords = ['示例', '样例', '测试', 'test', 'example', 'sample']

        async def classify_and_create(idx: int) -> Optional[QA_Item]:
            from app.services.auto_classify import auto_classify

            question = str(questions[idx]) if pd.notna(questions[idx]) else ""
            answer = str(answers[idx]) if pd.notna(answers[idx]) else ""

            if not question.strip():
                return None

            # 跳过示例数据
            question_lower = question.lower()
            if any(keyword in question_lower for keyword in skip_keywords):
                return None

            # 跳过模板中的示例行（示例问题1、示例问题2等）
            if question_lower.startswith('示例问题') or question_lower.startswith('样例问题'):
                return None

            classification = await auto_classify(question)

            db_qa = QA_Item(
                store_id=current_user.store_id,
                main_category=classification["main_category"],
                sub_category=classification["sub_category"],
                question=question,
                answer=answer,
                status=QAStatus.pending_review
            )
            return db_qa

        tasks = [classify_and_create(i) for i in range(len(df))]
        results = await asyncio.gather(*tasks)

        success_items = []
        skipped_count = 0

        for db_qa in results:
            if db_qa is not None:
                db.add(db_qa)
                success_items.append(db_qa)
            else:
                skipped_count += 1

        db.commit()

        for item in success_items:
            db.refresh(item)

        return BatchQAResponse(
            success_count=len(success_items),
            failed_count=0,
            skipped_count=skipped_count,
            total_count=len(df),
            items=success_items
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    car_model: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    current_user: User = Depends(get_current_store_user),
    db: Session = Depends(get_db)
):
    """
    上传任意格式文档（PDF、Word、TXT、Excel等）
    上传后自动触发解析
    """
    from app.services.document_parser import DocumentParser

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    file_ext = os.path.splitext(file.filename)[1].lower()

    # 检查文件格式
    supported_exts = DocumentParser.SUPPORTED_EXTENSIONS | {'.xlsx', '.xls'}
    if file_ext not in supported_exts:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式: {file_ext}。支持的格式: {', '.join(supported_exts)}"
        )

    unique_filename = f"{uuid.uuid4().hex}{file_ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)

    try:
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        file_size = len(content)

        db_doc = Document(
            store_id=current_user.store_id,
            store_name=current_user.store_name,
            filename=unique_filename,
            original_filename=file.filename,
            file_path=file_path,
            file_size=file_size,
            file_type=file_ext,
            car_model=car_model,
            category=category,
            status=DocStatus.pending
        )

        db.add(db_doc)
        db.commit()
        db.refresh(db_doc)

        # 如果是Excel文件，保持原有处理逻辑
        if file_ext in ['.xlsx', '.xls']:
            return {
                "id": db_doc.id,
                "filename": unique_filename,
                "original_filename": file.filename,
                "car_model": car_model,
                "category": category,
                "status": db_doc.status.value,
                "file_type": "excel",
                "message": "Excel文件上传成功，请使用批量导入接口处理"
            }

        # 其他格式文档，自动触发解析
        # 更新状态为解析中
        db_doc.status = DocStatus.parsing
        db.commit()

        # 后台解析
        asyncio.create_task(_auto_parse_document(db_doc.id, db))

        return {
            "id": db_doc.id,
            "filename": unique_filename,
            "original_filename": file.filename,
            "car_model": car_model,
            "category": category,
            "status": "parsing",
            "file_type": file_ext,
            "message": "文档上传成功，正在自动解析中"
        }

    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


async def _auto_parse_document(doc_id: int, db: Session):
    """自动解析文档（后台任务）"""
    from app.services.document_parser import DocumentParser, DocumentQAExtractor
    from app.services.auto_classify import auto_classify
    import asyncio

    try:
        # 重新获取数据库会话
        from app.core.database import SessionLocal
        db = SessionLocal()

        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            db.close()
            return

        # 解析文档
        parse_result = DocumentParser.parse(doc.file_path)

        if not parse_result["success"]:
            doc.status = DocStatus.rejected
            doc.parse_error = parse_result["error"]
            db.commit()
            db.close()
            return

        # 保存解析结果
        doc.parsed_content = parse_result["content"]
        doc.parsed_metadata = parse_result["metadata"]
        doc.status = DocStatus.parsed

        # 提取Q&A
        qa_pairs = DocumentQAExtractor.extract_qa_pairs(parse_result["text_blocks"])

        # 保存提取的Q&A并自动分类
        for qa in qa_pairs:
            classification = await auto_classify(qa["question"])

            doc_qa = DocumentQA(
                document_id=doc_id,
                store_id=doc.store_id,
                question=qa["question"],
                answer=qa["answer"],
                main_category=classification["main_category"],
                sub_category=classification["sub_category"],
                status=DocStatus.pending,
                is_merged=0
            )
            db.add(doc_qa)

        db.commit()
        db.close()

    except Exception as e:
        from app.core.database import SessionLocal
        db = SessionLocal()
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if doc:
            doc.status = DocStatus.rejected
            doc.parse_error = str(e)
            db.commit()
        db.close()

@router.get("/my_docs")
async def get_my_docs(
    current_user: User = Depends(get_current_store_user),
    db: Session = Depends(get_db)
):
    docs = db.query(Document).filter(Document.store_id == current_user.store_id).all()

    return {
        "total": len(docs),
        "documents": docs
    }
