"""
Body Composition Calculator - Fase 3.2

Motor de cálculo de composição corporal que implementa:
- Fórmulas de Densidade Corporal (Jackson-Pollock 7-site)
- Fórmulas de % Gordura Corporal (Siri, Brozek)
- BMI (Índice de Massa Corporal)
- WHR (Relação Cintura/Quadril)
- Média bilateral e assimetria
"""

from typing import Dict, Optional, Tuple
from enum import Enum
import math


class Sex(Enum):
    """Sexo biológico para fórmulas específicas."""
    MALE = "male"
    FEMALE = "female"


class BodyCompositionCalculator:
    """
    Motor de cálculo de composição corporal.
    
    Implementa fórmulas validadas cientificamente para cálculo de
    densidade corporal, percentual de gordura e outras métricas derivadas.
    """
    
    # Constantes para fórmula de Siri
    SIRI_CONSTANT_A = 4.95
    SIRI_CONSTANT_B = 4.50
    
    # Constantes para fórmula de Brozek
    BROZEK_CONSTANT_A = 4.57
    BROZEK_CONSTANT_B = 4.142
    
    def __init__(self):
        """Inicializa o calculador."""
        pass
    
    def calculate_jackson_pollock_7_site_density(
        self,
        skinfolds: Dict[str, float],
        sex: Sex,
        age: int
    ) -> float:
        """
        Calcula a Densidade Corporal usando Jackson-Pollock 7-site.
        
        Args:
            skinfolds: Dicionário com as 7 dobras em mm:
                - pectoral_mm
                - mid_axillary_mm
                - tricipital_mm (ou triceps_mm)
                - subscapular_mm
                - abdominal_mm
                - suprailiac_mm
                - thigh_skinfold_mm (ou thigh_mm)
            sex: Sexo biológico (MALE ou FEMALE)
            age: Idade em anos
            
        Returns:
            Densidade corporal em g/cm³
            
        Raises:
            ValueError: Se alguma dobra obrigatória estiver faltando
        """
        required_sites = [
            "pectoral_mm",
            "mid_axillary_mm",
            "tricipital_mm",
            "subscapular_mm",
            "abdominal_mm",
            "suprailiac_mm",
            "thigh_skinfold_mm"
        ]
        
        # Validar presença de todas as dobras
        missing = []
        for site in required_sites:
            if site not in skinfolds:
                # Tentar variações de nome
                alt_names = {
                    "tricipital_mm": ["triceps_mm", "tricep_mm"],
                    "thigh_skinfold_mm": ["thigh_mm", "thigh_skinfold"]
                }
                found = False
                for alt in alt_names.get(site, []):
                    if alt in skinfolds:
                        found = True
                        break
                if not found:
                    missing.append(site)
        
        if missing:
            raise ValueError(f"Dobras cutâneas faltando: {', '.join(missing)}")
        
        # Somatório das 7 dobras
        sum_skinfolds = sum(skinfolds[site] for site in required_sites)
        
        # Fórmula de Jackson-Pollock 7-site
        if sex == Sex.MALE:
            # Para homens
            body_density = 1.112 - (0.00043499 * sum_skinfolds) + (0.00000055 * (sum_skinfolds ** 2)) - (0.00028826 * age)
        else:
            # Para mulheres
            body_density = 1.097 - (0.00046971 * sum_skinfolds) + (0.00000056 * (sum_skinfolds ** 2)) - (0.00012828 * age)
        
        return body_density
    
    def calculate_body_fat_percentage_siri(
        self,
        body_density: float
    ) -> float:
        """
        Calcula o % de Gordura Corporal usando a fórmula de Siri.
        
        Fórmula: BF% = (4.95 / Density - 4.50) * 100
        
        Args:
            body_density: Densidade corporal em g/cm³
            
        Returns:
            Percentual de gordura corporal
        """
        body_fat = (self.SIRI_CONSTANT_A / body_density - self.SIRI_CONSTANT_B) * 100
        return max(0.0, min(100.0, body_fat))  # Clamp entre 0 e 100
    
    def calculate_body_fat_percentage_brozek(
        self,
        body_density: float
    ) -> float:
        """
        Calcula o % de Gordura Corporal usando a fórmula de Brozek.
        
        Fórmula: BF% = (4.57 / Density - 4.142) * 100
        
        Args:
            body_density: Densidade corporal em g/cm³
            
        Returns:
            Percentual de gordura corporal
        """
        body_fat = (self.BROZEK_CONSTANT_A / body_density - self.BROZEK_CONSTANT_B) * 100
        return max(0.0, min(100.0, body_fat))  # Clamp entre 0 e 100
    
    def calculate_bmi(
        self,
        weight_kg: float,
        height_cm: float
    ) -> float:
        """
        Calcula o Índice de Massa Corporal (BMI).
        
        Fórmula: BMI = peso (kg) / altura² (m)
        
        Args:
            weight_kg: Peso em kg
            height_cm: Altura em cm
            
        Returns:
            BMI
        """
        height_m = height_cm / 100.0
        if height_m <= 0:
            raise ValueError("Altura deve ser maior que zero")
        
        bmi = weight_kg / (height_m ** 2)
        return bmi
    
    def calculate_whr(
        self,
        waist_cm: float,
        hip_cm: float
    ) -> float:
        """
        Calcula a Relação Cintura/Quadril (WHR - Waist-to-Hip Ratio).
        
        Fórmula: WHR = cintura / quadril
        
        Args:
            waist_cm: Circunferência da cintura em cm
            hip_cm: Circunferência do quadril em cm
            
        Returns:
            WHR
        """
        if hip_cm <= 0:
            raise ValueError("Circunferência do quadril deve ser maior que zero")
        
        whr = waist_cm / hip_cm
        return whr
    
    def calculate_bilateral_average(
        self,
        right_value: float,
        left_value: float
    ) -> float:
        """
        Calcula a média bilateral de uma medida.
        
        Args:
            right_value: Valor do lado direito
            left_value: Valor do lado esquerdo
            
        Returns:
            Média dos dois lados
        """
        return (right_value + left_value) / 2.0
    
    def calculate_asymmetry_percentage(
        self,
        right_value: float,
        left_value: float
    ) -> float:
        """
        Calcula a assimetria percentual entre lados direito e esquerdo.
        
        Fórmula: |direita - esquerda| / ((direita + esquerda) / 2) * 100
        
        Args:
            right_value: Valor do lado direito
            left_value: Valor do lado esquerdo
            
        Returns:
            Assimetria em porcentagem
        """
        average = self.calculate_bilateral_average(right_value, left_value)
        if average == 0:
            return 0.0
        
        asymmetry = abs(right_value - left_value) / average * 100
        return asymmetry
    
    def calculate_fat_mass(
        self,
        weight_kg: float,
        body_fat_percentage: float
    ) -> float:
        """
        Calcula a massa gorda em kg.
        
        Args:
            weight_kg: Peso total em kg
            body_fat_percentage: Percentual de gordura corporal
            
        Returns:
            Massa gorda em kg
        """
        return weight_kg * (body_fat_percentage / 100.0)
    
    def calculate_lean_mass(
        self,
        weight_kg: float,
        body_fat_percentage: float
    ) -> float:
        """
        Calcula a massa magra em kg.
        
        Args:
            weight_kg: Peso total em kg
            body_fat_percentage: Percentual de gordura corporal
            
        Returns:
            Massa magra em kg
        """
        fat_mass = self.calculate_fat_mass(weight_kg, body_fat_percentage)
        return weight_kg - fat_mass
    
    def calculate_full_composition(
        self,
        weight_kg: float,
        height_cm: float,
        skinfolds: Dict[str, float],
        sex: Sex,
        age: int,
        waist_cm: Optional[float] = None,
        hip_cm: Optional[float] = None,
        use_siri: bool = True
    ) -> Dict[str, float]:
        """
        Calcula todas as métricas de composição corporal.
        
        Args:
            weight_kg: Peso em kg
            height_cm: Altura em cm
            skinfolds: Dicionário com as dobras cutâneas em mm
            sex: Sexo biológico
            age: Idade em anos
            waist_cm: Circunferência da cintura (opcional)
            hip_cm: Circunferência do quadril (opcional)
            use_siri: True para usar Siri, False para Brozek
            
        Returns:
            Dicionário com todas as métricas calculadas:
            - body_density: Densidade corporal (g/cm³)
            - body_fat_percentage: % de gordura corporal
            - bmi: Índice de Massa Corporal
            - fat_mass_kg: Massa gorda em kg
            - lean_mass_kg: Massa magra em kg
            - whr: Relação cintura/quadril (se disponível)
        """
        results = {}
        
        # Densidade corporal
        body_density = self.calculate_jackson_pollock_7_site_density(
            skinfolds, sex, age
        )
        results["body_density"] = round(body_density, 4)
        
        # % Gordura corporal
        if use_siri:
            body_fat = self.calculate_body_fat_percentage_siri(body_density)
        else:
            body_fat = self.calculate_body_fat_percentage_brozek(body_density)
        results["body_fat_percentage"] = round(body_fat, 2)
        
        # BMI
        bmi = self.calculate_bmi(weight_kg, height_cm)
        results["bmi"] = round(bmi, 2)
        
        # Massa gorda e magra
        fat_mass = self.calculate_fat_mass(weight_kg, body_fat)
        lean_mass = self.calculate_lean_mass(weight_kg, body_fat)
        results["fat_mass_kg"] = round(fat_mass, 2)
        results["lean_mass_kg"] = round(lean_mass, 2)
        
        # WHR (se disponível)
        if waist_cm is not None and hip_cm is not None:
            whr = self.calculate_whr(waist_cm, hip_cm)
            results["whr"] = round(whr, 3)
        
        return results
