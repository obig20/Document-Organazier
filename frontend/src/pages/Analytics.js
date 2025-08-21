import React from 'react';
import { useQuery } from 'react-query';
import { 
  ChartBarIcon,
  CheckCircleIcon,
  XCircleIcon,
  TrendingUpIcon,
  DocumentIcon,
  ClockIcon
} from '@heroicons/react/24/outline';
import api from '../utils/api';

const MetricCard = ({ title, value, icon: Icon, color = 'blue', subtitle = '' }) => (
  <div className="bg-white rounded-lg shadow-sm p-6">
    <div className="flex items-center">
      <div className={`p-3 rounded-full bg-${color}-100`}>
        <Icon className={`h-6 w-6 text-${color}-600`} />
      </div>
      <div className="ml-4">
        <p className="text-sm font-medium text-gray-600">{title}</p>
        <p className="text-2xl font-semibold text-gray-900">{value}</p>
        {subtitle && <p className="text-xs text-gray-500">{subtitle}</p>}
      </div>
    </div>
  </div>
);

const ProgressBar = ({ percentage, label, color = 'blue' }) => (
  <div className="mb-4">
    <div className="flex justify-between text-sm mb-1">
      <span className="text-gray-700">{label}</span>
      <span className="text-gray-900 font-medium">{percentage}%</span>
    </div>
    <div className="w-full bg-gray-200 rounded-full h-2">
      <div
        className={`bg-${color}-600 h-2 rounded-full transition-all duration-300`}
        style={{ width: `${percentage}%` }}
      />
    </div>
  </div>
);

export default function Analytics() {
  const { data: analytics, isLoading, error } = useQuery('analytics', api.getAnalytics);
  const { data: stats } = useQuery('stats', api.getStats);

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
  console.log("analytics:");

  if (error) {
    return (
      <div className="text-center py-12">
        <XCircleIcon className="mx-auto h-12 w-12 text-red-500" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">Error loading analytics</h3>
        <p className="mt-1 text-sm text-gray-500">{error.message}</p>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Analytics & Performance</h1>
        <p className="text-gray-600 mt-2">
          Monitor system performance, accuracy, and learning potential
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <MetricCard
          title="Overall Accuracy"
          value={`${(analytics?.overall_accuracy * 100 || 0).toFixed(1)}%`}
          icon={CheckCircleIcon}
          color="green"
          subtitle="Based on user feedback"
        />
        <MetricCard
          title="Total Feedback"
          value={analytics?.total_feedback || 0}
          icon={ChartBarIcon}
          color="blue"
          subtitle="User submissions"
        />
        <MetricCard
          title="Learning Potential"
          value={`${(analytics?.learning_potential * 100 || 0).toFixed(1)}%`}
          icon={XCircleIcon}
          color="purple"
          subtitle="Improvement opportunity"
        />
        <MetricCard
          title="Total Documents"
          value={stats?.total_documents || 0}
          icon={DocumentIcon}
          color="orange"
          subtitle="Processed documents"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Category Performance */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Category Performance</h3>
          <div className="space-y-4">
            {analytics?.category_accuracy ? (
              Object.entries(analytics.category_accuracy).map(([category, accuracy]) => (
                <ProgressBar
                  key={category}
                  percentage={(accuracy * 100).toFixed(1)}
                  label={category.replace('_', ' ').toUpperCase()}
                  color={accuracy > 0.8 ? 'green' : accuracy > 0.6 ? 'yellow' : 'red'}
                />
              ))
            ) : (
              <p className="text-gray-500 text-center py-8">No category data available</p>
            )}
          </div>
        </div>

        {/* Recent Performance Trends */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Performance</h3>
          <div className="space-y-4">
            {analytics?.recent_performance ? (
              analytics.recent_performance.map((performance, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {new Date(performance.date).toLocaleDateString()}
                    </p>
                    <p className="text-xs text-gray-500">
                      {performance.documents_processed} documents processed
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-gray-900">
                      {(performance.accuracy * 100).toFixed(1)}%
                    </p>
                    <p className="text-xs text-gray-500">accuracy</p>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-gray-500 text-center py-8">No recent performance data</p>
            )}
          </div>
        </div>
      </div>

      {/* Feedback Analysis */}
      {analytics?.feedback_analysis && (
        <div className="mt-6 bg-white rounded-lg shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Feedback Analysis</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {analytics.feedback_analysis.correct_classifications || 0}
              </div>
              <p className="text-sm text-gray-600">Correct Classifications</p>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">
                {analytics.feedback_analysis.incorrect_classifications || 0}
              </div>
              <p className="text-sm text-gray-600">Incorrect Classifications</p>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {analytics.feedback_analysis.feedback_rate || 0}%
              </div>
              <p className="text-sm text-gray-600">Feedback Rate</p>
            </div>
          </div>
        </div>
      )}

      {/* System Health */}
      <div className="mt-6 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg p-6 text-white">
        <h3 className="text-lg font-semibold mb-2">System Health</h3>
        <p className="text-blue-100 mb-4">Current system status and recommendations</p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <h4 className="font-medium mb-2">Status</h4>
            <div className="flex items-center">
              <CheckCircleIcon className="w-5 h-5 text-green-400 mr-2" />
              <span>System operational</span>
            </div>
          </div>
          <div>
            <h4 className="font-medium mb-2">Recommendations</h4>
            <ul className="text-sm text-blue-100 space-y-1">
              {analytics?.learning_potential > 0.3 && (
                <li>• Consider retraining the model with new feedback</li>
              )}
              {analytics?.total_feedback < 10 && (
                <li>• Encourage more user feedback for better accuracy</li>
              )}
              <li>• Monitor category performance regularly</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
