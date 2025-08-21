import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { Link } from 'react-router-dom';
import { 
  MagnifyingGlassIcon,
  DocumentIcon,
  FunnelIcon,
  SparklesIcon,
  AdjustmentsHorizontalIcon,
  EyeIcon,
  ArrowDownTrayIcon
} from '@heroicons/react/24/outline';
import api from '../utils/api';

const SearchResultCard = ({ result }) => {
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

  const handleDownload = async () => {
    try {
      const response = await api.downloadDocument(result.document.id);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', result.document.filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Download failed:', error);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-4 flex-1">
          <div className="flex-shrink-0">
            <DocumentIcon className="w-10 h-10 text-blue-500" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center space-x-3 mb-2">
              <Link
                to={`/documents/${result.document.id}`}
                className="text-lg font-medium text-blue-600 hover:text-blue-800 truncate"
              >
                {result.document.title || result.document.filename}
              </Link>
              <span className="text-sm text-gray-500">
                {(result.relevance_score * 100).toFixed(1)}% match
              </span>
            </div>
            
            <div className="flex items-center space-x-4 mb-3">
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getCategoryColor(result.document.category)}`}>
                {result.document.category.replace('_', ' ')}
              </span>
              <span className="text-sm text-gray-500">
                Confidence: {(result.document.confidence_score * 100).toFixed(1)}%
              </span>
            </div>
            
            {result.snippet && (
              <div className="mb-3">
                <p className="text-sm text-gray-600 leading-relaxed">
                  {result.snippet}
                </p>
              </div>
            )}
            
            <div className="flex items-center justify-between text-xs text-gray-500">
              <span>Uploaded: {new Date(result.document.created_date).toLocaleDateString()}</span>
              <div className="flex items-center space-x-2">
                <span>Matched fields: {result.matched_fields.join(', ')}</span>
              </div>
            </div>
            
            {result.document.tags && result.document.tags.length > 0 && (
              <div className="flex flex-wrap gap-1 mt-3">
                {result.document.tags.slice(0, 5).map((tag, index) => (
                  <span key={index} className="inline-flex items-center px-2 py-1 rounded-md text-xs bg-gray-100 text-gray-700">
                    {tag}
                  </span>
                ))}
                {result.document.tags.length > 5 && (
                  <span className="inline-flex items-center px-2 py-1 rounded-md text-xs bg-gray-100 text-gray-700">
                    +{result.document.tags.length - 5} more
                  </span>
                )}
              </div>
            )}
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <Link
            to={`/documents/${result.document.id}`}
            className="p-2 text-gray-400 hover:text-blue-600 rounded-full hover:bg-blue-50"
            title="View Details"
          >
            <EyeIcon className="w-5 h-5" />
          </Link>
          <button
            onClick={handleDownload}
            className="p-2 text-gray-400 hover:text-green-600 rounded-full hover:bg-green-50"
            title="Download"
          >
            <ArrowDownTrayIcon className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default function Search() {
  const [searchParams, setSearchParams] = useState({
    query: '',
    category: '',
    tags: [],
    use_semantic: true,
    similarity_threshold: 0.5,
    limit: 20
  });
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [searchHistory, setSearchHistory] = useState([]);

  const { data: searchResults, isLoading, error, refetch } = useQuery(
    ['search', searchParams],
    () => api.searchDocuments(searchParams),
    {
      enabled: false, // Don't auto-search
      retry: false
    }
  );

  const { data: categories } = useQuery('categories', api.getCategories);
  const { data: recentDocs } = useQuery('recent-documents', () => 
    api.getRecentDocuments(10)
  );

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchParams.query.trim() || searchParams.category) {
      setSearchHistory(prev => [searchParams, ...prev.slice(0, 4)]);
      refetch();
    }
  };

  const handleQuickSearch = (query) => {
    setSearchParams(prev => ({ ...prev, query }));
    refetch();
  };

  const handleParamChange = (key, value) => {
    setSearchParams(prev => ({ ...prev, [key]: value }));
  };

  const clearSearch = () => {
    setSearchParams({
      query: '',
      category: '',
      tags: [],
      use_semantic: true,
      similarity_threshold: 0.5,
      limit: 20
    });
  };

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Search Documents</h1>
        <p className="text-gray-600 mt-2">
          Find documents using keyword search or AI-powered semantic search
        </p>
      </div>

      {/* Search Form */}
      <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
        <form onSubmit={handleSearch}>
          <div className="flex flex-col sm:flex-row space-y-3 sm:space-y-0 sm:space-x-4 mb-4">
            <div className="flex-1 relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search documents by keywords, content, or title..."
                value={searchParams.query}
                onChange={(e) => handleParamChange('query', e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div className="flex space-x-2">
              <button
                type="submit"
                disabled={isLoading}
                className="flex-1 sm:flex-none px-4 sm:px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm sm:text-base"
              >
                {isLoading ? 'Searching...' : 'Search'}
              </button>
              <button
                type="button"
                onClick={() => setShowAdvanced(!showAdvanced)}
                className="px-3 sm:px-4 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
              >
                <AdjustmentsHorizontalIcon className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Advanced Search Options */}
          {showAdvanced && (
            <div className="border-t pt-4 space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Category
                  </label>
                  <select
                    value={searchParams.category}
                    onChange={(e) => handleParamChange('category', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">All Categories</option>
                    {categories?.categories?.map(cat => (
                      <option key={cat.value} value={cat.value}>
                        {cat.label}
                      </option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Results Limit
                  </label>
                  <select
                    value={searchParams.limit}
                    onChange={(e) => handleParamChange('limit', parseInt(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value={10}>10 results</option>
                    <option value={20}>20 results</option>
                    <option value={50}>50 results</option>
                    <option value={100}>100 results</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Search Type
                  </label>
                  <div className="flex items-center space-x-4">
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={searchParams.use_semantic}
                        onChange={(e) => handleParamChange('use_semantic', e.target.checked)}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="ml-2 text-sm text-gray-700">Semantic Search</span>
                    </label>
                  </div>
                </div>
              </div>
              
              {searchParams.use_semantic && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Similarity Threshold: {searchParams.similarity_threshold}
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    value={searchParams.similarity_threshold}
                    onChange={(e) => handleParamChange('similarity_threshold', parseFloat(e.target.value))}
                    className="w-full"
                  />
                </div>
              )}
              
              <div className="flex space-x-3">
                <button
                  type="button"
                  onClick={clearSearch}
                  className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
                >
                  Clear Filters
                </button>
              </div>
            </div>
          )}
        </form>
      </div>

      {/* Search Results */}
      {searchResults && (
        <div className="mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">
              Search Results ({searchResults.total_count || 0})
            </h2>
            {searchResults.query_time_ms && (
              <span className="text-sm text-gray-500">
                Found in {searchResults.query_time_ms}ms
              </span>
            )}
          </div>
          
          {searchResults.results?.length > 0 ? (
            <div className="space-y-4">
              {searchResults.results.map((result, index) => (
                <SearchResultCard key={index} result={result} />
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <DocumentIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No results found</h3>
              <p className="mt-1 text-sm text-gray-500">
                Try adjusting your search terms or filters
              </p>
            </div>
          )}
        </div>
      )}

      {/* Quick Search Suggestions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Documents */}
        <div className="bg-white rounded-lg shadow-sm p-6">
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
                <button
                  onClick={() => handleQuickSearch(doc.title)}
                  className="text-xs text-blue-600 hover:text-blue-800"
                >
                  Search
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Search History */}
        {searchHistory.length > 0 && (
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Searches</h3>
            <div className="space-y-2">
              {searchHistory.map((search, index) => (
                <button
                  key={index}
                  onClick={() => setSearchParams(search)}
                  className="w-full text-left p-2 text-sm text-gray-600 hover:bg-gray-50 rounded"
                >
                  {search.query || 'Advanced search'}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Search Tips */}
      <div className="mt-8 bg-blue-50 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-3">Search Tips</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-blue-800">
          <div>
            <h4 className="font-medium mb-2">Keyword Search</h4>
            <ul className="space-y-1">
              <li>• Use specific terms for better results</li>
              <li>• Search in document titles and content</li>
              <li>• Use quotes for exact phrases</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium mb-2">Semantic Search</h4>
            <ul className="space-y-1">
              <li>• Find related concepts and synonyms</li>
              <li>• Works in both English and Amharic</li>
              <li>• Adjust similarity threshold as needed</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
