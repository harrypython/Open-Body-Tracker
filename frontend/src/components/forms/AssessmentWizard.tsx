import React, { useState } from 'react';
import { useForm, SubmitHandler } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { useTranslation } from 'react-i18next';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card';

// Schema for Step 1: Vitals
const vitalsSchema = z.object({
  assessment_date: z.string().min(1, 'Required'),
  weight: z.number().positive('Weight must be positive'),
  resting_hr: z.number().min(30).max(250).optional(),
  bp_systolic: z.number().min(70).max(250).optional(),
  bp_diastolic: z.number().min(40).max(150).optional(),
});

// Schema for Step 2: Circumferences
const circumferencesSchema = z.object({
  arm_right: z.number().min(10).max(100).optional(),
  arm_left: z.number().min(10).max(100).optional(),
  arm_right_contracted: z.number().min(10).max(100).optional(),
  arm_left_contracted: z.number().min(10).max(100).optional(),
  forearm_right: z.number().min(10).max(100).optional(),
  forearm_left: z.number().min(10).max(100).optional(),
  chest: z.number().min(30).max(200).optional(),
  abdomen: z.number().min(30).max(200).optional(),
  waist: z.number().min(30).max(200).optional(),
  hip: z.number().min(30).max(200).optional(),
  thigh_right: z.number().min(20).max(150).optional(),
  thigh_left: z.number().min(20).max(150).optional(),
  calf_right: z.number().min(15).max(100).optional(),
  calf_left: z.number().min(15).max(100).optional(),
});

// Schema for Step 3: Skinfolds (Jackson-Pollock 7-site)
const skinfoldsSchema = z.object({
  protocol: z.enum(['jackson_pollock_7', 'jackson_pollock_3', 'durnin_womersley']),
  pectoral: z.number().min(1).max(100).optional(),
  mid_axillary: z.number().min(1).max(100).optional(),
  tricipital: z.number().min(1).max(100).optional(),
  subscapular: z.number().min(1).max(100).optional(),
  abdominal: z.number().min(1).max(100).optional(),
  suprailiac: z.number().min(1).max(100).optional(),
  thigh_skinfold: z.number().min(1).max(100).optional(),
  bicipital: z.number().min(1).max(100).optional(),
});

// Combined schema for wizard
const assessmentWizardSchema = vitalsSchema.merge(circumferencesSchema).merge(skinfoldsSchema);

type AssessmentFormData = z.infer<typeof assessmentWizardSchema>;

interface AssessmentWizardProps {
  onComplete?: (data: AssessmentFormData) => void;
}

