# Document Processing & Chunking Guide

## Overview

The AI service now includes a complete document processing pipeline for handling uploaded/parsed text content. This guide covers the new components and how to use them.

## Components

### 1. **TextSplitter** (`text_splitter.py`)

Handles intelligent text chunking using LangChain's RecursiveCharacterTextSplitter.

**Key Features:**

- Preserves context with overlapping chunks
- Intelligent separator-based splitting (paragraph → sentence → word → character)
- Configurable chunk size and overlap
- Batch processing of multiple documents
- Detailed chunk metadata tracking

**Usage:**

```python
from text_splitter import DocumentChunker

# Initialize chunker
chunker = DocumentChunker(chunk_size=1000, chunk_overlap=200)

# Chunk single document
chunks = chunker.chunk_text(
    text="Your document text here...",
    metadata={"source": "pdf", "title": "Document Title"}
)

# Process multiple documents
documents = [
    {"content": "Text 1..."},
    {"content": "Text 2..."}
]
all_chunks = chunker.chunk_multiple(documents, text_field="content")
```

**Output Format:**

```python
{
    "content": "chunk text",
    "metadata": {source metadata},
    "chunk_index": 0,
    "chunk_size": 450
}
```

### 2. **DocumentProcessor** (`document_processor.py`)

Comprehensive preprocessing and chunking for already-uploaded/parsed documents.

**Key Features:**

- Text preprocessing (cleaning, normalization, noise removal)
- Unicode normalization and special character handling
- Intelligent chunking with minimum chunk size enforcement
- Batch processing with error handling
- Metadata extraction from documents
- Language detection
- Processing statistics and error reporting

**Usage:**

#### Single Document Processing

```python
from document_processor import DocumentProcessor

processor = DocumentProcessor(
    chunk_size=1000,
    chunk_overlap=200,
    min_chunk_size=50
)

result = processor.process_document(
    text="Your parsed document text...",
    metadata={"author": "John Doe"},
    file_name="document.pdf",
    file_type="pdf"
)

if result["success"]:
    print(f"Created {result['chunk_count']} chunks")
    for chunk in result["chunks"]:
        print(chunk["content"])
```

#### Batch Processing

```python
documents = [
    {
        "text": "Document 1 content...",
        "metadata": {"source": "file1.pdf"}
    },
    {
        "text": "Document 2 content...",
        "metadata": {"source": "file2.pdf"}
    }
]

result = processor.process_batch(documents)

print(f"Processed: {result['stats']['processed_successfully']} documents")
print(f"Total chunks: {result['stats']['total_chunks']}")
print(f"Failed: {result['stats']['failed_documents']}")
```

#### Extract Metadata

```python
metadata = processor.extract_metadata(
    text="Your document text...",
    file_path="/path/to/document.pdf"
)

# Returns:
# {
#     "file_name": "document.pdf",
#     "file_type": "pdf",
#     "text_length": 5000,
#     "word_count": 850,
#     "paragraph_count": 12,
#     "line_count": 45,
#     "estimated_reading_time_minutes": 5,
#     "likely_language": "english"
# }
```

## API Endpoints

### 1. Process Single Document

**POST** `/api/process-document`

**Request:**

```json
{
  "text": "Your document text content...",
  "metadata": {
    "author": "John Doe",
    "source": "email"
  },
  "file_name": "document.txt",
  "file_type": "txt"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Document processed successfully into 5 chunks",
  "chunks_count": 5,
  "chunks": [
    {
      "content": "chunk text...",
      "chunk_index": 0,
      "chunk_size": 950,
      "metadata": {
        "author": "John Doe",
        "source": "email",
        "file_name": "document.txt"
      }
    }
  ]
}
```

### 2. Process Batch of Documents

**POST** `/api/process-batch`

**Request:**

```json
{
  "documents": [
    {
      "text": "Document 1 text...",
      "metadata": { "source": "file1" },
      "file_name": "file1.txt",
      "file_type": "txt"
    },
    {
      "text": "Document 2 text...",
      "metadata": { "source": "file2" },
      "file_name": "file2.txt",
      "file_type": "txt"
    }
  ]
}
```

**Response:**

```json
{
  "success": true,
  "message": "Batch processing completed. 12 chunks created.",
  "total_chunks": 12,
  "stats": {
    "total_documents": 2,
    "processed_successfully": 2,
    "failed_documents": 0,
    "total_chunks": 12,
    "errors": []
  }
}
```

### 3. Get Processor Statistics

**GET** `/api/processor-stats`

**Response:**

```json
{
  "processor_config": {
    "chunk_size": 1000,
    "chunk_overlap": 200,
    "min_chunk_size": 50
  },
  "vector_store_stats": {
    "total_vectors": 156,
    "total_documents": 12,
    "dimension": 384,
    "index_type": "flat",
    "index_path": "vector_store"
  }
}
```

## Text Preprocessing

The document processor automatically performs the following preprocessing steps:

