import { useTranslation } from 'react-i18next';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { Input } from '../components/ui/Input';
import { Button } from '../components/ui/Button';

const profileSchema = z.object({
  full_name: z.string().min(1, 'Required'),
  birth_date: z.string().min(1, 'Required'),
  biological_sex: z.enum(['male', 'female', 'other']),
  height_cm: z.number().min(50).max(250),
  default_unit_system: z.enum(['metric', 'imperial']),
  consent_accepted: z.boolean().refine((val) => val, 'Required'),
});

type ProfileForm = z.infer<typeof profileSchema>;

export const ProfilePage: React.FC = () => {
  const { t } = useTranslation();
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ProfileForm>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      full_name: '',
      birth_date: '',
      biological_sex: 'male',
      height_cm: 170,
      default_unit_system: 'metric',
      consent_accepted: false,
    },
  });

  const onSubmit = async (data: ProfileForm) => {
    console.log('Profile data', data);
    // TODO: call api to save profile
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">{t('settings.title')}</h1>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 max-w-lg">
        <Input
          label={t('settings.fullName')}
          name="full_name"
          {...register('full_name')}
          error={errors.full_name?.message}
        />
        <Input
          label={t('settings.birthDate')}
          name="birth_date"
          type="date"
          {...register('birth_date')}
          error={errors.birth_date?.message}
        />
        <div>
          <label className="block text-sm font-medium text-gray-700">
            {t('settings.biologicalSex')}
          </label>
          <select
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
            {...register('biological_sex')}
          >
            <option value="male">Male</option>
            <option value="female">Female</option>
            <option value="other">Other</option>
          </select>
        </div>
        <Input
          label={t('settings.height')}
          name="height_cm"
          type="number"
          step="0.1"
          {...register('height_cm', { valueAsNumber: true })}
          error={errors.height_cm?.message}
        />
        <div>
          <label className="block text-sm font-medium text-gray-700">
            {t('settings.unitSystem')}
          </label>
          <select
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
            {...register('default_unit_system')}
          >
            <option value="metric">Metric</option>
            <option value="imperial">Imperial</option>
          </select>
        </div>
        <div className="flex items-center">
          <input
            type="checkbox"
            {...register('consent_accepted')}
          />
          <label className="ml-2">{t('settings.consent')}</label>
        </div>
        <Button type="submit" variant="primary" className="w-full">
          {t('settings.save')}
        </Button>
      </form>
    </div>
  );
};
