export type UnitSystem = 'metric' | 'imperial';

export interface UserProfile {
  id: string;
  email: string;
  full_name: string;
  birth_date?: string;
  biological_sex?: 'male' | 'female';
  height_cm?: number;
  default_unit_system: UnitSystem;
}

export interface AuthState {
  user: UserProfile | null;
  token: string | null;
  isAuthenticated: boolean;
}

export interface MetricCatalog {
  id: string;
  key: string;
  category: 'vitals' | 'circumference' | 'skinfold';
  is_bilateral: boolean;
}

export interface UnitCode {
  id: string;
  key: string;
  system_type: 'METRIC' | 'IMPERIAL';
  conversion_factor_to_base: number;
}
