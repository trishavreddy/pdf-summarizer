import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import { pdfAPI } from '../services/api';

function Dashboard() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      const data = await pdfAPI.getDocuments();
      setDocuments(data);
    } catch (error) {
      toast.error('Failed to load documents');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this document?')) return;

    try {
      await pdfAPI.deleteDocument(id);
      setDocuments(documents.filter((doc) => doc.id !== id));
      toast.success('Document deleted');
    } catch (error) {
      toast.error('Failed to delete document');
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getStatusBadge = (status) => {
    const styles = {
      pending: 'bg-yellow-100 text-yellow-800',
      processing: 'bg-blue-100 text-blue-800',
      completed: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800',
    };

    return (
      <span
        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
          styles[status] || 'bg-gray-100 text-gray-800'
        }`}
      >
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="mt-1 text-sm text-gray-600">
            View and manage your PDF summaries
          </p>
        </div>
        <Link
          to="/upload"
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700"
        >
          Upload PDF
        </Link>
      </div>

      {documents.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">
            No documents yet
          </h3>
          <p className="mt-1 text-sm text-gray-500">
            Get started by uploading your first PDF.
          </p>
          <div className="mt-6">
            <Link
              to="/upload"
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
            >
              Upload PDF
            </Link>
          </div>
        </div>
      ) : (
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <ul className="divide-y divide-gray-200">
            {documents.map((doc) => (
              <li key={doc.id}>
                <div className="px-4 py-4 sm:px-6 hover:bg-gray-50">
                  <div className="flex items-center justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center">
                        <svg
                          className="h-8 w-8 text-red-500 mr-3"
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path
                            fillRule="evenodd"
                            d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z"
                            clipRule="evenodd"
                          />
                        </svg>
                        <div>
                          <p className="text-sm font-medium text-indigo-600 truncate">
                            {doc.original_filename}
                          </p>
                          <p className="text-sm text-gray-500">
                            {formatFileSize(doc.file_size)} |{' '}
                            {doc.page_count
                              ? `${doc.page_count} pages`
                              : 'Processing...'}{' '}
                            | {formatDate(doc.created_at)}
                          </p>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-4">
                      {getStatusBadge(doc.status)}
                      {doc.has_summary && (
                        <Link
                          to={`/summary/${doc.id}`}
                          className="text-sm text-indigo-600 hover:text-indigo-900"
                        >
                          View Summary
                        </Link>
                      )}
                      <button
                        onClick={() => handleDelete(doc.id)}
                        className="text-sm text-red-600 hover:text-red-900"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default Dashboard;
