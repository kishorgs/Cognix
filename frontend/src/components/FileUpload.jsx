import React, { useState, useRef, useEffect } from 'react';
import * as pdfjs from 'pdfjs-dist';
import { Document as DocxDocument } from 'docx';
import mammoth from 'mammoth';
import pdfjsWorker from 'pdfjs-dist/build/pdf.worker.entry';
import apiService from '../services/api';

// Initialize PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = pdfjsWorker;

export default function FileUpload() {
  const [isDragging, setIsDragging] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [parsedContent, setParsedContent] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const fileInputRef = useRef(null);

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    
    setIsSearching(true);
    try {
      const response = await fetch('http://localhost:5000/api/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: searchQuery,
          top_k: 5
        })
      });

      if (response.ok) {
        const data = await response.json();
        setSearchResults(data.results);
      } else {
        console.error('Error searching documents:', await response.text());
      }
    } catch (error) {
      console.error('Error calling search API:', error);
    } finally {
      setIsSearching(false);
    }
  };

  // Load saved files from localStorage on component mount
  useEffect(() => {
    const savedFiles = localStorage.getItem('uploadedFiles');
    if (savedFiles) {
      setUploadedFiles(JSON.parse(savedFiles));
    }
  }, []);

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const parseDocContent = async (file) => {
    let content = '';
    
    try {
      console.log('Parsing file:', file.name, 'Type:', file.type);
      
      if (file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')) {
        const arrayBuffer = await file.arrayBuffer();
        const loadingTask = pdfjs.getDocument({ data: arrayBuffer });
        
        // Add progress callback
        loadingTask.onProgress = ({ loaded, total }) => {
          console.log(`Loading PDF: ${Math.round((loaded / total) * 100)}%`);
        };

        try {
          const pdf = await loadingTask.promise;
          const numPages = pdf.numPages;
        
          for (let i = 1; i <= numPages; i++) {
            const page = await pdf.getPage(i);
            const textContent = await page.getTextContent();
            content += textContent.items.map(item => item.str).join(' ') + '\n';
          }
        } catch (error) {
          console.error('Error parsing PDF content:', error);
          throw new Error('Failed to parse PDF content');
        }
      } 
      else if (file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document') {
        try {
          const arrayBuffer = await file.arrayBuffer();
          const result = await mammoth.extractRawText({ arrayBuffer });
          content = result.value;
        } catch (error) {
          console.error('Error parsing DOCX content:', error);
          throw new Error('Failed to parse DOCX content');
        }
      } 
      else if (file.type === 'text/plain') {
        try {
          content = await file.text();
        } catch (error) {
          console.error('Error parsing text content:', error);
          throw new Error('Failed to parse text content');
        }
      } else {
        throw new Error('Unsupported file type');
      }
      
      return content || 'No content found in document';
    } catch (error) {
      console.error('Error parsing document:', error);
      return `Error: ${error.message || 'Failed to parse document content'}`;
    }
  };

  const handleUpload = async (files) => {
    if (!files.length) return;
    setIsUploading(true);

    try {
      const newFiles = await Promise.all(
        Array.from(files).map(async (file) => {
          // Create a local URL for the file
          const fileUrl = URL.createObjectURL(file);
          
          // Get file size in MB
          const fileSizeInMB = (file.size / (1024 * 1024)).toFixed(2);

          // Parse document content
          const content = await parseDocContent(file);

          // Process with AI service
          try {
            const result = await apiService.processDocument(
              content,
              {
                filename: file.name,
                type: file.type,
                size: fileSizeInMB,
              }
            );
            console.log('Document processed successfully:', result);
          } catch (error) {
            console.error('Error calling AI service:', error);
            // Don't throw the error to allow other files to be processed
          }

          // Create file object with metadata
          const fileObject = {
            name: file.name,
            url: fileUrl,
            size: fileSizeInMB,
            type: file.type,
            content: content,
            lastModified: file.lastModified,
            uploadedAt: new Date().toISOString()
          };

          return fileObject;
        })
      );

      const updatedFiles = [...uploadedFiles, ...newFiles];
      setUploadedFiles(updatedFiles);
      
      // Save to localStorage
      localStorage.setItem('uploadedFiles', JSON.stringify(updatedFiles));

    } catch (error) {
      console.error('Error handling files:', error);
      alert('Failed to process files. Please try again.');
    } finally {
      setIsUploading(false);
      setIsDragging(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      handleUpload(files);
    }
  };

  const handleFileSelect = (e) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleUpload(files);
    }
  };

  const handleClickUpload = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="p-6 bg-white rounded-xl shadow-lg">
      <div
        onDragOver={handleDragOver}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClickUpload}
        className={`
          relative border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
          transition-all duration-200 ease-in-out
          ${isDragging ? 'border-indigo-500 bg-indigo-50' : 'border-gray-300 hover:border-indigo-400'}
        `}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileSelect}
          className="hidden"
          accept=".pdf,.doc,.docx,.txt"
          multiple
        />

        <div className="space-y-4">
          <div className="flex justify-center">
            <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
          </div>

          <div className="text-gray-600">
            <span className="font-medium">Click to upload</span> or drag and drop
            <p className="text-sm text-gray-500 mt-1">PDF, DOC, DOCX, or TXT files</p>
          </div>
        </div>

        {isUploading && (
          <div className="absolute inset-0 bg-white bg-opacity-80 flex items-center justify-center rounded-lg">
            <div className="flex items-center space-x-2">
              <svg className="animate-spin h-5 w-5 text-indigo-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span className="text-indigo-600 font-medium">Uploading...</span>
            </div>
          </div>
        )}
      </div>

      {uploadedFiles.length > 0 && (
        <div className="mt-6">
          <h3 className="text-lg font-medium text-gray-900 mb-3">Uploaded Files</h3>
          <div className="space-y-3">
            {uploadedFiles.map((file, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors duration-200"
              >
                <div className="flex items-center space-x-4">
                  <div className="flex-shrink-0">
                    {file.type.startsWith('image/') ? (
                      <img
                        src={file.url}
                        alt={file.name}
                        className="h-10 w-10 object-cover rounded"
                      />
                    ) : (
                      <svg className="w-10 h-10 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                      </svg>
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {file.name}
                    </p>
                    <p className="text-sm text-gray-500">
                      {file.size} MB • {new Date(file.uploadedAt).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'short',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setSelectedFile(file);
                      setParsedContent(file.content);
                    }}
                    className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                  >
                    View Content
                  </button>
                  <a
                    href={file.url}
                    download={file.name}
                    className="text-indigo-600 hover:text-indigo-700 text-sm font-medium"
                    onClick={(e) => e.stopPropagation()}
                  >
                    Download
                  </a>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      const updatedFiles = uploadedFiles.filter(f => f.url !== file.url);
                      setUploadedFiles(updatedFiles);
                      localStorage.setItem('uploadedFiles', JSON.stringify(updatedFiles));
                      URL.revokeObjectURL(file.url);
                      if (selectedFile?.url === file.url) {
                        setSelectedFile(null);
                        setParsedContent('');
                      }
                    }}
                    className="text-red-600 hover:text-red-700 text-sm font-medium"
                  >
                    Remove
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="mt-6 space-y-6">
        {/* Search Section */}
        <div className="bg-white rounded-xl shadow-lg p-4">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Search Documents</h3>
          <div className="flex space-x-4">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Enter your search query..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
            <button
              onClick={handleSearch}
              disabled={isSearching || !searchQuery.trim()}
              className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
            >
              {isSearching ? 'Searching...' : 'Search'}
            </button>
          </div>

          {/* Search Results */}
          {searchResults.length > 0 && (
            <div className="mt-4">
              <h4 className="text-sm font-medium text-gray-700 mb-2">Search Results:</h4>
              <div className="space-y-3">
                {searchResults.map((result, index) => (
                  <div key={index} className="p-3 bg-gray-50 rounded-lg">
                    <p className="text-sm text-gray-900">{result.text.substring(0, 200)}...</p>
                    <div className="mt-2 flex items-center justify-between">
                      <span className="text-xs text-gray-500">
                        Similarity: {(1 - result.similarity).toFixed(4)}
                      </span>
                      <span className="text-xs text-gray-500">
                        File: {result.metadata.filename}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Document Content Viewer */}
        {selectedFile && (
          <div className="bg-white rounded-xl shadow-lg p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">
                Document Content: {selectedFile.name}
              </h3>
              <button
                onClick={() => {
                  setSelectedFile(null);
                  setParsedContent('');
                }}
                className="text-gray-500 hover:text-gray-700"
              >
                Close
              </button>
            </div>
            <div className="max-h-96 overflow-y-auto">
              <pre className="whitespace-pre-wrap text-sm text-gray-600 font-mono bg-gray-50 p-4 rounded">
                {parsedContent || 'No content available'}
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}