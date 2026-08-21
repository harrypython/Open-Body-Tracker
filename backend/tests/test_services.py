"""
Testes Unitários para os Serviços da Fase 3.

Cobre:
- UnitConverter (conversão de unidades)
- BodyCompositionCalculator (cálculos de composição corporal)
- MilestoneEngine (geração de milestones)
"""

import pytest
from datetime import datetime
from app.services.unit_converter import UnitConverter
from app.services.body_composition_calculator import BodyCompositionCalculator, Sex
from app.services.milestone_engine import MilestoneEngine, MilestoneType


class TestUnitConverter:
    """Testes para o serviço de conversão de unidades."""
    
    def setup_method(self):
        """Configura o conversor para cada teste."""
        self.converter = UnitConverter(default_unit_system="METRIC")
    
    def test_weight_kg_to_base(self):
        """Testa conversão de peso em kg (já está na base)."""
        result = self.converter.to_base_unit(75.0, "kg", "weight_kg")
        assert result == 75.0
    
    def test_weight_lbs_to_kg(self):
        """Testa conversão de lbs para kg."""
        # 10 lbs = 4.5359237 kg
        result = self.converter.to_base_unit(10.0, "lbs", "weight_kg")
        assert abs(result - 4.5359237) < 0.0001
    
    def test_weight_kg_to_lbs(self):
        """Testa conversão de kg para lbs."""
        # 10 kg = 22.0462 lbs
        result = self.converter.from_base_unit(10.0, "lbs", "weight_kg")
        assert abs(result - 22.0462) < 0.01
    
    def test_cm_to_base(self):
        """Testa conversão de cm (já está na base)."""
        result = self.converter.to_base_unit(35.0, "cm", "arm_right_cm")
        assert result == 35.0
    
    def test_inches_to_cm(self):
        """Testa conversão de polegadas para cm."""
        # 1 in = 2.54 cm
        result = self.converter.to_base_unit(1.0, "in", "arm_right_cm")
        assert abs(result - 2.54) < 0.0001
    
    def test_mm_to_base(self):
        """Testa conversão de mm (já está na base)."""
        result = self.converter.to_base_unit(15.0, "mm", "tricipital_mm")
        assert result == 15.0
    
    def test_round_trip_weight(self):
        """Testa conversão de ida e volta para peso sem perda."""
        original = 10.0
        base, back = self.converter.round_trip_convert(original, "lbs", "weight_kg")
        assert back == original
    
    def test_round_trip_length(self):
        """Testa conversão de ida e volta para comprimento sem perda."""
        original = 35.0
        base, back = self.converter.round_trip_convert(original, "in", "arm_right_cm")
        assert back == original
    
    def test_get_preferred_unit_metric(self):
        """Testa obtenção de unidade preferida no sistema métrico."""
        assert self.converter.get_preferred_unit("weight_kg", "METRIC") == "kg"
        assert self.converter.get_preferred_unit("arm_right_cm", "METRIC") == "cm"
        assert self.converter.get_preferred_unit("tricipital_mm", "METRIC") == "mm"
    
    def test_get_preferred_unit_imperial(self):
        """Testa obtenção de unidade preferida no sistema imperial."""
        assert self.converter.get_preferred_unit("weight_kg", "IMPERIAL") == "lbs"
        assert self.converter.get_preferred_unit("arm_right_cm", "IMPERIAL") == "in"
    
    def test_unsupported_unit_raises_error(self):
        """Testa que unidade não suportada levanta erro."""
        with pytest.raises(ValueError):
            self.converter.to_base_unit(10.0, "xyz", "weight_kg")


