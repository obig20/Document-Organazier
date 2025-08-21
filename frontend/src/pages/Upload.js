import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { useMutation, useQueryClient } from 'react-query';
import { 
  CloudArrowUpIcon, 
  DocumentIcon, 
  CheckCircleIcon, 
  XCircleIcon,
  ExclamationTriangleIcon,
  EyeIcon,
  EyeSlashIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import api from '../utils/api';

const FileUploadCard = ({ file, onRemove }) => (
  <div className="flex items-center p-3 bg-gray-50 rounded-lg border">
    <DocumentIcon className="w-8 h-8 text-blue-500 mr-3" />
    <div className="flex-1 min-w-0">
      <p className="text-sm font-medium text-gray-900 truncate">{file.name}</p>
      <p className="text-xs text-gray-500">
        {(file.size / 1024 / 1024).toFixed(2)} MB
      </p>
    </div>
    <button
      onClick={() => onRemove(file)}
      className="ml-2 p-1 text-gray-400 hover:text-red-500"
    >
      <XCircleIcon className="w-5 h-5" />
    </button>
  </div>
);

const ProcessingStatus = ({ status, message, documentId }) => {
  const getStatusIcon = () => {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon className="w-5 h-5 text-green-500" />;
      case 'error':
        return <XCircleIcon className="w-5 h-5 text-red-500" />;
      case 'processing':
        return <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />;
      default:
        return <ExclamationTriangleIcon className="w-5 h-5 text-yellow-500" />;
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'completed':
        return 'text-green-700 bg-green-50 border-green-200';
      case 'error':
        return 'text-red-700 bg-red-50 border-red-200';
      case 'processing':
        return 'text-blue-700 bg-blue-50 border-blue-200';
      default:
        return 'text-yellow-700 bg-yellow-50 border-yellow-200';
    }
  };

  return (
    <div className={`flex items-center p-3 rounded-lg border ${getStatusColor()}`}>
      {getStatusIcon()}
      <div className="ml-3">
        <p className="text-sm font-medium capitalize">{status}</p>
        <p className="text-xs opacity-75">{message}</p>
      </div>
    </div>
  );
};

export default function Upload() {
  const [files, setFiles] = useState([]);
  const [uploadResults, setUploadResults] = useState([]);
  const [showResults, setShowResults] = useState(false);
  const queryClient = useQueryClient();

  const onDrop = useCallback((acceptedFiles) => {
    const newFiles = acceptedFiles.filter(file => {
      const isValid = file.size <= 20 * 1024 * 1024; // 20MB limit
      if (!isValid) {
        toast.error(`${file.name} is too large. Maximum size is 20MB.`);
      }
      return isValid;
    });
    
    setFiles(prev => [...prev, ...newFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
      'image/tiff': ['.tiff'],
      'image/bmp': ['.bmp']
    },
    multiple: true
  });

  const removeFile = (fileToRemove) => {
    setFiles(prev => prev.filter(file => file !== fileToRemove));
  };

  const uploadMutation = useMutation({
    mutationFn: api.uploadDocuments,
    onSuccess: (data) => {
      setUploadResults(data.data);
      setShowResults(true);
      toast.success('Files uploaded successfully!');
      queryClient.invalidateQueries(['stats', 'recent-documents']);
    },
    onError: (error) => {
      toast.error('Upload failed: ' + (error.response?.data?.detail || error.message));
    }
  });

  const handleUpload = () => {
    if (files.length === 0) {
      toast.error('Please select files to upload');
      return;
    }
    uploadMutation.mutate(files);
  };

  const clearAll = () => {
    setFiles([]);
    setUploadResults([]);
    setShowResults(false);
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Upload Documents</h1>
        <p className="text-gray-600 mt-2">
          Upload PDF, DOCX, TXT, Excel, PowerPoint, or image files for AI-powered processing
        </p>
      </div>

      {/* Upload Area */}
      <div className="bg-white rounded-lg shadow-sm border-2 border-dashed border-gray-300 p-8 mb-6">
        <div {...getRootProps()} className="text-center cursor-pointer">
          <input {...getInputProps()} />
          <CloudArrowUpIcon className="mx-auto h-12 w-12 text-gray-400" />
          <div className="mt-4">
            {isDragActive ? (
              <p className="text-lg font-medium text-blue-600">Drop the files here...</p>
            ) : (
              <>
                <p className="text-lg font-medium text-gray-900">
                  Drag and drop files here, or click to select
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  Supports PDF, DOCX, TXT, Excel, PowerPoint, and image files (max 20MB each)
                </p>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Selected Files */}
      {files.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">
              Selected Files ({files.length})
            </h3>
            <button
              onClick={clearAll}
              className="text-sm text-red-600 hover:text-red-800"
            >
              Clear All
            </button>
          </div>
          <div className="space-y-3">
            {files.map((file, index) => (
              <FileUploadCard key={index} file={file} onRemove={removeFile} />
            ))}
          </div>
          <div className="mt-6">
            <button
              onClick={handleUpload}
              disabled={uploadMutation.isLoading}
              className="w-full bg-blue-600 text-white py-3 px-4 rounded-md font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {uploadMutation.isLoading ? 'Uploading...' : 'Upload Documents'}
            </button>
          </div>
        </div>
      )}

      {/* Upload Results */}
      {showResults && uploadResults.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">Upload Results</h3>
            <button
              onClick={() => setShowResults(!showResults)}
              className="text-sm text-gray-600 hover:text-gray-800"
            >
              {showResults ? (
                <EyeSlashIcon className="w-5 h-5" />
              ) : (
                <EyeIcon className="w-5 h-5" />
              )}
            </button>
          </div>
          <div className="space-y-3">
            {uploadResults.map((result, index) => (
              <ProcessingStatus
                key={index}
                status={result.status}
                message={result.message}
                documentId={result.document_id}
              />
            ))}
          </div>
        </div>
      )}

      {/* Features */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
            <DocumentIcon className="w-6 h-6 text-blue-600" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">AI Classification</h3>
          <p className="text-gray-600 text-sm">
            Documents are automatically categorized using AI with confidence scores
          </p>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
            <CheckCircleIcon className="w-6 h-6 text-green-600" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Language Detection</h3>
          <p className="text-gray-600 text-sm">
            Supports both English and Amharic text with automatic language detection
          </p>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
            <ExclamationTriangleIcon className="w-6 h-6 text-purple-600" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Key Phrase Extraction</h3>
          <p className="text-gray-600 text-sm">
            Important keywords and phrases are automatically extracted for better search
          </p>
        </div>
      </div>
    </div>
  );
}