export const AssessmentWizard: React.FC<AssessmentWizardProps> = ({ onComplete }) => {
  const { t } = useTranslation();
  const [currentStep, setCurrentStep] = useState(1);
  const [bodyFatResult, setBodyFatResult] = useState<{ bfPercent: number; fatMass: number; leanMass: number } | null>(null);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<AssessmentFormData>({
    resolver: zodResolver(assessmentWizardSchema),
    defaultValues: {
      assessment_date: new Date().toISOString().split('T')[0],
      weight: 0,
      resting_hr: undefined,
      bp_systolic: undefined,
      bp_diastolic: undefined,
      arm_right: undefined,
      arm_left: undefined,
      arm_right_contracted: undefined,
      arm_left_contracted: undefined,
      forearm_right: undefined,
      forearm_left: undefined,
      chest: undefined,
      abdomen: undefined,
      waist: undefined,
      hip: undefined,
      thigh_right: undefined,
      thigh_left: undefined,
      calf_right: undefined,
      calf_left: undefined,
      protocol: 'jackson_pollock_7',
      pectoral: undefined,
      mid_axillary: undefined,
      tricipital: undefined,
      subscapular: undefined,
      abdominal: undefined,
      suprailiac: undefined,
      thigh_skinfold: undefined,
      bicipital: undefined,
    },
  });

  const watchedValues = watch();
  const weight = watch('weight');

  // Calculate BMI in real-time
  const calculateBMI = () => {
    const heightCm = 170; // TODO: Get from user profile
    if (weight && heightCm) {
      return (weight / ((heightCm / 100) ** 2)).toFixed(1);
    }
    return null;
  };

  // Calculate asymmetry percentage
  const calculateAsymmetry = (left: number | undefined, right: number | undefined) => {
    if (left && right && left > 0 && right > 0) {
      return Math.abs(((right - left) / ((right + left) / 2)) * 100).toFixed(1);
    }
    return null;
  };

  // Calculate WHR (Waist-to-Hip Ratio)
  const calculateWHR = () => {
    const waist = watch('waist');
    const hip = watch('hip');
    if (waist && hip && waist > 0 && hip > 0) {
      return (waist / hip).toFixed(2);
    }
    return null;
  };

  // Jackson-Pollock 7-site body fat calculation (simplified)
  const calculateBodyFat = () => {
    const { pectoral, mid_axillary, tricipital, subscapular, abdominal, suprailiac, thigh_skinfold } = watchedValues;
    
    // Check if all 7 required skinfolds are present
    const requiredSkinfoods = [pectoral, mid_axillary, tricipital, subscapular, abdominal, suprailiac, thigh_skinfold];
    const allPresent = requiredSkinfoods.every(v => v !== undefined && v !== null && v > 0);
    
    if (!allPresent) {
      setBodyFatResult(null);
      return;
    }

    const sum7 = pectoral! + mid_axillary! + tricipital! + subscapular! + abdominal! + suprailiac! + thigh_skinfold!;
    
    // Simplified Jackson-Pollock formula (for demonstration)
    // In production, use proper age/sex-specific formulas
    const age = 30; // TODO: Get from user profile
    const sex = 'male'; // TODO: Get from user profile
    
    let bodyDensity: number;
    if (sex === 'male') {
      bodyDensity = 1.112 - 0.00043499 * sum7 + 0.00000055 * (sum7 ** 2) - 0.00028826 * age;
    } else {
      bodyDensity = 1.097 - 0.00046971 * sum7 + 0.00000056 * (sum7 ** 2) - 0.00012828 * age;
    }

    // Siri equation for body fat percentage
    const bfPercent = ((4.95 / bodyDensity) - 4.50) * 100;
    const fatMass = (weight! * bfPercent) / 100;
    const leanMass = weight! - fatMass;

    setBodyFatResult({
      bfPercent: parseFloat(bfPercent.toFixed(1)),
      fatMass: parseFloat(fatMass.toFixed(1)),
      leanMass: parseFloat(leanMass.toFixed(1)),
    });
  };

  // Auto-calculate body fat when skinfolds change
  React.useEffect(() => {
    if (currentStep === 3) {
      calculateBodyFat();
    }
  }, [watchedValues.pectoral, watchedValues.mid_axillary, watchedValues.tricipital, 
      watchedValues.subscapular, watchedValues.abdominal, watchedValues.suprailiac, 
      watchedValues.thigh_skinfold, weight]);

  const onSubmit: SubmitHandler<AssessmentFormData> = (data) => {
    console.log('Assessment data:', data);
    // TODO: Send to API
    if (onComplete) {
      onComplete(data);
    }
  };

  const nextStep = () => setCurrentStep(prev => Math.min(prev + 1, 4));
  const prevStep = () => setCurrentStep(prev => Math.max(prev - 1, 1));

  // Render step content
  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">{t('assessment.vitals')}</h3>
            
            <Input
              label={t('assessment.date')}
              type="date"
              {...register('assessment_date')}
              error={errors.assessment_date?.message}
            />

            <div className="grid grid-cols-2 gap-4">
              <Input
                label={`${t('assessment.weight')} (${t('units.kg')})`}
                type="number"
                step="0.1"
                {...register('weight', { valueAsNumber: true })}
                error={errors.weight?.message}
              />
              {calculateBMI() && (
                <div className="flex items-end">
                  <p className="text-sm text-gray-600">BMI: <span className="font-semibold">{calculateBMI()}</span></p>
                </div>
              )}
            </div>

            <Input
              label={`${t('assessment.restingHeartRate')} (${t('units.bpm')})`}
              type="number"
              {...register('resting_hr', { valueAsNumber: true })}
              error={errors.resting_hr?.message}
            />

            <div className="grid grid-cols-2 gap-4">
              <Input
                label={`${t('assessment.systolic')} (${t('units.mmhg')})`}
                type="number"
                {...register('bp_systolic', { valueAsNumber: true })}
                error={errors.bp_systolic?.message}
              />
              <Input
                label={`${t('assessment.diastolic')} (${t('units.mmhg')})`}
                type="number"
                {...register('bp_diastolic', { valueAsNumber: true })}
                error={errors.bp_diastolic?.message}
              />
            </div>
          </div>
        );

      case 2:
        return (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold">{t('assessment.circumferences')}</h3>

            {/* Upper Limbs */}
            <Card>
              <CardHeader>
                <CardTitle className="text-base">{t('metrics.upper_limbs') || 'Upper Limbs'}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <Input
                    label={`${t('metrics.arm_right_cm')} (${t('units.cm')})`}
                    type="number"
                    step="0.1"
                    {...register('arm_right', { valueAsNumber: true })}
                    error={errors.arm_right?.message}
                  />
                  <Input
                    label={`${t('metrics.arm_left_cm')} (${t('units.cm')})`}
                    type="number"
                    step="0.1"
                    {...register('arm_left', { valueAsNumber: true })}
                    error={errors.arm_left?.message}
                  />
                </div>
                {calculateAsymmetry(watchedValues.arm_left, watchedValues.arm_right) && (
                  <p className="text-xs text-gray-500">
                    Asymmetry: {calculateAsymmetry(watchedValues.arm_left, watchedValues.arm_right)}%
                  </p>
                )}

                <div className="grid grid-cols-2 gap-4">
                  <Input
                    label={`${t('metrics.arm_right_contracted_cm')} (${t('units.cm')})`}
                    type="number"
                    step="0.1"
                    {...register('arm_right_contracted', { valueAsNumber: true })}
                    error={errors.arm_right_contracted?.message}
                  />
                  <Input
                    label={`${t('metrics.arm_left_contracted_cm')} (${t('units.cm')})`}
                    type="number"
                    step="0.1"
                    {...register('arm_left_contracted', { valueAsNumber: true })}
                    error={errors.arm_left_contracted?.message}
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <Input
                    label={`${t('metrics.forearm_right_cm')} (${t('units.cm')})`}
                    type="number"
                    step="0.1"
                    {...register('forearm_right', { valueAsNumber: true })}
                    error={errors.forearm_right?.message}
                  />
                  <Input
                    label={`${t('metrics.forearm_left_cm')} (${t('units.cm')})`}
                    type="number"
                    step="0.1"
                    {...register('forearm_left', { valueAsNumber: true })}
                    error={errors.forearm_left?.message}
                  />
                </div>
              </CardContent>
            </Card>

            {/* Trunk */}
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Trunk</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <Input
                    label={`${t('metrics.chest_cm')} (${t('units.cm')})`}
                    type="number"
                    step="0.1"
                    {...register('chest', { valueAsNumber: true })}
                    error={errors.chest?.message}
                  />
                  <Input
                    label={`${t('metrics.abdomen_cm')} (${t('units.cm')})`}
                    type="number"
                    step="0.1"
                    {...register('abdomen', { valueAsNumber: true })}
                    error={errors.abdomen?.message}
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <Input
                    label={`${t('metrics.waist_cm')} (${t('units.cm')})`}
                    type="number"
                    step="0.1"
                    {...register('waist', { valueAsNumber: true })}
                    error={errors.waist?.message}
                  />
                  <Input
                    label={`${t('metrics.hip_cm')} (${t('units.cm')})`}
                    type="number"
                    step="0.1"
                    {...register('hip', { valueAsNumber: true })}
                    error={errors.hip?.message}
                  />
                </div>
                {calculateWHR() && (
                  <p className="text-xs text-gray-500">
                    WHR (Waist/Hip): <span className="font-semibold">{calculateWHR()}</span>
                  </p>
                )}
              </CardContent>
            </Card>

            {/* Lower Limbs */}
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Lower Limbs</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <Input
                    label={`${t('metrics.thigh_right_cm')} (${t('units.cm')})`}
                    type="number"
                    step="0.1"
                    {...register('thigh_right', { valueAsNumber: true })}
                    error={errors.thigh_right?.message}
                  />
                  <Input
                    label={`${t('metrics.thigh_left_cm')} (${t('units.cm')})`}
                    type="number"
                    step="0.1"
                    {...register('thigh_left', { valueAsNumber: true })}
                    error={errors.thigh_left?.message}
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <Input
                    label={`${t('metrics.calf_right_cm')} (${t('units.cm')})`}
                    type="number"
                    step="0.1"
                    {...register('calf_right', { valueAsNumber: true })}
                    error={errors.calf_right?.message}
                  />
                  <Input
                    label={`${t('metrics.calf_left_cm')} (${t('units.cm')})`}
                    type="number"
                    step="0.1"
                    {...register('calf_left', { valueAsNumber: true })}
                    error={errors.calf_left?.message}
                  />
                </div>
              </CardContent>
            </Card>
          </div>
        );

      case 3:
        return (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold">{t('assessment.skinfolds')}</h3>

            <div className="flex flex-col">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                {t('assessment.protocol')}
              </label>
              <select
                {...register('protocol')}
                className="flex h-10 w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600"
              >
                <option value="jackson_pollock_7">Jackson & Pollock 7-site</option>
                <option value="jackson_pollock_3">Jackson & Pollock 3-site</option>
                <option value="durnin_womersley">Durnin-Womersley</option>
              </select>
            </div>

            <Card>
              <CardHeader>
                <CardTitle className="text-base">Skinfold Measurements ({t('units.mm')})</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <Input
                    label={t('metrics.pectoral_mm')}
                    type="number"
                    step="0.5"
                    {...register('pectoral', { valueAsNumber: true })}
                    error={errors.pectoral?.message}
                  />
                  <Input
                    label={t('metrics.mid_axillary_mm')}
                    type="number"
                    step="0.5"
                    {...register('mid_axillary', { valueAsNumber: true })}
                    error={errors.mid_axillary?.message}
                  />
                  <Input
                    label={t('metrics.tricipital_mm')}
                    type="number"
                    step="0.5"
                    {...register('tricipital', { valueAsNumber: true })}
                    error={errors.tricipital?.message}
                  />
                  <Input
                    label={t('metrics.subscapular_mm')}
                    type="number"
                    step="0.5"
                    {...register('subscapular', { valueAsNumber: true })}
                    error={errors.subscapular?.message}
                  />
                  <Input
                    label={t('metrics.abdominal_mm')}
                    type="number"
                    step="0.5"
                    {...register('abdominal', { valueAsNumber: true })}
                    error={errors.abdominal?.message}
                  />
                  <Input
                    label={t('metrics.suprailiac_mm')}
                    type="number"
                    step="0.5"
                    {...register('suprailiac', { valueAsNumber: true })}
                    error={errors.suprailiac?.message}
                  />
                  <Input
                    label={t('metrics.thigh_skinfold_mm')}
                    type="number"
                    step="0.5"
                    {...register('thigh_skinfold', { valueAsNumber: true })}
                    error={errors.thigh_skinfold?.message}
                  />
                  <Input
                    label={t('metrics.bicipital_mm')}
                    type="number"
                    step="0.5"
                    {...register('bicipital', { valueAsNumber: true })}
                    error={errors.bicipital?.message}
                  />
                </div>
              </CardContent>
            </Card>

            {/* Real-time Body Fat Result */}
            {bodyFatResult && (
              <Card className="bg-green-50 dark:bg-green-900/20 border-green-200">
                <CardHeader>
                  <CardTitle className="text-base text-green-800 dark:text-green-300">
                    Body Composition Results
                  </CardTitle>
                </CardHeader>
                <CardContent className="grid grid-cols-3 gap-4">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Body Fat %</p>
                    <p className="text-2xl font-bold text-green-700 dark:text-green-400">{bodyFatResult.bfPercent}%</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Fat Mass</p>
                    <p className="text-2xl font-bold text-green-700 dark:text-green-400">{bodyFatResult.fatMass} kg</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Lean Mass</p>
                    <p className="text-2xl font-bold text-green-700 dark:text-green-400">{bodyFatResult.leanMass} kg</p>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        );

      case 4:
        return (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold">{t('assessment.review')}</h3>

            <Card>
              <CardHeader>
                <CardTitle className="text-base">Summary</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <h4 className="font-semibold text-sm">Vitals</h4>
                    <p className="text-sm">Date: {watchedValues.assessment_date}</p>
                    <p className="text-sm">Weight: {watchedValues.weight} kg</p>
                    <p className="text-sm">Resting HR: {watchedValues.resting_hr || 'N/A'} bpm</p>
                    <p className="text-sm">BP: {watchedValues.bp_systolic || 'N/A'}/{watchedValues.bp_diastolic || 'N/A'} mmHg</p>
                  </div>

                  <div>
                    <h4 className="font-semibold text-sm">Body Fat Results</h4>
                    {bodyFatResult ? (
                      <>
                        <p className="text-sm">Body Fat: {bodyFatResult.bfPercent}%</p>
                        <p className="text-sm">Fat Mass: {bodyFatResult.fatMass} kg</p>
                        <p className="text-sm">Lean Mass: {bodyFatResult.leanMass} kg</p>
                      </>
                    ) : (
                      <p className="text-sm text-gray-500">Complete skinfold measurements to see results</p>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-base">{t('assessment.photos')}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-3 gap-4">
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center">
                    <p className="text-sm">Front</p>
                    <input type="file" accept="image/*" className="mt-2 text-xs" />
                  </div>
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center">
                    <p className="text-sm">Side</p>
                    <input type="file" accept="image/*" className="mt-2 text-xs" />
                  </div>
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center">
                    <p className="text-sm">Back</p>
                    <input type="file" accept="image/*" className="mt-2 text-xs" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <h1 className="text-3xl font-bold mb-6">{t('assessment.new')}</h1>

      {/* Progress Indicator */}
      <div className="mb-8">
        <div className="flex justify-between mb-2">
          {[1, 2, 3, 4].map((step) => (
            <div
              key={step}
              className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold ${
                currentStep >= step
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-600'
              }`}
            >
              {step}
            </div>
          ))}
        </div>
        <div className="flex justify-between text-xs text-gray-600">
          <span>{t('assessment.vitals')}</span>
          <span>{t('assessment.circumferences')}</span>
          <span>{t('assessment.skinfolds')}</span>
          <span>{t('assessment.review')}</span>
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)}>
        <div className="mb-8">
          {renderStep()}
        </div>

        <div className="flex justify-between">
          <Button
            type="button"
            variant="secondary"
            onClick={prevStep}
            disabled={currentStep === 1}
          >
            {t('common.back')}
          </Button>

          {currentStep < 4 ? (
            <Button type="button" variant="primary" onClick={nextStep}>
              {t('common.next')}
            </Button>
          ) : (
            <>
              <Button type="button" variant="secondary">
                {t('assessment.saveDraft')}
              </Button>
              <Button type="submit" variant="primary">
                {t('assessment.finalize')}
              </Button>
            </>
          )}
        </div>
      </form>
    </div>
  );
};
