"""
检查数据库表结构
"""
from app.core.database import SessionLocal, engine
from sqlalchemy import inspect

def check_table_structure():
    db = SessionLocal()
    inspector = inspect(engine)
    
    print("\n" + "="*80)
    print("  数据库表结构检查")
    print("="*80)
    
    # 获取所有表
    tables = inspector.get_table_names()
    print(f"\n数据库表列表：{tables}")
    
    # 检查 documents 表
    if 'documents' in tables:
        print("\n" + "-"*80)
        print("  documents 表结构:")
        print("-"*80)
        columns = inspector.get_columns('documents')
        for col in columns:
            print(f"  - {col['name']}: {col['type']} (nullable={col['nullable']})")
    
    # 检查 document_qas 表
    if 'document_qas' in tables:
        print("\n" + "-"*80)
        print("  document_qas 表结构:")
        print("-"*80)
        columns = inspector.get_columns('document_qas')
        for col in columns:
            print(f"  - {col['name']}: {col['type']} (nullable={col['nullable']})")
    
    db.close()
    
    print("\n" + "="*80)

if __name__ == "__main__":
    check_table_structure()
