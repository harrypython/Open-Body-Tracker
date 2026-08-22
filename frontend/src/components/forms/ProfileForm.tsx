import React, { useEffect, useState } from 'react';
import { useForm, SubmitHandler } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { useTranslation } from 'react-i18next';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';

// Validation schema matching Fase 6 requirements
const ProfileSchema = z.object({
  full_name: z.string().min(1, 'Required'),
  birth_date: z.string().refine((date) => {
    const today = new Date();
    const dob = new Date(date);
    const age = today.getFullYear() - dob.getFullYear() - ((today.getMonth() < dob.getMonth()) || (today.getMonth() === dob.getMonth() && today.getDate() < dob.getDate()) ? 1 : 0);
    return age >= 10;
  }, { message: 'Age must be greater than 10 years' }),
  biological_sex: z.enum(['male', 'female', 'other']),
  height_cm: z.number().min(50, 'Height must be > 50cm').max(250, 'Height must be < 250cm'),
  default_unit_system: z.enum(['metric', 'imperial']),
  consent_accepted: z.boolean().refine(val => val === true, { message: 'You must accept the terms' })
});

type ProfileForm = z.infer<typeof ProfileSchema>;

export const ProfileForm: React.FC = () => {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { register, handleSubmit, setValue, formState: { errors } } = useForm<ProfileForm>({
    resolver: zodResolver(ProfileSchema),
    defaultValues: {
      full_name: '',
      birth_date: '',
      biological_sex: 'male',
      height_cm: 170,
      default_unit_system: 'metric',
      consent_accepted: false as const
    }
  });

  // Load existing profile
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const res = await fetch('/api/v1/user/profile');
        if (!res.ok) return;
        const data = await res.json();
        if (data) {
          setValue('full_name', data.full_name ?? '');
          setValue('birth_date', data.birth_date ?? '');
          setValue('biological_sex', data.biological_sex ?? 'male');
          setValue('height_cm', data.height_cm ?? 170);
          setValue('default_unit_system', data.default_unit_system ?? 'metric');
          setValue('consent_accepted', data.consent_accepted ?? false);
        }
      } catch (err) {
        console.error(err);
      }
    };
    fetchProfile();
  }, [setValue]);

  const onSubmit: SubmitHandler<ProfileForm> = async (data) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('/api/v1/user/profile', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      if (!res.ok) {
        const errResp = await res.json();
        throw new Error(errResp.detail || 'Error saving profile');
      }
    } catch (err: any) {
      setError(err.message || 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className="space-y-4 max-w-lg" onSubmit={handleSubmit(onSubmit)}>
      {error && <div className="text-red-600">{error}</div>}

      <Input
        label={t('profile.fullName')}
        id="full_name"
        type="text"
        {...register('full_name')}
        error={errors.full_name?.message}
      />

      <Input
        label={t('profile.birthDate')}
        id="birth_date"
        type="date"
        {...register('birth_date')}
        error={errors.birth_date?.message}
      />

      <div className="flex flex-col">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1" htmlFor="biological_sex">
          {t('profile.biologicalSex')}
        </label>
        <select
          id="biological_sex"
          {...register('biological_sex')}
          className="flex h-10 w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600"
        >
          <option value="male">{t('profile.male') || 'Male'}</option>
          <option value="female">{t('profile.female') || 'Female'}</option>
          <option value="other">{t('profile.other') || 'Other'}</option>
        </select>
      </div>

      <Input
        label={t('profile.height')}
        id="height_cm"
        type="number"
        step="0.1"
        {...register('height_cm', { valueAsNumber: true })}
        error={errors.height_cm?.message}
      />

      <div className="flex flex-col">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1" htmlFor="default_unit_system">
          {t('profile.defaultUnitSystem')}
        </label>
        <select
          id="default_unit_system"
          {...register('default_unit_system')}
          className="flex h-10 w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600"
        >
          <option value="metric">{t('profile.metric')}</option>
          <option value="imperial">{t('profile.imperial')}</option>
        </select>
      </div>

      <div className="flex items-center space-x-2">
        <input
          id="consent_accepted"
          type="checkbox"
          {...register('consent_accepted')}
          className="h-4 w-4"
        />
        <label htmlFor="consent_accepted" className="text-sm">{t('profile.consentAccepted')}</label>
      </div>
      {errors.consent_accepted && <p className="text-sm text-red-500">{errors.consent_accepted.message}</p>}

      <Button type="submit" variant="primary" className="w-full" disabled={loading}>
        {loading ? t('common.loading') : t('common.save')}
      </Button>
    </form>
  );
};

export default ProfileForm;
