"""
Example usage of DocumentProcessor and TextSplitter
This file demonstrates how to use the document processing components
"""

from text_splitter import DocumentChunker
from document_processor import DocumentProcessor
import json


def example_1_basic_chunking():
    """Example 1: Basic text chunking"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Text Chunking")
    print("="*60)
    
    chunker = DocumentChunker(chunk_size=500, chunk_overlap=100)
    
    text = """
    Machine learning is a subset of artificial intelligence.
    It enables systems to learn and improve from experience without being explicitly programmed.
    
    There are three main types of machine learning:
    1. Supervised Learning
    2. Unsupervised Learning
    3. Reinforcement Learning
    
    Each type has its own applications and use cases.
    """
    
    chunks = chunker.chunk_text(
        text=text,
        metadata={"source": "tutorial", "topic": "ML"}
    )
    
    print(f"\nCreated {len(chunks)} chunks:")
    for chunk in chunks:
        print(f"\nChunk {chunk['chunk_index']} (size: {chunk['chunk_size']} chars):")
        print(f"Content: {chunk['content'][:100]}...")
        print(f"Metadata: {chunk['metadata']}")


def example_2_document_preprocessing():
    """Example 2: Document preprocessing and chunking"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Document Preprocessing")
    print("="*60)
    
    processor = DocumentProcessor(chunk_size=800, chunk_overlap=150)
    
    # Messy document with various formatting issues
    messy_text = """
    This   is   a   document   with   extra   spaces
    
    
    
    Multiple blank lines and "smart quotes"


    Also has em—dashes and other unicode characters
    """
    
    result = processor.process_document(
        text=messy_text,
        metadata={"author": "John Doe"},
        file_name="example.pdf",
        file_type="pdf"
    )
    
    print(f"\nProcessing Result:")
    print(f"Success: {result['success']}")
    print(f"Original length: {result['original_length']} chars")
    print(f"Cleaned length: {result['cleaned_length']} chars")
    print(f"Chunk count: {result['chunk_count']}")
    
    if result['success']:
        print(f"\nFirst chunk preview:")
        print(result['chunks'][0]['content'][:150])


def example_3_batch_processing():
    """Example 3: Batch processing multiple documents"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Batch Processing")
    print("="*60)
    
    processor = DocumentProcessor()
    
    documents = [
        {
            "text": "Python is a high-level programming language. " * 10,
            "metadata": {"language": "Python", "category": "Programming"}
        },
        {
            "text": "JavaScript runs in web browsers. " * 10,
            "metadata": {"language": "JavaScript", "category": "Web"}
        },
        {
            "text": "Java is used for enterprise applications. " * 10,
            "metadata": {"language": "Java", "category": "Enterprise"}
        }
    ]
    
    result = processor.process_batch(documents)
    
    print(f"\nBatch Processing Results:")
    print(f"Total documents: {result['stats']['total_documents']}")
    print(f"Successfully processed: {result['stats']['processed_successfully']}")
    print(f"Failed: {result['stats']['failed_documents']}")
    print(f"Total chunks created: {result['stats']['total_chunks']}")
    
    if result['stats']['errors']:
        print(f"Errors: {result['stats']['errors']}")


def example_4_metadata_extraction():
    """Example 4: Extract metadata from document"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Metadata Extraction")
    print("="*60)
    
    processor = DocumentProcessor()
    
    sample_text = """
    Artificial Intelligence and Machine Learning are revolutionizing technology.
    
    AI systems can now perform tasks that typically required human intelligence.
    These include visual perception, speech recognition, and natural language processing.
    
    The field continues to evolve rapidly with new breakthroughs happening frequently.
    """
    
    metadata = processor.extract_metadata(sample_text)
    
    print("\nExtracted Metadata:")
    for key, value in metadata.items():
        print(f"  {key}: {value}")