class TestBodyCompositionCalculator:
    """Testes para o calculador de composição corporal."""
    
    def setup_method(self):
        """Configura o calculador para cada teste."""
        self.calculator = BodyCompositionCalculator()
        
        # Valores de exemplo para homem de 30 anos
        self.test_skinfolds_male = {
            "pectoral_mm": 12.0,
            "mid_axillary_mm": 10.0,
            "tricipital_mm": 15.0,
            "subscapular_mm": 14.0,
            "abdominal_mm": 20.0,
            "suprailiac_mm": 11.0,
            "thigh_skinfold_mm": 22.0
        }
        
        # Valores de exemplo para mulher de 30 anos
        self.test_skinfolds_female = {
            "pectoral_mm": 18.0,
            "mid_axillary_mm": 14.0,
            "tricipital_mm": 22.0,
            "subscapular_mm": 16.0,
            "abdominal_mm": 25.0,
            "suprailiac_mm": 18.0,
            "thigh_skinfold_mm": 28.0
        }
    
    def test_jackson_pollock_density_male(self):
        """Testa cálculo de densidade corporal para homem."""
        density = self.calculator.calculate_jackson_pollock_7_site_density(
            self.test_skinfolds_male, Sex.MALE, 30
        )
        # Densidade típica para homem: 1.05 - 1.10 g/cm³
        assert 1.05 <= density <= 1.10
    
    def test_jackson_pollock_density_female(self):
        """Testa cálculo de densidade corporal para mulher."""
        density = self.calculator.calculate_jackson_pollock_7_site_density(
            self.test_skinfolds_female, Sex.FEMALE, 30
        )
        # Densidade típica para mulher: 1.03 - 1.08 g/cm³
        assert 1.03 <= density <= 1.08
    
    def test_missing_skinfold_raises_error(self):
        """Testa que dobra faltando levanta erro."""
        incomplete_skinfolds = {
            "pectoral_mm": 12.0,
            "mid_axillary_mm": 10.0,
            # Faltam várias dobras
        }
        with pytest.raises(ValueError) as exc_info:
            self.calculator.calculate_jackson_pollock_7_site_density(
                incomplete_skinfolds, Sex.MALE, 30
            )
        assert "Dobras cutâneas faltando" in str(exc_info.value)
    
    def test_body_fat_siri(self):
        """Testa cálculo de % gordura com fórmula de Siri."""
        density = 1.07  # Densidade de exemplo
        bf = self.calculator.calculate_body_fat_percentage_siri(density)
        # BF% típico: 10-25%
        assert 10.0 <= bf <= 25.0
    
    def test_body_fat_brozek(self):
        """Testa cálculo de % gordura com fórmula de Brozek."""
        density = 1.07
        bf = self.calculator.calculate_body_fat_percentage_brozek(density)
        # BF% típico: 10-25%
        assert 10.0 <= bf <= 25.0
    
    def test_bmi_calculation(self):
        """Testa cálculo de BMI."""
        # BMI = 75 / (1.75²) = 24.49
        bmi = self.calculator.calculate_bmi(75.0, 175.0)
        assert abs(bmi - 24.49) < 0.1
    
    def test_whr_calculation(self):
        """Testa cálculo de WHR."""
        # WHR = 82 / 96 = 0.854
        whr = self.calculator.calculate_whr(82.0, 96.0)
        assert abs(whr - 0.854) < 0.001
    
    def test_bilateral_average(self):
        """Testa cálculo de média bilateral."""
        avg = self.calculator.calculate_bilateral_average(35.0, 34.0)
        assert avg == 34.5
    
    def test_asymmetry_percentage(self):
        """Testa cálculo de assimetria percentual."""
        # Braço D=35, E=34 -> assimetria = |35-34| / 34.5 * 100 = 2.9%
        asymmetry = self.calculator.calculate_asymmetry_percentage(35.0, 34.0)
        assert abs(asymmetry - 2.9) < 0.2
    
    def test_fat_mass_calculation(self):
        """Testa cálculo de massa gorda."""
        # 75kg com 15% BF = 11.25kg de gordura
        fat_mass = self.calculator.calculate_fat_mass(75.0, 15.0)
        assert abs(fat_mass - 11.25) < 0.01
    
    def test_lean_mass_calculation(self):
        """Testa cálculo de massa magra."""
        # 75kg com 15% BF = 63.75kg de massa magra
        lean_mass = self.calculator.calculate_lean_mass(75.0, 15.0)
        assert abs(lean_mass - 63.75) < 0.01
    
    def test_full_composition(self):
        """Testa cálculo completo de composição corporal."""
        results = self.calculator.calculate_full_composition(
            weight_kg=75.0,
            height_cm=175.0,
            skinfolds=self.test_skinfolds_male,
            sex=Sex.MALE,
            age=30,
            waist_cm=82.0,
            hip_cm=96.0
        )
        
        assert "body_density" in results
        assert "body_fat_percentage" in results
        assert "bmi" in results
        assert "fat_mass_kg" in results
        assert "lean_mass_kg" in results
        assert "whr" in results
        
        # Verificar valores razoáveis
        assert 1.05 <= results["body_density"] <= 1.10
        assert 5.0 <= results["body_fat_percentage"] <= 25.0
        assert 20.0 <= results["bmi"] <= 30.0
        assert 0.7 <= results["whr"] <= 1.0


