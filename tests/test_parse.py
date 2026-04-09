"""
手动触发文档解析测试
"""
from app.core.database import SessionLocal
from app.models import Document, DocStatus, DocumentQA
from app.services.document_parser import DocumentParser, DocumentQAExtractor
from app.services.auto_classify import auto_classify
import asyncio

async def test_parse_document(doc_id: int):
    db = SessionLocal()
    
    try:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        
        if not doc:
            print(f"❌ 文档 {doc_id} 不存在")
            return
        
        print(f"\n{'='*80}")
        print(f"  测试解析文档：{doc.original_filename}")
        print(f"{'='*80}")
        print(f"  文件路径：{doc.file_path}")
        print(f"  文件类型：{doc.file_type}")
        print(f"  当前状态：{doc.status}")
        
        # 检查文件是否存在
        import os
        if not os.path.exists(doc.file_path):
            print(f"❌ 文件不存在：{doc.file_path}")
            return
        
        # 解析文档
        print(f"\n  开始解析...")
        parse_result = DocumentParser.parse(doc.file_path)
        
        print(f"  解析结果：{parse_result['success']}")
        if not parse_result['success']:
            print(f"  错误：{parse_result['error']}")
            return
        
        print(f"  解析成功！")
        print(f"  文本块数量：{len(parse_result['text_blocks'])}")
        print(f"  元数据：{parse_result['metadata']}")
        
        # 提取 Q&A
        print(f"\n  提取 Q&A...")
        qa_pairs = DocumentQAExtractor.extract_qa_pairs(parse_result["text_blocks"])
        print(f"  提取到 {len(qa_pairs)} 条 Q&A")
        
        for i, qa in enumerate(qa_pairs[:3], 1):
            print(f"\n    Q&A #{i}:")
            print(f"      问题：{qa['question'][:100]}...")
            print(f"      答案：{qa['answer'][:100]}...")
        
        if len(qa_pairs) > 3:
            print(f"\n    ... 还有 {len(qa_pairs) - 3} 条")
        
        # 更新文档状态
        doc.status = DocStatus.parsed
        doc.parsed_content = parse_result["content"]
        doc.parsed_metadata = parse_result["metadata"]
        
        # 保存 Q&A
        print(f"\n  保存 Q&A 到数据库...")
        for qa in qa_pairs:
            classification = await auto_classify(qa["question"])
            
            doc_qa = DocumentQA(
                document_id=doc.id,
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
        print(f"  ✅ 保存成功！")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 解析失败：{e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    # 测试解析 PDF 文档
    doc_id = 2  # 轮胎价格监控与调整系统说明.pdf
    asyncio.run(test_parse_document(doc_id))
