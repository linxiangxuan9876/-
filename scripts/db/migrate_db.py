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
    print("  Database Migration Started")
    print("="*80)

    changes_made = False

    # 1. Check and create document_qas table
    if 'document_qas' not in inspector.get_table_names():
        print("\n[1/4] Creating document_qas table...")

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
        print("OK - document_qas table created")
        changes_made = True
    else:
        print("\n[1/4] document_qas table exists, skipping")

    # 2. Check qa_items table and add missing columns
    print("\n[2/4] Checking qa_items table columns...")
    qa_columns = [col['name'] for col in inspector.get_columns('qa_items')]

    qa_missing_columns = []

    if 'is_deleted' not in qa_columns:
        qa_missing_columns.append('is_deleted INTEGER DEFAULT 0')

    if 'deleted_at' not in qa_columns:
        qa_missing_columns.append('deleted_at DATETIME')

    if qa_missing_columns:
        print(f"  Found missing columns: {', '.join(qa_missing_columns)}")

        for col_def in qa_missing_columns:
            col_name = col_def.split()[0]
            print(f"  Adding column {col_name}...")
            try:
                alter_sql = f"ALTER TABLE qa_items ADD COLUMN {col_def}"
                db.execute(text(alter_sql))
                db.commit()
                print(f"  OK - Added {col_name}")
                changes_made = True
            except Exception as e:
                print(f"  ERROR - Adding {col_name} failed: {e}")
    else:
        print("  OK - qa_items table columns complete")

    # 3. Check documents table and add missing columns
    print("\n[3/4] Checking documents table columns...")
    doc_columns = [col['name'] for col in inspector.get_columns('documents')]

    doc_missing_columns = []

    if 'file_type' not in doc_columns:
        doc_missing_columns.append('file_type VARCHAR(50)')

    if 'parsed_content' not in doc_columns:
        doc_missing_columns.append('parsed_content TEXT')

    if 'parsed_metadata' not in doc_columns:
        doc_missing_columns.append('parsed_metadata JSON')

    if 'parse_error' not in doc_columns:
        doc_missing_columns.append('parse_error TEXT')

    if doc_missing_columns:
        print(f"  Found missing columns: {', '.join(doc_missing_columns)}")

        for col_def in doc_missing_columns:
            col_name = col_def.split()[0]
            print(f"  Adding column {col_name}...")
            try:
                alter_sql = f"ALTER TABLE documents ADD COLUMN {col_def}"
                db.execute(text(alter_sql))
                db.commit()
                print(f"  OK - Added {col_name}")
                changes_made = True
            except Exception as e:
                print(f"  ERROR - Adding {col_name} failed: {e}")
    else:
        print("  OK - documents table columns complete")

    # 4. Statistics
    print("\n[4/4] Statistics")
    print("-" * 80)

    try:
        doc_count = db.execute(text("SELECT COUNT(*) FROM documents")).scalar()
        print(f"  documents table records: {doc_count}")
    except:
        doc_count = 0
        print("  documents table does not exist or cannot query")

    try:
        qa_count = db.execute(text("SELECT COUNT(*) FROM qa_items")).scalar()
        print(f"  qa_items table records: {qa_count}")
    except:
        qa_count = 0
        print("  qa_items table does not exist or cannot query")

    if 'document_qas' in inspector.get_table_names():
        try:
            doc_qa_count = db.execute(text("SELECT COUNT(*) FROM document_qas")).scalar()
            print(f"  document_qas table records: {doc_qa_count}")
        except:
            print("  document_qas table cannot query")

    # 5. Update existing document statuses
    if doc_count > 0:
        print("\n  Checking existing document statuses...")

        try:
            docs = db.execute(text("SELECT id, filename, status FROM documents")).fetchall()

            for doc in docs:
                doc_id, filename, status = doc

                if not status or status not in ['pending', 'parsing', 'parsed', 'approved', 'rejected']:
                    print(f"  Updating document {filename} status to pending...")
                    db.execute(text(f"UPDATE documents SET status = 'pending' WHERE id = {doc_id}"))
                    db.commit()
        except Exception as e:
            print(f"  ERROR - Updating document status failed: {e}")

    db.close()

    print("\n" + "="*80)
    if changes_made:
        print("  Migration completed successfully!")
    else:
        print("  Database is up to date, no migration needed")
    print("="*80 + "\n")

    return changes_made

if __name__ == "__main__":
    migrate_database()