class TestMilestoneEngine:
    """Testes para o motor de milestones."""
    
    def setup_method(self):
        """Configura o engine para cada teste."""
        self.engine = MilestoneEngine()
        
        self.current_assessment = {
            "assessment_date": "2023-10-27",
            "weight_kg": 70.0,
            "body_fat_percentage": 12.0,
            "bmi": 22.5,
            "whr": 0.85
        }
        
        self.historical_assessments = [
            {
                "assessment_date": "2023-01-15",
                "weight_kg": 80.0,
                "body_fat_percentage": 18.0,
                "bmi": 25.5,
                "whr": 0.90
            },
            {
                "assessment_date": "2023-05-20",
                "weight_kg": 75.0,
                "body_fat_percentage": 15.0,
                "bmi": 24.0,
                "whr": 0.87
            }
        ]
    
    def test_lowest_body_fat_milestone(self):
        """Testa milestone de menor gordura corporal."""
        milestones = self.engine.check_milestones(
            self.current_assessment,
            self.historical_assessments
        )
        
        lowest_bf_milestones = [
            m for m in milestones 
            if m.milestone_type == MilestoneType.LOWEST_BODY_FAT
        ]
        assert len(lowest_bf_milestones) == 1
        assert lowest_bf_milestones[0].value == 12.0
    
    def test_lowest_weight_milestone(self):
        """Testa milestone de menor peso."""
        milestones = self.engine.check_milestones(
            self.current_assessment,
            self.historical_assessments
        )
        
        lowest_weight_milestones = [
            m for m in milestones 
            if m.milestone_type == MilestoneType.LOWEST_WEIGHT
        ]
        assert len(lowest_weight_milestones) == 1
        assert lowest_weight_milestones[0].value == 70.0
    
    def test_weight_loss_5kg_milestone(self):
        """Testa milestone de perda de 5kg."""
        milestones = self.engine.check_milestones(
            self.current_assessment,
            self.historical_assessments
        )
        
        weight_loss_milestones = [
            m for m in milestones 
            if m.milestone_type == MilestoneType.WEIGHT_LOSS_5KG
        ]
        # 80kg -> 70kg = 10kg perdidos, deve gerar milestone
        assert len(weight_loss_milestones) == 1
    
    def test_bmi_improvement_milestone(self):
        """Testa milestone de melhoria de BMI."""
        milestones = self.engine.check_milestones(
            self.current_assessment,
            self.historical_assessments
        )
        
        bmi_milestones = [
            m for m in milestones 
            if m.milestone_type == MilestoneType.BMI_IMPROVEMENT
        ]
        # 25.5 -> 22.5 = 3 pontos de melhoria
        assert len(bmi_milestones) == 1
    
    def test_no_milestones_first_assessment(self):
        """Testa que primeira avaliação não gera milestones comparativos."""
        milestones = self.engine.check_milestones(
            self.current_assessment,
            []  # Sem histórico
        )
        
        # Não deve ter milestones comparativos sem histórico
        assert len(milestones) == 0
    
    def test_milestone_to_dict(self):
        """Testa serialização de milestone para dicionário."""
        milestone = self.engine.check_milestones(
            self.current_assessment,
            self.historical_assessments
        )[0]
        
        data = milestone.to_dict()
        assert "type" in data
        assert "title" in data
        assert "description" in data
        assert "achieved_at" in data
        assert "value" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
