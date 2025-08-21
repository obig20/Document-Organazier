import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { 
  ArrowLeftIcon,
  DocumentIcon,
  PencilIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  ArrowDownTrayIcon,
  ChatBubbleLeftRightIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import api from '../utils/api';

const FeedbackModal = ({ isOpen, onClose, documentId, onSubmit }) => {
  const [feedback, setFeedback] = useState({
    is_correct: true,
    corrected_category: '',
    comments: ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({ document_id: documentId, ...feedback });
    setFeedback({ is_correct: true, corrected_category: '', comments: '' });
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Provide Feedback</h3>
        <form onSubmit={handleSubmit}>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Was the classification correct?
              </label>
              <div className="flex space-x-4">
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="true"
                    checked={feedback.is_correct === true}
                    onChange={(e) => setFeedback(prev => ({ ...prev, is_correct: e.target.value === 'true' }))}
                    className="mr-2"
                  />
                  Yes
                </label>
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="false"
                    checked={feedback.is_correct === false}
                    onChange={(e) => setFeedback(prev => ({ ...prev, is_correct: e.target.value === 'true' }))}
                    className="mr-2"
                  />
                  No
                </label>
              </div>
            </div>

            {!feedback.is_correct && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Correct Category
                </label>
                <select
                  value={feedback.corrected_category}
                  onChange={(e) => setFeedback(prev => ({ ...prev, corrected_category: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  required
                >
                  <option value="">Select category</option>
                  <option value="demographics">Demographics</option>
                  <option value="housing">Housing</option>
                  <option value="id_registry">ID Registry</option>
                  <option value="land_plans">Land Plans</option>
                  <option value="other">Other</option>
                </select>
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Comments (optional)
              </label>
              <textarea
                value={feedback.comments}
                onChange={(e) => setFeedback(prev => ({ ...prev, comments: e.target.value }))}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                placeholder="Any additional comments..."
              />
            </div>
          </div>

          <div className="flex space-x-3 mt-6">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Submit Feedback
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default function DocumentDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [showFeedback, setShowFeedback] = useState(false);

  const { data: document, isLoading, error } = useQuery(
    ['document', id],
    () => api.getDocument(id)
  );

  const feedbackMutation = useMutation({
    mutationFn: api.submitFeedback,
    onSuccess: () => {
      toast.success('Feedback submitted successfully');
      queryClient.invalidateQueries('analytics');
    },
    onError: () => {
      toast.error('Failed to submit feedback');
    }
  });

  const handleDownload = async () => {
    try {
      const response = await api.downloadDocument(id);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', document.filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      toast.error('Download failed');
    }
  };

  const handleFeedback = (feedbackData) => {
    feedbackMutation.mutate(feedbackData);
  };

  const getStatusIcon = () => {
    switch (document?.processing_status) {
      case 'completed':
        return <CheckCircleIcon className="w-5 h-5 text-green-500" />;
      case 'error':
        return <XCircleIcon className="w-5 h-5 text-red-500" />;
      case 'processing':
        return <ClockIcon className="w-5 h-5 text-blue-500" />;
      default:
        return <ClockIcon className="w-5 h-5 text-gray-400" />;
    }
  };

  const getCategoryColor = (category) => {
    const colors = {
      demographics: 'bg-blue-100 text-blue-800',
      housing: 'bg-green-100 text-green-800',
      id_registry: 'bg-purple-100 text-purple-800',
      land_plans: 'bg-orange-100 text-orange-800',
      other: 'bg-gray-100 text-gray-800'
    };
    return colors[category] || colors.other;
  };

  if (isLoading) {
    return <div className="animate-pulse">Loading...</div>;
  }

  if (error) {
    return <div>Error loading document: {error.message}</div>;
  }

  if (!document) {
    return <div>Document not found</div>;
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-6">
        <button
          onClick={() => navigate(-1)}
          className="flex items-center text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeftIcon className="w-5 h-5 mr-2" />
          Back to Documents
        </button>
        
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              {document.title || document.filename}
            </h1>
            <p className="text-gray-600 mt-1">Document ID: {document.id}</p>
          </div>
          
          <div className="flex space-x-3">
            <button
              onClick={() => setShowFeedback(true)}
              className="flex items-center px-4 py-2 text-blue-600 border border-blue-600 rounded-md hover:bg-blue-50"
            >
              <ChatBubbleLeftRightIcon className="w-5 h-5 mr-2" />
              Feedback
            </button>
            <button
              onClick={handleDownload}
              className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              <ArrowDownTrayIcon className="w-5 h-5 mr-2" />
              Download
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Document Information</h2>
          <div className="space-y-4">
            <div className="flex items-center space-x-4">
              <span className="text-sm font-medium text-gray-700">Status:</span>
              <div className="flex items-center">
                {getStatusIcon()}
                <span className="ml-2 text-sm capitalize">{document.processing_status}</span>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <span className="text-sm font-medium text-gray-700">Category:</span>
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getCategoryColor(document.category)}`}>
                {document.category.replace('_', ' ')}
              </span>
            </div>
            
            <div className="flex items-center space-x-4">
              <span className="text-sm font-medium text-gray-700">Confidence:</span>
              <span className="text-sm text-gray-900">
                {(document.confidence_score * 100).toFixed(1)}%
              </span>
            </div>
            
            <div className="flex items-center space-x-4">
              <span className="text-sm font-medium text-gray-700">Language:</span>
              <span className="text-sm text-gray-900 capitalize">
                {document.language_detected || 'Unknown'}
              </span>
            </div>
            
            <div className="flex items-center space-x-4">
              <span className="text-sm font-medium text-gray-700">Uploaded:</span>
              <span className="text-sm text-gray-900">
                {new Date(document.created_date).toLocaleString()}
              </span>
            </div>
          </div>
        </div>

        {document.content && (
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Content Preview</h2>
            <div className="bg-gray-50 rounded-lg p-4 max-h-96 overflow-y-auto">
              <pre className="text-sm text-gray-700 whitespace-pre-wrap font-sans">
                {document.content.substring(0, 1000)}...
              </pre>
            </div>
          </div>
        )}
      </div>

      {document.tags && document.tags.length > 0 && (
        <div className="mt-6 bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Key Phrases</h2>
          <div className="flex flex-wrap gap-2">
            {document.tags.map((tag, index) => (
              <span key={index} className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800">
                {tag}
              </span>
            ))}
          </div>
        </div>
      )}

      <FeedbackModal
        isOpen={showFeedback}
        onClose={() => setShowFeedback(false)}
        documentId={id}
        onSubmit={handleFeedback}
      />
    </div>
  );
}
