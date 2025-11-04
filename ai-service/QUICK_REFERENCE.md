# Document Chunking & Preprocessing - Quick Reference

## 🚀 Quick Start

### Installation

All dependencies already in `requirements.txt`. No additional packages needed!

### Using in Code

```python
from document_processor import DocumentProcessor

processor = DocumentProcessor()
result = processor.process_document("Your text here...")

if result['success']:
    print(f"✅ Created {result['chunk_count']} chunks")
```

### Using the API

```bash
# Process single document
curl -X POST http://localhost:5000/api/process-document \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your document text...",
    "metadata": {"source": "email"},
    "file_name": "doc.txt",
    "file_type": "txt"
  }'

# Get processor stats
curl http://localhost:5000/api/processor-stats
```

## 📚 Key Components

| Component             | File                    | Purpose                    |
| --------------------- | ----------------------- | -------------------------- |
| **DocumentChunker**   | `text_splitter.py`      | Intelligent text splitting |
| **DocumentProcessor** | `document_processor.py` | Preprocessing & chunking   |
| **Updated API**       | `app.py`                | REST endpoints             |

## 🎯 Main Features

✅ **Intelligent Chunking** - Preserves meaning across chunks  
✅ **Preprocessing** - Cleans & normalizes text  
✅ **Batch Processing** - Handle multiple documents  
✅ **Metadata Tracking** - Preserve document metadata  
✅ **Error Handling** - Detailed error messages  
✅ **Vector Integration** - Automatic embedding & storage

## 💻 Common Use Cases

### Single Document

```python
result = processor.process_document(
    text=parsed_file_content,
    file_name="report.pdf",
    file_type="pdf"
)
```

### Multiple Documents

```python
result = processor.process_batch(documents)
print(f"Created {result['stats']['total_chunks']} chunks")
```

### Extract Metadata

```python
metadata = processor.extract_metadata(text, file_path)
print(f"Words: {metadata['word_count']}")
print(f"Reading time: {metadata['estimated_reading_time_minutes']} min")
```

## 🔧 Configuration

```python
# Customize processor
processor = DocumentProcessor(
    chunk_size=1500,        # Larger chunks
    chunk_overlap=250,      # More overlap
    min_chunk_size=100      # Higher minimum
)
```

## 📊 API Endpoints

| Endpoint                | Method | Purpose                     |
| ----------------------- | ------ | --------------------------- |
| `/api/process-document` | POST   | Process single document     |
| `/api/process-batch`    | POST   | Process multiple documents  |
| `/api/processor-stats`  | GET    | Get configuration & stats   |
| `/api/search`           | POST   | Search documents (existing) |

## 🎓 Learning Resources

| Resource   | Location                       | Content                |
| ---------- | ------------------------------ | ---------------------- |
| User Guide | `DOCUMENT_PROCESSING_GUIDE.md` | Complete documentation |
| Examples   | `example_usage.py`             | 7 working examples     |
| Summary    | `IMPLEMENTATION_SUMMARY.md`    | Overview & features    |
| Changes    | `CHANGES.md`                   | What was modified      |

## ⚡ Performance Tips

1. **Large Documents**: Increase `chunk_size` (1000 → 1500)
2. **Many Documents**: Use `process_batch()` instead of individual calls
3. **Memory**: Adjust `chunk_size` based on available RAM
4. **Quality**: Lower `min_chunk_size` for short documents

## ❌ Common Errors & Solutions

| Error               | Cause                | Solution               |
| ------------------- | -------------------- | ---------------------- |
| "Empty text"        | Text only whitespace | Verify text content    |
| "Expected str"      | Wrong data type      | Ensure text is string  |
| "No chunks created" | Size too small       | Lower `min_chunk_size` |
| "Processing failed" | Check logs           | Review error messages  |

## 🧪 Testing

```bash
# Run examples
python example_usage.py

# Test single document
curl -X POST http://localhost:5000/api/process-document ...

# Check health
curl http://localhost:5000/api/processor-stats
```

## 📈 What Gets Stored

```
Input:  "Raw document text from PDF/DOCX/TXT"
        ↓
Output: {
  "content": "chunk of text",
  "chunk_index": 0,
  "chunk_size": 450,
  "metadata": {
    "file_name": "document.pdf",
    "file_type": "pdf",
    "source": "uploaded"
  }
}
        ↓
Stored: FAISS Vector Store with embeddings
```

## 🔍 Search After Processing

```python
# After processing, documents are automatically embedded
query_embedding = embedder.generate_query_embedding("search term")
results = vector_store.search(query_embedding, top_k=5)

# Results include chunk content + metadata
for doc, score in results:
    print(f"Match: {doc['text']}")
    print(f"From: {doc['metadata']['file_name']}")
    print(f"Score: {score}")
```

## 📋 Preprocessing Steps (Automatic)

1. UTF-8 decoding with error handling
2. Unicode normalization ("→" becomes -)
3. Whitespace cleanup (multiple spaces → single)
4. Newline normalization (3+ → 2)
5. Special character removal
6. Invalid character filtering

## 🎯 Chunking Hierarchy

```
Paragraph (\\n\\n)
    ↓
Sentence (\\n)
    ↓
Words (. or space)
    ↓
Characters (fallback)
```

## 💡 Pro Tips

- **Metadata is crucial** - Include source, author, date
- **Monitor stats** - Check `/api/processor-stats` regularly
- **Tune chunk size** - Larger for summaries, smaller for search
- **Use batch mode** - More efficient than individual processing
- **Check errors** - Batch responses include detailed error info

## 🚀 Production Checklist

- ✅ Dependencies installed
- ✅ API endpoints tested
- ✅ Chunk configuration optimized
- ✅ Error handling verified
- ✅ Vector store integration working
- ✅ Monitoring enabled via stats endpoint

## 📞 Documentation Map

```
START HERE
    ↓
QUICK_REFERENCE.md (this file)
    ↓
Run example_usage.py
    ↓
Read DOCUMENT_PROCESSING_GUIDE.md
    ↓
Test with API
    ↓
Fine-tune configuration
    ↓
Deploy to production
```

## 🎓 Default Configuration

- **Chunk Size**: 1000 characters
- **Overlap**: 200 characters (20%)
- **Minimum Size**: 50 characters
- **Split Strategy**: Hierarchical (paragraph→word→char)

## 📊 Response Template

### Success

```json
{
  "success": true,
  "chunks_count": 5,
  "chunks": [...]
}
```

### Failure

```json
{
  "success": false,
  "error": "Description of what went wrong"
}
```

## 🔗 Integration Points

```
Your Frontend
    ↓
POST /api/process-document (NEW)
    ↓
DocumentProcessor (NEW)
    ↓
TextSplitter (NEW)
    ↓
EmbeddingService (existing)
    ↓
VectorStore (existing)
    ↓
POST /api/search (existing)
```

---

**Need More Help?**

- See `DOCUMENT_PROCESSING_GUIDE.md` for detailed docs
- Check `example_usage.py` for working code
- Review `IMPLEMENTATION_SUMMARY.md` for technical details
