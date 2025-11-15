import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import toast from 'react-hot-toast';
import { Upload, File, X, CheckCircle } from 'lucide-react';

function DocumentUpload() {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);

  const onDrop = useCallback((acceptedFiles) => {
    const newFiles = acceptedFiles.map(file => ({
      file,
      title: file.name.replace('.pdf', ''),
      id: Math.random().toString(36).substr(2, 9)
    }));
    setFiles(prev => [...prev, ...newFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    multiple: true
  });

  const removeFile = (id) => {
    setFiles(files.filter(f => f.id !== id));
  };

  const updateTitle = (id, title) => {
    setFiles(files.map(f => f.id === id ? { ...f, title } : f));
  };

  const uploadFiles = async () => {
    if (files.length === 0) {
      toast.error('Please select files to upload');
      return;
    }

    setUploading(true);
    const results = [];

    for (const fileData of files) {
      try {
        const formData = new FormData();
        formData.append('file', fileData.file);
        formData.append('title', fileData.title);

        const response = await axios.post('/api/documents/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        results.push({
          ...fileData,
          success: true,
          document: response.data.document
        });

        toast.success(`${fileData.title} uploaded successfully!`);
      } catch (error) {
        console.error('Upload error:', error);
        results.push({
          ...fileData,
          success: false,
          error: error.response?.data?.detail || 'Upload failed'
        });
        toast.error(`Failed to upload ${fileData.title}`);
      }
    }

    setUploadedFiles(results);
    setFiles([]);
    setUploading(false);
  };

  return (
    <div className="space-y-6">
      <div className="card">
        <div className="card-header">
          <h1 className="card-title">Upload Documents</h1>
          <p className="card-description">
            Upload your study materials to get started with AI-powered learning
          </p>
        </div>
      </div>

      {/* Upload Area */}
      <div className="card">
        <div className="card-content">
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
              isDragActive
                ? 'border-accent-400 bg-accent-50'
                : 'border-primary-300 hover:border-accent-400 hover:bg-accent-50'
            }`}
          >
            <input {...getInputProps()} />
            <Upload className="mx-auto h-12 w-12 text-primary-400 mb-4" />
            {isDragActive ? (
              <p className="text-lg text-accent-600">Drop the files here...</p>
            ) : (
              <div>
                <p className="text-lg text-primary-600 mb-2">
                  Drag & drop PDF files here, or click to select
                </p>
                <p className="text-sm text-primary-500">
                  Maximum file size: 10MB per file
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* File List */}
      {files.length > 0 && (
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Files to Upload</h2>
          </div>
          <div className="card-content">
            <div className="space-y-4">
              {files.map((fileData) => (
                <div key={fileData.id} className="flex items-center space-x-4 p-4 border border-primary-200 rounded-lg">
                  <File className="h-8 w-8 text-danger-500" />
                  <div className="flex-1">
                    <input
                      type="text"
                      value={fileData.title}
                      onChange={(e) => updateTitle(fileData.id, e.target.value)}
                      className="input"
                      placeholder="Document title"
                    />
                    <p className="text-sm text-primary-500 mt-1">
                      {fileData.file.name} ({(fileData.file.size / 1024 / 1024).toFixed(2)} MB)
                    </p>
                  </div>
                  <button
                    onClick={() => removeFile(fileData.id)}
                    className="p-2 text-primary-400 hover:text-danger-500 transition-colors"
                  >
                    <X className="h-5 w-5" />
                  </button>
                </div>
              ))}
            </div>
            
            <div className="mt-6 flex justify-end">
              <button
                onClick={uploadFiles}
                disabled={uploading}
                className="btn-primary"
              >
                {uploading ? (
                  <div className="flex items-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Uploading...
                  </div>
                ) : (
                  `Upload ${files.length} file${files.length > 1 ? 's' : ''}`
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Upload Results */}
      {uploadedFiles.length > 0 && (
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Upload Results</h2>
          </div>
          <div className="card-content">
            <div className="space-y-3">
              {uploadedFiles.map((result) => (
                <div key={result.id} className="flex items-center space-x-3 p-3 rounded-lg bg-primary-50">
                  {result.success ? (
                    <CheckCircle className="h-5 w-5 text-success-500" />
                  ) : (
                    <X className="h-5 w-5 text-danger-500" />
                  )}
                  <div className="flex-1">
                    <p className="font-medium text-primary-900">{result.title}</p>
                    {result.success ? (
                      <p className="text-sm text-success-600">
                        Uploaded successfully • {result.document.chunk_count} chunks processed
                      </p>
                    ) : (
                      <p className="text-sm text-danger-600">{result.error}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default DocumentUpload;