def example_5_custom_chunking():
    """Example 5: Custom chunking parameters"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Custom Chunking Parameters")
    print("="*60)
    
    text = "Word " * 300  # 1500 words
    
    # Large chunks
    large_chunker = DocumentChunker(chunk_size=2000, chunk_overlap=300)
    large_chunks = large_chunker.chunk_text(text)
    
    # Small chunks
    small_chunker = DocumentChunker(chunk_size=500, chunk_overlap=50)
    small_chunks = small_chunker.chunk_text(text)
    
    print(f"\nText size: {len(text)} characters")
    print(f"\nLarge chunks (2000 chars):")
    print(f"  Number of chunks: {len(large_chunks)}")
    print(f"  Avg chunk size: {sum(c['chunk_size'] for c in large_chunks) / len(large_chunks):.0f}")
    
    print(f"\nSmall chunks (500 chars):")
    print(f"  Number of chunks: {len(small_chunks)}")
    print(f"  Avg chunk size: {sum(c['chunk_size'] for c in small_chunks) / len(small_chunks):.0f}")


def example_6_error_handling():
    """Example 6: Error handling"""
    print("\n" + "="*60)
    print("EXAMPLE 6: Error Handling")
    print("="*60)
    
    processor = DocumentProcessor(min_chunk_size=100)
    
    # Test 1: Empty text
    print("\nTest 1: Empty text")
    try:
        result = processor.process_document("")
        print(f"Result: {result['success']}")
        print(f"Error: {result.get('error', 'None')}")
    except ValueError as e:
        print(f"Caught error: {e}")
    
    # Test 2: Invalid type
    print("\nTest 2: Invalid input type")
    try:
        result = processor.process_document(123)
    except TypeError as e:
        print(f"Caught error: {e}")
    
    # Test 3: Text too small for chunks
    print("\nTest 3: Text too small for chunks")
    result = processor.process_document("Small text.")
    print(f"Result: {result['success']}")
    print(f"Error: {result.get('error', 'None')}")


def example_7_real_world_scenario():
    """Example 7: Real-world scenario - Processing research paper"""
    print("\n" + "="*60)
    print("EXAMPLE 7: Real-World Scenario")
    print("="*60)
    
    processor = DocumentProcessor(chunk_size=1200, chunk_overlap=200)
    
    # Simulate a research paper section
    paper_excerpt = """
    Abstract:
    This study investigates the effectiveness of transformer-based models in natural language processing.
    
    Introduction:
    Recent advancements in deep learning have revolutionized the field of natural language processing.
    Transformer models, introduced by Vaswani et al. (2017), have become the de facto standard for many NLP tasks.
    
    Methodology:
    We conducted experiments using BERT, GPT-2, and RoBERTa models on three benchmark datasets.
    The evaluation metrics included accuracy, F1-score, and inference time.
    
    Results:
    Our findings demonstrate that transformer models consistently outperform traditional approaches.
    BERT achieved 95.2% accuracy on the first benchmark, while GPT-2 showed superior performance in generation tasks.
    """
    
    result = processor.process_document(
        text=paper_excerpt,
        metadata={
            "source": "research_paper",
            "title": "Transformer Models in NLP",
            "year": 2024
        },
        file_name="paper.pdf",
        file_type="pdf"
    )
    
    print(f"\nPaper Processing Results:")
    print(f"Success: {result['success']}")
    print(f"Chunks created: {result['chunk_count']}")
    
    print(f"\nChunk Summary:")
    for i, chunk in enumerate(result['chunks']):
        print(f"\nChunk {i+1} ({chunk['chunk_size']} chars):")
        print(f"Preview: {chunk['content'][:100]}...")


if __name__ == "__main__":
    print("Document Processing Examples")
    print("============================\n")
    
    try:
        example_1_basic_chunking()
        example_2_document_preprocessing()
        example_3_batch_processing()
        example_4_metadata_extraction()
        example_5_custom_chunking()
        example_6_error_handling()
        example_7_real_world_scenario()
        
        print("\n" + "="*60)
        print("All examples completed successfully!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()