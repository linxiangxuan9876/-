"""
排查工具：检查文档和 DocumentQA 数据
"""
from app.core.database import SessionLocal
from app.models import Document, DocumentQA, DocStatus

def check_documents():
    db = SessionLocal()
    
    print("\n" + "="*80)
    print("  文档数据检查")
    print("="*80)
    
    # 查询所有文档
    docs = db.query(Document).order_by(Document.created_at.desc()).all()
    
    print(f"\n总文档数：{len(docs)}")
    print("\n文档列表:")
    print("-" * 80)
    
    for doc in docs:
        print(f"\nID: {doc.id}")
        print(f"  文件名：{doc.filename}")
        print(f"  原始文件名：{doc.original_filename}")
        print(f"  门店 ID: {doc.store_id}")
        print(f"  状态：{doc.status.value}")
        print(f"  文件类型：{doc.file_type}")
        print(f"  上传时间：{doc.created_at}")
        print(f"  解析内容长度：{len(doc.parsed_content) if doc.parsed_content else 0}")
        
        # 查询关联的 DocumentQA
        doc_qas = db.query(DocumentQA).filter(DocumentQA.document_id == doc.id).all()
        print(f"  关联的 DocumentQA 数量：{len(doc_qas)}")
        
        if doc_qas:
            for i, qa in enumerate(doc_qas[:3], 1):  # 只显示前 3 个
                print(f"\n    QA #{i}:")
                print(f"      问题：{qa.question[:50]}...")
                print(f"      答案：{qa.answer[:50]}...")
                print(f"      状态：{qa.status.value}")
                print(f"      分类：{qa.main_category} - {qa.sub_category}")
        
        if len(doc_qas) > 3:
            print(f"\n    ... 还有 {len(doc_qas) - 3} 条 QA")
    
    # 统计信息
    print("\n" + "="*80)
    print("  统计信息")
    print("="*80)
    
    total_docs = len(docs)
    parsed_docs = len([d for d in docs if d.status == DocStatus.parsed])
    pending_docs = len([d for d in docs if d.status == DocStatus.pending])
    docs_with_qa = len([d for d in docs if db.query(DocumentQA).filter(DocumentQA.document_id == d.id).count() > 0])
    docs_without_qa = total_docs - docs_with_qa
    
    print(f"\n总文档数：{total_docs}")
    print(f"已解析：{parsed_docs}")
    print(f"待审核：{pending_docs}")
    print(f"有 QA 的文档：{docs_with_qa}")
    print(f"无 QA 的文档：{docs_without_qa}")
    
    # 检查没有 QA 的文档
    if docs_without_qa > 0:
        print("\n" + "="*80)
        print("  没有 QA 的文档列表")
        print("="*80)
        for doc in docs:
            qa_count = db.query(DocumentQA).filter(DocumentQA.document_id == doc.id).count()
            if qa_count == 0:
                print(f"  - ID: {doc.id}, 文件名：{doc.filename}, 状态：{doc.status.value}, 类型：{doc.file_type}")
    
    # 检查 DocumentQA 的状态分布
    print("\n" + "="*80)
    print("  DocumentQA 状态分布")
    print("="*80)
    
    all_qas = db.query(DocumentQA).all()
    status_count = {}
    for qa in all_qas:
        status = qa.status.value
        status_count[status] = status_count.get(status, 0) + 1
    
    print(f"\n总 QA 数：{len(all_qas)}")
    for status, count in status_count.items():
        print(f"  {status}: {count}")
    
    db.close()
    
    print("\n" + "="*80)
    print("  排查完成")
    print("="*80)

if __name__ == "__main__":
    check_documents()