1. **Byte Decoding**: Handles UTF-8 byte decoding with fallback
2. **Unicode Normalization**: Converts smart quotes, dashes, etc. to standard characters
3. **Whitespace Cleaning**: Removes excessive spaces and normalizes indentation
4. **Newline Normalization**: Collapses multiple newlines to maximum of 2
5. **Special Character Cleanup**: Removes form feeds, excessive punctuation, etc.
6. **Encoding Validation**: Removes null characters and invalid Unicode

**Example:**

```python
# Input
raw_text = """
This is a "smart quoted" text with—em dashes

and   multiple    spaces.


Multiple newlines too.
"""

# After preprocessing
# "This is a "smart quoted" text with--em dashes\n\nand multiple spaces.\n\nMultiple newlines too."
```

## Chunking Strategy

The chunker uses a hierarchical approach with the following separators:

1. **Paragraph breaks** (`\n\n`) - Largest semantic unit
2. **Newlines** (`\n`) - Sentence-level breaks
3. **Sentence endings** (`. `) - Semantic continuity
4. **Spaces** (` `) - Word-level splitting
5. **Character splitting** as fallback

This ensures chunks remain semantically coherent while respecting size limits.

## Configuration

### DocumentProcessor Parameters

```python
processor = DocumentProcessor(
    chunk_size=1000,        # Size of each chunk in characters
    chunk_overlap=200,      # Overlap between consecutive chunks
    min_chunk_size=50       # Minimum characters required for a chunk
)
```

### DocumentChunker Parameters

```python
chunker = DocumentChunker(
    chunk_size=1000,        # Size of each chunk in characters
    chunk_overlap=200,      # Overlap between consecutive chunks
    separators=[            # Custom separators (optional)
        "\n\n",
        "\n",
        ". ",
        " ",
        ""
    ]
)
```

## Integration with Vector Store

When documents are processed, they are automatically:

1. **Chunked** into manageable pieces
2. **Embedded** using the EmbeddingService
3. **Stored** in the FAISS vector store with metadata
4. **Indexed** for semantic search

Example flow:

```
Raw Document Text
        ↓
  DocumentProcessor (preprocess + chunk)
        ↓
  Multiple Chunks
        ↓
  EmbeddingService (generate embeddings)
        ↓
  Multiple Embeddings
        ↓
  VectorStoreService (store with metadata)
```

## Error Handling

All processors include comprehensive error handling:

```python
result = processor.process_document(text)

if not result["success"]:
    print(f"Error: {result['error']}")
    print(f"Details: {result}")
```

Common errors:

- **Empty text**: "Text content cannot be empty"
- **Invalid input type**: "Expected str, got {type}"
- **Minimum size not met**: "No chunks met minimum size requirement"
- **Processing failures**: Tracked in batch results

## Performance Considerations

1. **Chunk Size**: Larger chunks preserve more context but reduce granularity

   - Small (500): More chunks, better for specific searches
   - Medium (1000): Balanced approach (default)
   - Large (2000): Fewer chunks, better for topic searches

2. **Chunk Overlap**: Prevents losing information at chunk boundaries

   - Typical range: 10-20% of chunk size
   - Default: 200 chars (20% of 1000)

3. **Batch Processing**: More efficient than processing individually
   - Use for multiple documents
   - Better error recovery

## Best Practices

1. **Metadata**: Always include relevant metadata

   - Helps in filtering search results
   - Provides context for downstream processing

2. **File Information**: Include file type and name

   - Enables filtering by source
   - Helps track document provenance

3. **Error Handling**: Check success flags

   - Not all documents may process successfully
   - Review error lists in batch operations

4. **Testing**: Start with small documents
   - Verify preprocessing works as expected
   - Adjust chunk size based on results

## Example: Complete Workflow

```python
from document_processor import DocumentProcessor
from embedding_service import EmbeddingService
from vector_store_service import VectorStoreService

# Initialize services
processor = DocumentProcessor(chunk_size=1000, chunk_overlap=200)
embedder = EmbeddingService()
vector_store = VectorStoreService(index_path="vector_store")

# Load vector store
vector_store.load()

# Process document
result = processor.process_document(
    text=open("document.txt").read(),
    metadata={"source": "uploaded_file", "date": "2024-01-15"},
    file_name="document.txt",
    file_type="txt"
)

# Generate embeddings and store
if result["success"]:
    chunks = result["chunks"]
    texts = [c["content"] for c in chunks]
    embeddings = embedder.generate_embeddings(texts)

    docs = [
        {
            "text": chunk["content"],
            "metadata": chunk["metadata"],
            "chunk_index": chunk["chunk_index"]
        }
        for chunk in chunks
    ]

    vector_store.add_documents(embeddings, docs)
    vector_store.save()

    print(f"Successfully stored {len(chunks)} chunks")
```

## Troubleshooting

### Empty results from processing

- Check if text contains only whitespace
- Verify minimum chunk size setting
- Ensure text is properly decoded

### Chunks too small/large

- Adjust `chunk_size` parameter
- Review preprocessing logic for edge cases

### Memory issues with large documents

- Use batch processing with smaller batches
- Increase chunk size to reduce number of chunks

### Embedding failures

- Check text encoding (should be UTF-8)
- Verify embedding service is running
- Check for extremely long chunks
