import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { pdfAPI } from '../services/api';

function Upload() {
  const [uploading, setUploading] = useState(false);
  const [uploadedFile, setUploadedFile] = useState(null);
  const navigate = useNavigate();

  const onDrop = useCallback(async (acceptedFiles) => {
    const file = acceptedFiles[0];

    if (!file) return;

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      toast.error('Please upload a PDF file');
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      toast.error('File size must be less than 10MB');
      return;
    }

    setUploadedFile(file);
    setUploading(true);

    try {
      const response = await pdfAPI.upload(file);
      toast.success('PDF uploaded successfully! Processing started.');
      setUploadedFile(null);
      navigate('/dashboard');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to upload PDF');
    } finally {
      setUploading(false);
    }
  }, [navigate]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
    },
    maxFiles: 1,
    disabled: uploading,
  });

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Upload PDF</h1>
        <p className="mt-1 text-sm text-gray-600">
          Upload a PDF document to generate an AI-powered summary.
        </p>
      </div>

      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors ${
          isDragActive
            ? 'border-indigo-500 bg-indigo-50'
            : 'border-gray-300 hover:border-indigo-400'
        } ${uploading ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        <input {...getInputProps()} />

        {uploading ? (
          <div className="flex flex-col items-center">
            <svg
              className="animate-spin h-12 w-12 text-indigo-600 mb-4"
              xmlns="http://www.w3.org/2000/svg"
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
            <p className="text-lg font-medium text-gray-900">
              Uploading {uploadedFile?.name}...
            </p>
            <p className="text-sm text-gray-500 mt-1">
              Please wait while we process your file
            </p>
          </div>
        ) : (
          <div className="flex flex-col items-center">
            <svg
              className="h-12 w-12 text-gray-400 mb-4"
              stroke="currentColor"
              fill="none"
              viewBox="0 0 48 48"
              aria-hidden="true"
            >
              <path
                d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            {isDragActive ? (
              <p className="text-lg font-medium text-indigo-600">
                Drop the PDF here...
              </p>
            ) : (
              <>
                <p className="text-lg font-medium text-gray-900">
                  Drag and drop your PDF here
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  or click to browse files
                </p>
              </>
            )}
            <p className="text-xs text-gray-400 mt-4">
              Maximum file size: 10MB
            </p>
          </div>
        )}
      </div>

      <div className="mt-8 bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">How it works</h2>
        <ol className="list-decimal list-inside space-y-2 text-gray-600">
          <li>Upload your PDF document (up to 10MB)</li>
          <li>Our AI extracts and analyzes the text content</li>
          <li>A comprehensive summary is generated using GPT-4</li>
          <li>Receive the summary via email and view it in your dashboard</li>
        </ol>
      </div>
    </div>
  );
}

export default Upload;
