"""
数据库迁移脚本：添加缺失的表和字段
"""
from app.core.database import engine, SessionLocal
from sqlalchemy import inspect, text
from datetime import datetime

def migrate_database():
    db = SessionLocal()
    inspector = inspect(engine)
    
    print("\n" + "="*80)
    print("  数据库迁移开始")
    print("="*80)
    
    changes_made = False
    
    # 1. 检查并创建 document_qas 表
    if 'document_qas' not in inspector.get_table_names():
        print("\n[1/3] 创建 document_qas 表...")
        
        create_table_sql = """
        CREATE TABLE document_qas (
            id INTEGER PRIMARY KEY,
            document_id INTEGER NOT NULL,
            store_id VARCHAR(50) NOT NULL,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            main_category VARCHAR(100),
            sub_category VARCHAR(100),
            status VARCHAR(8) DEFAULT 'pending' NOT NULL,
            is_merged INTEGER DEFAULT 0,
            merged_at DATETIME,
            created_at DATETIME,
            updated_at DATETIME
        )
        """
        
        db.execute(text(create_table_sql))
        db.commit()
        print("✅ document_qas 表创建成功")
        changes_made = True
    else:
        print("\n[1/3] document_qas 表已存在，跳过")
    
    # 2. 检查 documents 表并添加缺失的字段
    print("\n[2/3] 检查 documents 表字段...")
    doc_columns = [col['name'] for col in inspector.get_columns('documents')]
    
    missing_columns = []
    
    if 'file_type' not in doc_columns:
        missing_columns.append('file_type VARCHAR(50)')
    
    if 'parsed_content' not in doc_columns:
        missing_columns.append('parsed_content TEXT')
    
    if 'parsed_metadata' not in doc_columns:
        missing_columns.append('parsed_metadata JSON')
    
    if 'parse_error' not in doc_columns:
        missing_columns.append('parse_error TEXT')
    
    if missing_columns:
        print(f"  发现缺失字段：{', '.join(missing_columns)}")
        
        for col_def in missing_columns:
            col_name = col_def.split()[0]
            print(f"  添加字段 {col_name}...")
            alter_sql = f"ALTER TABLE documents ADD COLUMN {col_def}"
            db.execute(text(alter_sql))
            db.commit()
            print(f"  ✅ 添加 {col_name} 成功")
        
        changes_made = True
    else:
        print("  ✅ documents 表字段完整")
    
    # 3. 统计信息
    print("\n[3/3] 统计信息")
    print("-" * 80)
    
    doc_count = db.execute(text("SELECT COUNT(*) FROM documents")).scalar()
    print(f"  documents 表记录数：{doc_count}")
    
    if 'document_qas' in inspector.get_table_names():
        qa_count = db.execute(text("SELECT COUNT(*) FROM document_qas")).scalar()
        print(f"  document_qas 表记录数：{qa_count}")
    
    # 4. 更新现有文档的状态（如果需要）
    if doc_count > 0:
        print("\n  检查现有文档状态...")
        
        # 查询所有文档
        docs = db.execute(text("SELECT id, filename, status FROM documents")).fetchall()
        
        for doc in docs:
            doc_id, filename, status = doc
            
            # 如果状态是空或者不是有效状态，更新为 pending
            if not status or status not in ['pending', 'parsing', 'parsed', 'approved', 'rejected']:
                print(f"  更新文档 {filename} 状态为 pending...")
                db.execute(text(f"UPDATE documents SET status = 'pending' WHERE id = {doc_id}"))
                db.commit()
    
    db.close()
    
    print("\n" + "="*80)
    if changes_made:
        print("  ✅ 数据库迁移完成！")
    else:
        print("  ℹ️ 数据库已是最新，无需迁移")
    print("="*80 + "\n")
    
    return changes_made

if __name__ == "__main__":
    migrate_database()
