import React, { useEffect, useState } from 'react';
import { useForm, SubmitHandler } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';

// Validation schema
const ProfileSchema = z.object({
  full_name: z.string().nonempty('Nome obrigatório'),
  birth_date: z.string().refine((date) => {
    const today = new Date();
    const dob = new Date(date);
    const age = today.getFullYear() - dob.getFullYear() - ((today.getMonth() < dob.getMonth()) || (today.getMonth() === dob.getMonth() && today.getDate() < dob.getDate()) ? 1 : 0);
    return age >= 10;
  }, { message: 'A idade deve ser maior que 10 anos' }),
  biological_sex: z.enum(['male', 'female', 'other']),
  height_cm: z.number().min(50, 'Altura mínima 50cm').max(250, 'Altura máxima 250cm'),
  default_unit_system: z.enum(['metric', 'imperial']),
  consent_accepted: z.literal(true, { errorMap: () => ({ message: 'Você deve aceitar as condições' }) })
});

type ProfileForm = z.infer<typeof ProfileSchema>;

const ProfileForm: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { register, handleSubmit, setValue, formState: { errors, isSubmitting } } = useForm<ProfileForm>({
    resolver: zodResolver(ProfileSchema),
    defaultValues: {
      full_name: '',
      birth_date: '',
      biological_sex: 'male',
      height_cm: 160,
      default_unit_system: 'metric',
      consent_accepted: false
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
          setValue('height_cm', data.height_cm ?? 160);
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
        throw new Error(errResp.detail || 'Erro ao salvar perfil');
      }
      // Optionally show success toast
    } catch (err: any) {
      setError(err.message || 'Erro desconhecido');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className="space-y-4" onSubmit={handleSubmit(onSubmit)}>
      {error && <div className="text-red-600">{error}</div>}

      <div className="flex flex-col">
        <label className="mb-1 font-medium" htmlFor="full_name">Nome Completo</label>
        <input
          id="full_name"
          type="text"
          {...register('full_name')}
          className="border p-2 rounded"
        />
        {errors.full_name && <p className="text-sm text-red-500">{errors.full_name.message}</p>}
      </div>

      <div className="flex flex-col">
        <label className="mb-1 font-medium" htmlFor="birth_date">Data de Nascimento</label>
        <input
          id="birth_date"
          type="date"
          {...register('birth_date')}
          className="border p-2 rounded"
        />
        {errors.birth_date && <p className="text-sm text-red-500">{errors.birth_date.message}</p>}
      </div>

      <div className="flex flex-col">
        <label className="mb-1 font-medium" htmlFor="biological_sex">Sexo Biológico</label>
        <select id="biological_sex" {...register('biological_sex')} className="border p-2 rounded">
          <option value="male">Masculino</option>
          <option value="female">Feminino</option>
          <option value="other">Outro</option>
        </select>
      </div>

      <div className="flex flex-col">
        <label className="mb-1 font-medium" htmlFor="height_cm">Altura (cm)</label>
        <input
          id="height_cm"
          type="number"
          step="0.1"
          {...register('height_cm', { valueAsNumber: true })}
          className="border p-2 rounded"
        />
        {errors.height_cm && <p className="text-sm text-red-500">{errors.height_cm.message}</p>}
      </div>

      <div className="flex flex-col">
        <label className="mb-1 font-medium" htmlFor="default_unit_system">Sistema de Unidade</label>
        <select id="default_unit_system" {...register('default_unit_system')} className="border p-2 rounded">
          <option value="metric">Métrico (kg, cm)</option>
          <option value="imperial">Imperial (lb, in)</option>
        </select>
      </div>

      <div className="flex items-center space-x-2">
        <input
          id="consent_accepted"
          type="checkbox"
          {...register('consent_accepted')}
          className="h-4 w-4"
        />
        <label htmlFor="consent_accepted" className="select-none">Concordo com os Termos de Uso</label>
      </div>
      {errors.consent_accepted && <p className="text-sm text-red-500">{errors.consent_accepted.message}</p>}

      <button type="submit" disabled={isSubmitting || loading} className="bg-blue-600 text-white px-4 py-2 rounded">
        {isSubmitting || loading ? 'Salvando...' : 'Salvar Perfil'}
      </button>
    </form>
  );
};

export default ProfileForm;
