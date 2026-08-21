import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { UnitSystem } from '../types';

interface UnitContextType {
  unitSystem: UnitSystem;
  toggleUnitSystem: () => void;
  convertWeight: (value: number, toSystem?: UnitSystem) => number;
  convertLength: (value: number, toSystem?: UnitSystem) => number;
  getWeightUnit: () => string;
  getLengthUnit: () => string;
}

const UnitContext = createContext<UnitContextType | undefined>(undefined);

export const useUnits = () => {
  const context = useContext(UnitContext);
  if (!context) {
    throw new Error('useUnits must be used within a UnitProvider');
  }
  return context;
};

interface UnitProviderProps {
  children: ReactNode;
  defaultSystem?: UnitSystem;
}

export const UnitProvider: React.FC<UnitProviderProps> = ({ 
  children, 
  defaultSystem = 'metric' 
}) => {
  const [unitSystem, setUnitSystem] = useState<UnitSystem>(() => {
    const saved = localStorage.getItem('unit_system') as UnitSystem;
    return saved || defaultSystem;
  });

  useEffect(() => {
    localStorage.setItem('unit_system', unitSystem);
  }, [unitSystem]);

  const toggleUnitSystem = () => {
    setUnitSystem(prev => prev === 'metric' ? 'imperial' : 'metric');
  };

  const convertWeight = (value: number, toSystem?: UnitSystem): number => {
    const target = toSystem || unitSystem;
    if (target === 'metric') {
      // lbs to kg
      return value / 2.20462;
    } else {
      // kg to lbs
      return value * 2.20462;
    }
  };

  const convertLength = (value: number, toSystem?: UnitSystem): number => {
    const target = toSystem || unitSystem;
    if (target === 'metric') {
      // in to cm
      return value * 2.54;
    } else {
      // cm to in
      return value / 2.54;
    }
  };

  const getWeightUnit = (): string => {
    return unitSystem === 'metric' ? 'kg' : 'lbs';
  };

  const getLengthUnit = (): string => {
    return unitSystem === 'metric' ? 'cm' : 'in';
  };

  return (
    <UnitContext.Provider value={{ 
      unitSystem, 
      toggleUnitSystem, 
      convertWeight, 
      convertLength,
      getWeightUnit,
      getLengthUnit,
    }}>
      {children}
    </UnitContext.Provider>
  );
};
