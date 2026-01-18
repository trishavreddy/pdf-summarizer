import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import { pdfAPI, summaryAPI } from '../services/api';

function SummaryDetail() {
  const { id } = useParams();
  const [document, setDocument] = useState(null);
  const [loading, setLoading] = useState(true);
  const [resending, setResending] = useState(false);

  useEffect(() => {
    fetchDocument();
  }, [id]);

  const fetchDocument = async () => {
    try {
      const data = await pdfAPI.getDocument(id);
      setDocument(data);
    } catch (error) {
      toast.error('Failed to load document');
    } finally {
      setLoading(false);
    }
  };

  const handleResendEmail = async () => {
    if (!document?.summary?.id) return;

    setResending(true);
    try {
      await summaryAPI.resendEmail(document.summary.id);
      toast.success('Summary email sent successfully!');
    } catch (error) {
      toast.error('Failed to send email');
    } finally {
      setResending(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (!document) {
    return (
      <div className="text-center py-12">
        <h3 className="text-lg font-medium text-gray-900">Document not found</h3>
        <Link to="/dashboard" className="text-indigo-600 hover:text-indigo-500">
          Return to dashboard
        </Link>
      </div>
    );
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="mb-6">
        <Link
          to="/dashboard"
          className="text-sm text-indigo-600 hover:text-indigo-500 flex items-center"
        >
          <svg
            className="h-4 w-4 mr-1"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M15 19l-7-7 7-7"
            />
          </svg>
          Back to Dashboard
        </Link>
      </div>

      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-xl font-bold text-gray-900">
                {document.original_filename}
              </h1>
              <p className="text-sm text-gray-500 mt-1">
                Uploaded on {formatDate(document.created_at)}
              </p>
            </div>
            {document.summary && (
              <button
                onClick={handleResendEmail}
                disabled={resending}
                className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
              >
                {resending ? (
                  <>
                    <svg
                      className="animate-spin -ml-0.5 mr-2 h-4 w-4"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      ></circle>
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      ></path>
                    </svg>
                    Sending...
                  </>
                ) : (
                  <>
                    <svg
                      className="-ml-0.5 mr-2 h-4 w-4"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                      />
                    </svg>
                    Resend Email
                  </>
                )}
              </button>
            )}
          </div>
        </div>

        <div className="px-6 py-4">
          <div className="grid grid-cols-4 gap-4 mb-6">
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-500">Status</p>
              <p className="text-lg font-medium text-gray-900 capitalize">
                {document.status}
              </p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-500">Pages</p>
              <p className="text-lg font-medium text-gray-900">
                {document.page_count || '-'}
              </p>
            </div>
            {document.summary && (
              <>
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-500">Summary Words</p>
                  <p className="text-lg font-medium text-gray-900">
                    {document.summary.word_count || '-'}
                  </p>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-500">Processing Time</p>
                  <p className="text-lg font-medium text-gray-900">
                    {document.summary.processing_time
                      ? `${document.summary.processing_time.toFixed(1)}s`
                      : '-'}
                  </p>
                </div>
              </>
            )}
          </div>

          {document.summary ? (
            <div>
              <h2 className="text-lg font-medium text-gray-900 mb-3">Summary</h2>
              <div className="bg-gray-50 rounded-lg p-6">
                <p className="text-gray-700 whitespace-pre-wrap leading-relaxed">
                  {document.summary.content}
                </p>
              </div>
              {document.summary.email_sent && (
                <p className="text-sm text-gray-500 mt-4">
                  Email sent on{' '}
                  {document.summary.email_sent_at
                    ? formatDate(document.summary.email_sent_at)
                    : 'Unknown'}
                </p>
              )}
            </div>
          ) : document.status === 'processing' ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto mb-4"></div>
              <p className="text-gray-600">
                Your summary is being generated. Please check back shortly.
              </p>
            </div>
          ) : document.status === 'failed' ? (
            <div className="text-center py-8">
              <svg
                className="h-12 w-12 text-red-500 mx-auto mb-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
              <p className="text-gray-600">
                Failed to generate summary. Please try uploading the PDF again.
              </p>
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-gray-600">Summary pending...</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default SummaryDetail;
