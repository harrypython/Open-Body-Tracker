import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { apiClient } from '../lib/api';
import { Button } from '../components/ui/Button';

interface Measurement {
  id: string;
  metric_code_key: string;
  value_raw: number;
  unit_code_key: string;
  side: string | null;
}

interface Assessment {
  id: string;
  user_id: string;
  assessment_date: string;
  notes: string | null;
  protocol_used: string | null;
  created_at: string;
  measurements: Measurement[];
}

export const AssessmentList: React.FC = () => {
  const { t } = useTranslation();
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAssessments = async () => {
      try {
        setLoading(true);
        const response = await apiClient.get('/assessments/history');
        setAssessments(response.data);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch assessments:', err);
        setError('Failed to load assessments');
      } finally {
        setLoading(false);
      }
    };

    fetchAssessments();
  }, []);

  const handleDelete = async (assessmentId: string) => {
    if (!confirm('Are you sure you want to delete this assessment?')) {
      return;
    }

    try {
      await apiClient.delete(`/assessments/${assessmentId}`);
      setAssessments(prev => prev.filter(a => a.id !== assessmentId));
    } catch (err) {
      console.error('Failed to delete assessment:', err);
      alert('Failed to delete assessment');
    }
  };

  const getMeasurementValue = (measurements: Measurement[], metricKey: string): number | null => {
    const measurement = measurements.find(m => m.metric_code_key === metricKey);
    return measurement ? measurement.value_raw : null;
  };

  if (loading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
          {t('assessment.history')}
        </h2>
        <p className="text-gray-600 dark:text-gray-400">Loading...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
          {t('assessment.history')}
        </h2>
        <p className="text-red-600 dark:text-red-400">{error}</p>
      </div>
    );
  }

  if (assessments.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
          {t('assessment.history')}
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          No assessments yet. Create your first assessment to see your data here.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
        {t('assessment.history')}
      </h2>
      
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead className="bg-gray-50 dark:bg-gray-900">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Date
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Weight
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Body Fat %
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Protocol
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            {assessments.map((assessment) => {
              const weight = getMeasurementValue(assessment.measurements, 'weight_kg');
              // Note: Body fat would need to be calculated or stored as a derived metric
              
              return (
                <tr key={assessment.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                    {new Date(assessment.assessment_date).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                    {weight !== null ? `${weight.toFixed(1)} kg` : '--'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                    --
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                    {assessment.protocol_used || '--'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => window.location.href = `/assessment/${assessment.id}`}
                      className="mr-2"
                    >
                      View
                    </Button>
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => handleDelete(assessment.id)}
                      className="text-red-600 hover:text-red-800"
                    >
                      Delete
                    </Button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
