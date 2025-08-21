import React from 'react';
import { useQuery } from 'react-query';
import { ChartBarIcon, DocumentIcon, ClockIcon, FolderIcon } from '@heroicons/react/24/outline';
import api from '../utils/api';

const StatCard = ({ title, value, icon: Icon, color = 'blue' }) => (
  <div className="bg-white rounded-lg shadow p-6">
    <div className="flex items-center">
      <div className={`p-3 rounded-full bg-${color}-100`}>
        <Icon className={`h-6 w-6 text-${color}-600`} />
      </div>
      <div className="ml-4">
        <p className="text-sm font-medium text-gray-600">{title}</p>
        <p className="text-2xl font-semibold text-gray-900">{value}</p>
      </div>
    </div>
  </div>
);

export default function Dashboard() {
  const { data: stats, isLoading } = useQuery('stats', api.getStats);
  const { data: recentDocs } = useQuery('recent-documents', () => 
    api.searchDocuments({ limit: 5 })
  );

  if (isLoading) {
    return (
      <div className="animate-pulse">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="bg-white rounded-lg shadow p-6 h-24" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-2">
          Welcome to your AI-powered document organization system
        </p>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Total Documents"
          value={stats?.total_documents || 0}
          icon={DocumentIcon}
          color="blue"
        />
        <StatCard
          title="Recent Uploads"
          value={stats?.recent_uploads || 0}
          icon={ClockIcon}
          color="green"
        />
        <StatCard
          title="Storage Used"
          value={`${stats?.storage_used_mb || 0} MB`}
          icon={FolderIcon}
          color="purple"
        />
        <StatCard
          title="Categories"
          value={Object.keys(stats?.documents_by_category || {}).length}
          icon={ChartBarIcon}
          color="orange"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Documents by Category */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Documents by Category</h3>
          <div className="space-y-3">
            {Object.entries(stats?.documents_by_category || {}).map(([category, count]) => (
              <div key={category} className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="w-3 h-3 rounded-full bg-blue-500 mr-3" />
                  <span className="text-sm text-gray-700 capitalize">{category.replace('_', ' ')}</span>
                </div>
                <span className="text-sm font-medium text-gray-900">{count}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Documents */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Documents</h3>
          <div className="space-y-3">
            {recentDocs?.results?.slice(0, 5).map((doc) => (
              <div key={doc.id} className="flex items-center justify-between py-2">
                <div className="flex items-center">
                  <DocumentIcon className="w-5 h-5 text-gray-400 mr-3" />
                  <div>
                    <p className="text-sm font-medium text-gray-900 truncate max-w-xs">
                      {doc.title}
                    </p>
                    <p className="text-xs text-gray-500 capitalize">{doc.category}</p>
                  </div>
                </div>
                <span className="text-xs text-gray-400">
                  {new Date(doc.created_date).toLocaleDateString()}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="mt-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg p-6 text-white">
        <h3 className="text-lg font-semibold mb-2">Quick Actions</h3>
        <p className="text-blue-100 mb-4">Get started with your document management</p>
        <div className="flex flex-wrap gap-3">
          <button 
            onClick={() => window.location.href = '/upload'}
            className="bg-white text-blue-600 px-4 py-2 rounded-md font-medium hover:bg-blue-50 transition-colors"
          >
            Upload Documents
          </button>
          <button 
            onClick={() => window.location.href = '/search'}
            className="bg-blue-400 text-white px-4 py-2 rounded-md font-medium hover:bg-blue-500 transition-colors"
          >
            Search Documents
          </button>
        </div>
      </div>
    </div>
  );
}
