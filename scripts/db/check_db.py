from app.core.database import SessionLocal
from app.models import Document, QA_Item, DocumentQA, DocStatus, QAStatus


def check_db():
    db = SessionLocal()
    try:
        print("=" * 60)
        print("数据库检查")
        print("=" * 60)

        # 检查文档
        print("\n【1】文档表 (documents):")
        docs = db.query(Document).all()
        print(f"  总数: {len(docs)}")
        for doc in docs:
            print(f"    ID: {doc.id}, 门店: {doc.store_id}, 文件: {doc.original_filename}, 状态: {doc.status.value}")

        # 检查QA项
        print("\n【2】QA项表 (qa_items):")
        qas = db.query(QA_Item).all()
        print(f"  总数: {len(qas)}")
        for qa in qas:
            print(f"    ID: {qa.id}, 门店: {qa.store_id}, 状态: {qa.status.value}, 删除: {qa.is_deleted}")

        # 检查文档QA
        print("\n【3】文档QA表 (document_qas):")
        doc_qas = db.query(DocumentQA).all()
        print(f"  总数: {len(doc_qas)}")
        for qa in doc_qas:
            print(f"    ID: {qa.id}, 文档ID: {qa.document_id}, 门店: {qa.store_id}, 状态: {qa.status.value}, 已合并: {qa.is_merged}")

        print("\n" + "=" * 60)
        print("检查完成")
        print("=" * 60)

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    check_db()
