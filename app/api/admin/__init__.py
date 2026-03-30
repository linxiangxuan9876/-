from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from pathlib import Path
import os
import io
from pydantic import BaseModel

from app.core import get_db, get_current_admin
from app.models import User, Document, DocStatus, QA_Item, QAStatus, DocumentQA


class CategoryUpdate(BaseModel):
    main_category: str
    sub_category: str

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

router = APIRouter(prefix="/admin", tags=["管理员端接口"])

@router.get("/all_docs")
async def get_all_docs(
    car_model: Optional[str] = Query(None, description="按车型过滤"),
    store_id: Optional[str] = Query(None, description="按门店ID过滤"),
    status: Optional[str] = Query(None, description="按状态过滤"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    query = db.query(Document)

    if car_model:
        query = query.filter(Document.car_model == car_model)
    if store_id:
        query = query.filter(Document.store_id == store_id)
    if status:
        query = query.filter(Document.status == status)

    total = query.count()
    docs = query.order_by(Document.created_at.desc()).offset(skip).limit(limit).all()

    return {
        "total": total,
        "documents": [
            {
                "id": doc.id,
                "store_id": doc.store_id,
                "store_name": doc.store_name,
                "filename": doc.filename,
                "original_filename": doc.original_filename,
                "file_size": doc.file_size,
                "car_model": doc.car_model,
                "category": doc.category,
                "status": doc.status.value,
                "created_at": doc.created_at.isoformat() if doc.created_at else None
            }
            for doc in docs
        ]
    }

@router.delete("/delete_doc/{doc_id}")
async def delete_document(
    doc_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == doc_id).first()

    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")

    file_path = doc.file_path
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"删除文件失败: {str(e)}")

    db.delete(doc)
    db.commit()

    return {"message": "文档删除成功", "doc_id": doc_id}

@router.get("/all_qa")
async def get_all_qa(
    main_category: Optional[str] = Query(None, description="按大类过滤"),
    sub_category: Optional[str] = Query(None, description="按小类过滤"),
    store_id: Optional[str] = Query(None, description="按门店ID过滤"),
    status: Optional[str] = Query(None, description="按状态过滤"),
    include_deleted: bool = Query(False, description="是否包含已删除"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    query = db.query(QA_Item)

    # 默认不显示已删除的
    if not include_deleted:
        query = query.filter(QA_Item.is_deleted == False)

    if main_category:
        query = query.filter(QA_Item.main_category == main_category)
    if sub_category:
        query = query.filter(QA_Item.sub_category == sub_category)
    if store_id:
        query = query.filter(QA_Item.store_id == store_id)
    if status:
        query = query.filter(QA_Item.status == status)

    total = query.count()
    items = query.order_by(QA_Item.created_at.desc()).offset(skip).limit(limit).all()

    return {
        "total": total,
        "items": [
            {
                "id": item.id,
                "store_id": item.store_id,
                "main_category": item.main_category,
                "sub_category": item.sub_category,
                "question": item.question,
                "answer": item.answer,
                "status": item.status.value,
                "is_deleted": item.is_deleted,
                "deleted_at": item.deleted_at.isoformat() if item.deleted_at else None,
                "created_at": item.created_at.isoformat() if item.created_at else None
            }
            for item in items
        ]
    }

@router.put("/review_qa/{qa_id}")
async def review_qa(
    qa_id: int,
    status: str,
    main_category: Optional[str] = Query(None, description="修改后的大类"),
    sub_category: Optional[str] = Query(None, description="修改后的小类"),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """审核Q&A，通过或拒绝，支持修改分类"""
    qa_item = db.query(QA_Item).filter(QA_Item.id == qa_id).first()

    if not qa_item:
        raise HTTPException(status_code=404, detail="Q&A不存在")

    if status not in ["published", "rejected"]:
        raise HTTPException(status_code=400, detail="状态必须是 published 或 rejected")

    qa_item.status = QAStatus.published if status == "published" else QAStatus.rejected

    # 如果提供了新的分类，则更新
    if main_category and sub_category:
        from app.services.kb_categories import KB_CATEGORIES
        if main_category in KB_CATEGORIES and sub_category in KB_CATEGORIES[main_category]:
            qa_item.main_category = main_category
            qa_item.sub_category = sub_category

    db.commit()

    return {
        "message": "审核成功",
        "qa_id": qa_id,
        "status": status,
        "main_category": qa_item.main_category,
        "sub_category": qa_item.sub_category
    }

@router.get("/categories")
async def get_categories(
    current_user: User = Depends(get_current_admin)
):
    """获取所有分类体系"""
    from app.services.kb_categories import KB_CATEGORIES
    return {
        "categories": KB_CATEGORIES
    }


@router.put("/update_category/{qa_id}")
async def update_category(
    qa_id: int,
    category_update: CategoryUpdate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """仅更新Q&A的分类，不改变审核状态"""
    qa_item = db.query(QA_Item).filter(QA_Item.id == qa_id).first()

    if not qa_item:
        raise HTTPException(status_code=404, detail="Q&A不存在")

    from app.services.kb_categories import KB_CATEGORIES
    if category_update.main_category not in KB_CATEGORIES or category_update.sub_category not in KB_CATEGORIES[category_update.main_category]:
        raise HTTPException(status_code=400, detail="无效的分类")

    qa_item.main_category = category_update.main_category
    qa_item.sub_category = category_update.sub_category

    db.commit()

    return {
        "message": "分类更新成功",
        "qa_id": qa_id,
        "main_category": qa_item.main_category,
        "sub_category": qa_item.sub_category
    }

@router.put("/review_qa_batch")
async def review_qa_batch(
    qa_ids: List[int],
    status: str,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """批量审核Q&A"""
    if status not in ["published", "rejected"]:
        raise HTTPException(status_code=400, detail="状态必须是 published 或 rejected")
    
    updated_count = db.query(QA_Item).filter(
        QA_Item.id.in_(qa_ids)
    ).update(
        {"status": QAStatus.published if status == "published" else QAStatus.rejected},
        synchronize_session=False
    )
    db.commit()
    
    return {
        "message": f"批量审核成功，共{updated_count}条",
        "updated_count": updated_count,
        "status": status
    }

@router.delete("/delete_qa_batch")
async def delete_qa_batch(
    qa_ids: List[int],
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """批量软删除Q&A（移入回收站）"""
    from sqlalchemy import func

    updated_count = db.query(QA_Item).filter(
        QA_Item.id.in_(qa_ids),
        QA_Item.is_deleted == False
    ).update(
        {"is_deleted": True, "deleted_at": func.now()},
        synchronize_session=False
    )
    db.commit()

    return {
        "message": f"已移入回收站，共{updated_count}条",
        "deleted_count": updated_count
    }

@router.get("/recycle_bin")
async def get_recycle_bin(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取回收站中的Q&A"""
    query = db.query(QA_Item).filter(QA_Item.is_deleted == True)

    total = query.count()
    items = query.order_by(QA_Item.deleted_at.desc()).offset(skip).limit(limit).all()

    return {
        "total": total,
        "items": [
            {
                "id": item.id,
                "store_id": item.store_id,
                "main_category": item.main_category,
                "sub_category": item.sub_category,
                "question": item.question,
                "answer": item.answer,
                "status": item.status.value,
                "deleted_at": item.deleted_at.isoformat() if item.deleted_at else None,
                "created_at": item.created_at.isoformat() if item.created_at else None
            }
            for item in items
        ]
    }

@router.put("/restore_qa_batch")
async def restore_qa_batch(
    qa_ids: List[int],
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """批量恢复Q&A（从回收站还原）"""
    updated_count = db.query(QA_Item).filter(
        QA_Item.id.in_(qa_ids),
        QA_Item.is_deleted == True
    ).update(
        {"is_deleted": False, "deleted_at": None},
        synchronize_session=False
    )
    db.commit()

    return {
        "message": f"批量恢复成功，共{updated_count}条",
        "restored_count": updated_count
    }

@router.delete("/permanent_delete_qa_batch")
async def permanent_delete_qa_batch(
    qa_ids: List[int],
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """批量彻底删除Q&A（从回收站永久删除）"""
    deleted_count = db.query(QA_Item).filter(
        QA_Item.id.in_(qa_ids),
        QA_Item.is_deleted == True
    ).delete(synchronize_session=False)
    db.commit()

    return {
        "message": f"彻底删除成功，共{deleted_count}条",
        "deleted_count": deleted_count
    }

@router.get("/stats")
async def get_stats(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    # 文档统计
    total_docs = db.query(Document).count()
    doc_parsing = db.query(Document).filter(Document.status == DocStatus.parsing).count()
    doc_parsed = db.query(Document).filter(Document.status == DocStatus.parsed).count()

    # Q&A统计（排除已删除）
    total_qa = db.query(QA_Item).filter(QA_Item.is_deleted == False).count()

    # 按状态统计Q&A数量（排除已删除）
    qa_by_status = db.query(
        QA_Item.status,
        db.func.count(QA_Item.id).label('count')
    ).filter(QA_Item.is_deleted == False).group_by(QA_Item.status).all()

    # 回收站数量
    recycle_bin_count = db.query(QA_Item).filter(QA_Item.is_deleted == True).count()

    # 文档Q&A统计
    total_doc_qas = db.query(DocumentQA).count()
    doc_qa_pending = db.query(DocumentQA).filter(DocumentQA.status == DocStatus.pending).count()
    doc_qa_approved = db.query(DocumentQA).filter(DocumentQA.status == DocStatus.approved).count()
    doc_qa_merged = db.query(DocumentQA).filter(DocumentQA.is_merged == 1).count()

    docs_by_store = db.query(
        Document.store_id,
        db.func.count(Document.id).label('count')
    ).group_by(Document.store_id).all()

    qa_by_category = db.query(
        QA_Item.main_category,
        db.func.count(QA_Item.id).label('count')
    ).filter(QA_Item.status == QAStatus.published, QA_Item.is_deleted == False).group_by(QA_Item.main_category).all()

    # 构建状态统计字典
    status_counts = {str(item.status.value): item.count for item in qa_by_status}

    return {
        "total_documents": total_docs,
        "doc_parsing_count": doc_parsing,
        "doc_parsed_count": doc_parsed,
        "total_qa_items": total_qa,
        "recycle_bin_count": recycle_bin_count,
        "qa_by_status": status_counts,
        "published_count": status_counts.get('published', 0),
        "pending_count": status_counts.get('pending_review', 0),
        "rejected_count": status_counts.get('rejected', 0),
        "documents_by_store": {item.store_id: item.count for item in docs_by_store},
        "qa_by_category": {item.main_category: item.count for item in qa_by_category},
        # 文档Q&A统计
        "total_doc_qas": total_doc_qas,
        "doc_qa_pending": doc_qa_pending,
        "doc_qa_approved": doc_qa_approved,
        "doc_qa_merged": doc_qa_merged
    }

@router.get("/export_qa")
async def export_qa(
    status: Optional[str] = Query(None, description="按状态过滤"),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """导出Q&A为Excel"""
    if not PANDAS_AVAILABLE:
        raise HTTPException(status_code=500, detail="导出功能需要pandas库")
    
    query = db.query(QA_Item)
    if status:
        query = query.filter(QA_Item.status == status)
    
    items = query.order_by(QA_Item.created_at.desc()).all()
    
    data = []
    for item in items:
        data.append({
            "ID": item.id,
            "门店ID": item.store_id,
            "大类": item.main_category,
            "小类": item.sub_category,
            "问题": item.question,
            "答案": item.answer,
            "状态": item.status.value,
            "创建时间": item.created_at.strftime("%Y-%m-%d %H:%M:%S") if item.created_at else ""
        })
    
    df = pd.DataFrame(data)
    output = io.BytesIO()
    df.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=qa_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"}
    )


# ========== 文档解析相关接口 ==========

@router.post("/parse_document/{doc_id}")
async def parse_document(
    doc_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    解析文档，提取文本和Q&A
    后台异步执行解析任务
    """
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")

    # 更新状态为解析中
    doc.status = DocStatus.parsing
    db.commit()

    # 后台执行解析
    background_tasks.add_task(_do_parse_document, doc_id, db)

    return {
        "message": "文档解析任务已启动",
        "doc_id": doc_id,
        "status": "parsing"
    }


async def _do_parse_document(doc_id: int, db: Session):
    """后台执行文档解析"""
    from app.services.document_parser import DocumentParser, DocumentQAExtractor
    from app.services.auto_classify import auto_classify

    try:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            return

        # 解析文档
        parse_result = DocumentParser.parse(doc.file_path)

        if not parse_result["success"]:
            doc.status = DocStatus.rejected
            doc.parse_error = parse_result["error"]
            db.commit()
            return

        # 保存解析结果
        doc.parsed_content = parse_result["content"]
        doc.parsed_metadata = parse_result["metadata"]
        doc.file_type = Path(doc.file_path).suffix.lower()
        doc.status = DocStatus.parsed

        # 提取Q&A
        qa_pairs = DocumentQAExtractor.extract_qa_pairs(parse_result["text_blocks"])

        # 保存提取的Q&A
        for qa in qa_pairs:
            # 自动分类
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

    except Exception as e:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if doc:
            doc.status = DocStatus.rejected
            doc.parse_error = str(e)
            db.commit()


@router.get("/document_qas/{doc_id}")
async def get_document_qas(
    doc_id: int,
    status: Optional[str] = Query(None, description="按状态过滤"),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取从文档提取的Q&A列表"""
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")

    query = db.query(DocumentQA).filter(DocumentQA.document_id == doc_id)

    if status:
        query = query.filter(DocumentQA.status == status)

    qas = query.order_by(DocumentQA.created_at.desc()).all()

    return {
        "document_id": doc_id,
        "document_name": doc.original_filename,
        "total": len(qas),
        "items": [
            {
                "id": qa.id,
                "question": qa.question,
                "answer": qa.answer,
                "main_category": qa.main_category,
                "sub_category": qa.sub_category,
                "status": qa.status.value,
                "is_merged": qa.is_merged,
                "created_at": qa.created_at.isoformat() if qa.created_at else None
            }
            for qa in qas
        ]
    }


@router.get("/all_document_qas")
async def get_all_document_qas(
    status: Optional[str] = Query(None, description="按状态过滤: pending, approved, rejected"),
    is_merged: Optional[int] = Query(None, description="是否已合并: 0=未合并, 1=已合并"),
    store_id: Optional[str] = Query(None, description="按门店过滤"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取所有文档提取的Q&A（用于审核）"""
    query = db.query(DocumentQA)

    if status:
        query = query.filter(DocumentQA.status == status)
    if is_merged is not None:
        query = query.filter(DocumentQA.is_merged == is_merged)
    if store_id:
        query = query.filter(DocumentQA.store_id == store_id)

    total = query.count()
    qas = query.order_by(DocumentQA.created_at.desc()).offset(skip).limit(limit).all()

    return {
        "total": total,
        "items": [
            {
                "id": qa.id,
                "document_id": qa.document_id,
                "store_id": qa.store_id,
                "question": qa.question,
                "answer": qa.answer,
                "main_category": qa.main_category,
                "sub_category": qa.sub_category,
                "status": qa.status.value,
                "is_merged": qa.is_merged,
                "created_at": qa.created_at.isoformat() if qa.created_at else None
            }
            for qa in qas
        ]
    }


@router.put("/review_document_qa/{qa_id}")
async def review_document_qa(
    qa_id: int,
    status: str,  # approved 或 rejected
    main_category: Optional[str] = Query(None, description="修改后的大类"),
    sub_category: Optional[str] = Query(None, description="修改后的小类"),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """审核文档提取的Q&A"""
    if status not in ["approved", "rejected"]:
        raise HTTPException(status_code=400, detail="状态必须是 approved 或 rejected")

    qa = db.query(DocumentQA).filter(DocumentQA.id == qa_id).first()
    if not qa:
        raise HTTPException(status_code=404, detail="Q&A不存在")

    qa.status = DocStatus.approved if status == "approved" else DocStatus.rejected

    # 如果提供了新的分类，则更新
    if main_category and sub_category:
        from app.services.kb_categories import KB_CATEGORIES
        if main_category in KB_CATEGORIES and sub_category in KB_CATEGORIES[main_category]:
            qa.main_category = main_category
            qa.sub_category = sub_category

    db.commit()

    return {
        "message": "审核成功",
        "qa_id": qa_id,
        "status": status
    }


@router.post("/merge_document_qa/{qa_id}")
async def merge_document_qa(
    qa_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    将文档提取的Q&A合并到全量知识库
    """
    from sqlalchemy import func

    doc_qa = db.query(DocumentQA).filter(DocumentQA.id == qa_id).first()
    if not doc_qa:
        raise HTTPException(status_code=404, detail="Q&A不存在")

    if doc_qa.status != DocStatus.approved:
        raise HTTPException(status_code=400, detail="只有已通过的Q&A才能合并")

    if doc_qa.is_merged:
        raise HTTPException(status_code=400, detail="该Q&A已合并")

    # 创建新的Q&A记录
    new_qa = QA_Item(
        store_id=doc_qa.store_id,
        main_category=doc_qa.main_category,
        sub_category=doc_qa.sub_category,
        question=doc_qa.question,
        answer=doc_qa.answer,
        status=QAStatus.published  # 直接发布
    )

    db.add(new_qa)

    # 更新文档Q&A状态
    doc_qa.is_merged = 1
    doc_qa.merged_at = func.now()

    db.commit()
    db.refresh(new_qa)

    return {
        "message": "已合并到知识库",
        "qa_id": qa_id,
        "new_qa_id": new_qa.id
    }


@router.post("/merge_document_qas_batch")
async def merge_document_qas_batch(
    qa_ids: List[int],
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """批量合并文档Q&A到知识库"""
    from sqlalchemy import func

    merged_count = 0
    errors = []

    for qa_id in qa_ids:
        doc_qa = db.query(DocumentQA).filter(DocumentQA.id == qa_id).first()

        if not doc_qa:
            errors.append(f"ID {qa_id}: 不存在")
            continue

        if doc_qa.status != DocStatus.approved:
            errors.append(f"ID {qa_id}: 未通过审核")
            continue

        if doc_qa.is_merged:
            errors.append(f"ID {qa_id}: 已合并")
            continue

        # 创建新的Q&A记录
        new_qa = QA_Item(
            store_id=doc_qa.store_id,
            main_category=doc_qa.main_category,
            sub_category=doc_qa.sub_category,
            question=doc_qa.question,
            answer=doc_qa.answer,
            status=QAStatus.published
        )

        db.add(new_qa)

        # 更新文档Q&A状态
        doc_qa.is_merged = 1
        doc_qa.merged_at = func.now()

        merged_count += 1

    db.commit()

    return {
        "message": f"批量合并完成，成功 {merged_count} 条",
        "merged_count": merged_count,
        "errors": errors
    }
