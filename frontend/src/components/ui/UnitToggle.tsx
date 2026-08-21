import { useUnits } from '../../contexts/UnitContext';
import { Button } from './Button';

export const UnitToggle: React.FC = () => {
  const { unitSystem, toggleUnitSystem } = useUnits();

  return (
    <div className="flex items-center gap-2">
      <span className="text-sm text-gray-600 dark:text-gray-400">
        {unitSystem === 'metric' ? 'Metric' : 'Imperial'}
      </span>
      <Button
        variant="outline"
        size="sm"
        onClick={toggleUnitSystem}
        className="min-w-[80px]"
      >
        {unitSystem === 'metric' ? 'kg / cm' : 'lbs / in'}
      </Button>
    </div>
  );
};
