import React, { useState, useEffect } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';
import { 
  FileText, 
  Upload, 
  Trash2, 
  Eye, 
  Calendar,
  Hash,
  Tag,
  AlertTriangle,
  Plus
} from 'lucide-react';

function DocumentsPage() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [deleteLoading, setDeleteLoading] = useState(null);
  const [showUpload, setShowUpload] = useState(false);

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/documents/');
      setDocuments(response.data.documents);
    } catch (error) {
      console.error('Error fetching documents:', error);
      toast.error('Failed to load documents');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (documentId, title) => {
    if (!window.confirm(`Are you sure you want to delete "${title}"? This action cannot be undone.`)) {
      return;
    }

    setDeleteLoading(documentId);
    try {
      await axios.delete(`/api/documents/${documentId}`);
      toast.success('Document deleted successfully');
      // Remove from local state
      setDocuments(documents.filter(doc => doc.id !== documentId));
    } catch (error) {
      console.error('Error deleting document:', error);
      toast.error('Failed to delete document');
    } finally {
      setDeleteLoading(null);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatTopics = (topics) => {
    if (!topics || topics.length === 0) return 'No topics';
    return topics.slice(0, 3).join(', ') + (topics.length > 3 ? '...' : '');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-900"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="card">
        <div className="card-header">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <FileText className="h-8 w-8 text-accent-600" />
              <div>
                <h1 className="card-title">My Documents</h1>
                <p className="card-description">
                  Manage your uploaded study materials
                </p>
              </div>
            </div>
            <button
              onClick={() => setShowUpload(!showUpload)}
              className="btn btn-primary flex items-center space-x-2"
            >
              <Plus className="h-4 w-4" />
              <span>Upload Document</span>
            </button>
          </div>
        </div>
      </div>

      {/* Upload Section */}
      {showUpload && (
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Upload New Document</h2>
            <p className="card-description">Add a new PDF to your study materials</p>
          </div>
          <div className="card-content">
            <DocumentUploadForm onSuccess={() => {
              setShowUpload(false);
              fetchDocuments();
            }} />
          </div>
        </div>
      )}

      {/* Documents List */}
      <div className="card">
        <div className="card-header">
          <div className="flex items-center justify-between">
            <h2 className="card-title">Uploaded Documents ({documents.length})</h2>
          </div>
        </div>
        <div className="card-content">
          {documents.length === 0 ? (
            <div className="text-center py-12">
              <FileText className="h-16 w-16 mx-auto text-primary-300 mb-4" />
              <h3 className="text-lg font-medium text-primary-900 mb-2">No documents uploaded</h3>
              <p className="text-primary-600 mb-4">
                Upload your first document to start learning with AI
              </p>
              <button
                onClick={() => setShowUpload(true)}
                className="btn btn-primary"
              >
                Upload Document
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              {documents.map((document) => (
                <div
                  key={document.id}
                  className="border border-primary-200 rounded-lg p-4 hover:border-accent-300 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <FileText className="h-5 w-5 text-accent-600" />
                        <h3 className="font-medium text-primary-900">{document.title}</h3>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-primary-600">
                        <div className="flex items-center space-x-2">
                          <Calendar className="h-4 w-4" />
                          <span>Uploaded {formatDate(document.created_at)}</span>
                        </div>
                        
                        <div className="flex items-center space-x-2">
                          <Hash className="h-4 w-4" />
                          <span>{document.chunk_count || 0} chunks</span>
                        </div>
                        
                        <div className="flex items-center space-x-2">
                          <Tag className="h-4 w-4" />
                          <span>{formatTopics(document.topics)}</span>
                        </div>
                      </div>

                      {document.filename && (
                        <div className="mt-2 text-xs text-primary-500">
                          Original file: {document.filename}
                        </div>
                      )}
                    </div>

                    <div className="flex items-center space-x-2 ml-4">
                      <button
                        onClick={() => handleDelete(document.id, document.title)}
                        disabled={deleteLoading === document.id}
                        className="p-2 text-error-600 hover:bg-error-50 rounded-lg transition-colors disabled:opacity-50"
                        title="Delete document"
                      >
                        {deleteLoading === document.id ? (
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-error-600"></div>
                        ) : (
                          <Trash2 className="h-4 w-4" />
                        )}
                      </button>
                    </div>
                  </div>

                  {/* Topics Display */}
                  {document.topics && document.topics.length > 0 && (
                    <div className="mt-3 flex flex-wrap gap-2">
                      {document.topics.map((topic, index) => (
                        <span
                          key={index}
                          className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-accent-100 text-accent-800"
                        >
                          {topic}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Warning Section */}
      <div className="card border-warning-200 bg-warning-50">
        <div className="card-content">
          <div className="flex items-start space-x-3">
            <AlertTriangle className="h-5 w-5 text-warning-600 mt-0.5" />
            <div>
              <h3 className="font-medium text-warning-900 mb-1">Important Note</h3>
              <p className="text-sm text-warning-800">
                Deleting a document will permanently remove it from your study materials, 
                including all generated quizzes and flashcards based on this content. 
                This action cannot be undone.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Simple upload form component
function DocumentUploadForm({ onSuccess }) {
  const [file, setFile] = useState(null);
  const [title, setTitle] = useState('');
  const [uploading, setUploading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file || !title.trim()) {
      toast.error('Please select a file and enter a title');
      return;
    }

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('title', title.trim());

      await axios.post('/api/documents/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      toast.success('Document uploaded successfully');
      setFile(null);
      setTitle('');
      onSuccess();
    } catch (error) {
      console.error('Error uploading document:', error);
      toast.error(error.response?.data?.detail || 'Failed to upload document');
    } finally {
      setUploading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-primary-700 mb-2">
          Document Title
        </label>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="input w-full"
          placeholder="Enter a descriptive title for your document"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-primary-700 mb-2">
          PDF File
        </label>
        <input
          type="file"
          accept=".pdf"
          onChange={(e) => setFile(e.target.files[0])}
          className="input w-full"
          required
        />
        {file && (
          <p className="text-sm text-primary-600 mt-1">
            Selected: {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
          </p>
        )}
      </div>

      <div className="flex items-center space-x-3">
        <button
          type="submit"
          disabled={uploading}
          className="btn btn-primary disabled:opacity-50"
        >
          {uploading ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              Uploading...
            </>
          ) : (
            <>
              <Upload className="h-4 w-4 mr-2" />
              Upload Document
            </>
          )}
        </button>
      </div>
    </form>
  );
}

export default DocumentsPage;
