from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
import os
import io
from pydantic import BaseModel

from app.core import get_db, get_current_admin
from app.models import User, Document, QA_Item, QAStatus


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
    total_docs = db.query(Document).count()
    total_qa = db.query(QA_Item).filter(QA_Item.is_deleted == False).count()

    # 按状态统计Q&A数量（排除已删除）
    qa_by_status = db.query(
        QA_Item.status,
        db.func.count(QA_Item.id).label('count')
    ).filter(QA_Item.is_deleted == False).group_by(QA_Item.status).all()

    # 回收站数量
    recycle_bin_count = db.query(QA_Item).filter(QA_Item.is_deleted == True).count()

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
        "total_qa_items": total_qa,
        "recycle_bin_count": recycle_bin_count,
        "qa_by_status": status_counts,
        "published_count": status_counts.get('published', 0),
        "pending_count": status_counts.get('pending_review', 0),
        "rejected_count": status_counts.get('rejected', 0),
        "documents_by_store": {item.store_id: item.count for item in docs_by_store},
        "qa_by_category": {item.main_category: item.count for item in qa_by_category}
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
