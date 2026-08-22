import { useTranslation } from 'react-i18next';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { TrendsModule, ComparisonView, MilestonesView, TimelinePhotos } from '../components/analytics';
import { AssessmentList } from '../components/AssessmentList';

export const DashboardPage: React.FC = () => {
  const { t } = useTranslation();

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">
        {t('dashboard.title')}
      </h1>
      
      {/* Assessment List */}
      <div className="mb-8">
        <AssessmentList />
      </div>
      
      {/* Last Assessment Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">{t('dashboard.lastAssessment')}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <p className="text-sm text-gray-600 dark:text-gray-400">
                No assessments yet. Create your first assessment to see your data here.
              </p>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Weight Trend</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-blue-600">-- kg</p>
            <p className="text-sm text-gray-500">Last 3 months</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Body Fat %</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-green-600">--%</p>
            <p className="text-sm text-gray-500">Latest measurement</p>
          </CardContent>
        </Card>
      </div>

      {/* Trends Module - Weight graph for last 3 months */}
      <div className="mb-8">
        <TrendsModule />
      </div>

      {/* Comparison View */}
      <div className="mb-8">
        <ComparisonView />
      </div>

      {/* Milestones */}
      <div className="mb-8">
        <MilestonesView />
      </div>

      {/* Photo Timeline */}
      <div className="mb-8">
        <TimelinePhotos />
      </div>
      
      {/* Quick Actions */}
      <div className="mt-8 flex gap-4">
        <Button variant="primary" size="lg" onClick={() => window.location.href = '/assessment/new'}>
          {t('assessment.new')}
        </Button>
        <Button variant="secondary" size="lg" onClick={() => window.location.href = '/import-csv'}>
          Import CSV
        </Button>
      </div>
    </div>
  );
};
