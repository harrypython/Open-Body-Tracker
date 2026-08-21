"""
Unit Converter Service - Fase 3.1

Responsável por converter valores entre diferentes unidades de medida,
sempre convertendo para a unidade base antes de armazenar no banco de dados.

Unidades Base:
- Peso: kg
- Comprimento (circunferências): cm
- Comprimento (dobras cutâneas): mm
"""

from typing import Dict, Tuple
from enum import Enum


class UnitType(Enum):
    """Tipos de unidades suportadas."""
    WEIGHT = "weight"
    LENGTH_CM = "length_cm"  # Para circunferências
    LENGTH_MM = "length_mm"  # Para dobras cutâneas


# Fatores de conversão para unidades base
# Peso -> kg
WEIGHT_CONVERSIONS: Dict[str, float] = {
    "kg": 1.0,
    "lbs": 0.45359237,
}

# Comprimento (cm) -> cm
LENGTH_CM_CONVERSIONS: Dict[str, float] = {
    "cm": 1.0,
    "in": 2.54,
}

# Comprimento (mm) -> mm
LENGTH_MM_CONVERSIONS: Dict[str, float] = {
    "mm": 1.0,
    "cm": 10.0,
    "in": 25.4,
}


class UnitConverter:
    """
    Serviço de conversão de unidades.
    
    Converte qualquer entrada para a unidade base antes de salvar,
    e converte da unidade base para a unidade preferida para exibição.
    """
    
    def __init__(self, default_unit_system: str = "METRIC"):
        """
        Inicializa o conversor com um sistema de unidades padrão.
        
        Args:
            default_unit_system: 'METRIC' ou 'IMPERIAL'
        """
        self.default_unit_system = default_unit_system
    
    def get_base_unit(self, metric_key: str) -> str:
        """
        Retorna a unidade base para uma determinada métrica.
        
        Args:
            metric_key: Chave da métrica (ex: 'weight_kg', 'arm_right_cm', 'tricipital_mm')
            
        Returns:
            A unidade base (kg, cm, ou mm)
        """
        if metric_key.startswith("weight"):
            return "kg"
        elif metric_key.endswith("_cm"):
            return "cm"
        elif metric_key.endswith("_mm"):
            return "mm"
        else:
            # Para outras métricas sem sufixo claro
            if "hr" in metric_key or "bpm" in metric_key:
                return "bpm"
            elif "bp" in metric_key or "mmhg" in metric_key:
                return "mmhg"
            else:
                return "kg"  # Default
    
    def to_base_unit(self, value: float, from_unit: str, metric_key: str) -> float:
        """
        Converte um valor da unidade fornecida para a unidade base.
        
        Args:
            value: O valor a ser convertido
            from_unit: A unidade de origem (ex: 'lbs', 'in', 'cm')
            metric_key: A chave da métrica para determinar o tipo de conversão
            
        Returns:
            O valor na unidade base
            
        Raises:
            ValueError: Se a unidade não for suportada
        """
        base_unit = self.get_base_unit(metric_key)
        
        # Unidades que já estão na base
        if from_unit == base_unit:
            return value
        
        # Determinar o tipo de conversão
        if base_unit == "kg":
            conversion_dict = WEIGHT_CONVERSIONS
        elif base_unit == "cm":
            conversion_dict = LENGTH_CM_CONVERSIONS
        elif base_unit == "mm":
            conversion_dict = LENGTH_MM_CONVERSIONS
        elif base_unit in ["bpm", "mmhg"]:
            # Estas unidades não precisam de conversão
            return value
        else:
            conversion_dict = WEIGHT_CONVERSIONS  # Default
        
        if from_unit not in conversion_dict:
            raise ValueError(f"Unidade não suportada: {from_unit} para {metric_key}")
        
        factor = conversion_dict[from_unit]
        return value * factor
    
    def from_base_unit(self, value: float, to_unit: str, metric_key: str) -> float:
        """
        Converte um valor da unidade base para a unidade desejada.
        
        Args:
            value: O valor na unidade base
            to_unit: A unidade de destino (ex: 'lbs', 'in', 'cm')
            metric_key: A chave da métrica para determinar o tipo de conversão
            
        Returns:
            O valor na unidade desejada
            
        Raises:
            ValueError: Se a unidade não for suportada
        """
        base_unit = self.get_base_unit(metric_key)
        
        # Unidades que já estão na base
        if to_unit == base_unit:
            return value
        
        # Determinar o tipo de conversão
        if base_unit == "kg":
            conversion_dict = WEIGHT_CONVERSIONS
        elif base_unit == "cm":
            conversion_dict = LENGTH_CM_CONVERSIONS
        elif base_unit == "mm":
            conversion_dict = LENGTH_MM_CONVERSIONS
        elif base_unit in ["bpm", "mmhg"]:
            return value
        else:
            conversion_dict = WEIGHT_CONVERSIONS
        
        if to_unit not in conversion_dict:
            raise ValueError(f"Unidade não suportada: {to_unit} para {metric_key}")
        
        factor = conversion_dict[to_unit]
        return value / factor
    
    def get_preferred_unit(self, metric_key: str, unit_system: str = None) -> str:
        """
        Retorna a unidade preferida para exibição baseada no sistema de unidades.
        
        Args:
            metric_key: A chave da métrica
            unit_system: 'METRIC' ou 'IMPERIAL' (usa o default se None)
            
        Returns:
            A unidade preferida para exibição
        """
        system = unit_system or self.default_unit_system
        base_unit = self.get_base_unit(metric_key)
        
        if system == "IMPERIAL":
            if base_unit == "kg":
                return "lbs"
            elif base_unit in ["cm", "mm"]:
                return "in"
            else:
                return base_unit
        else:
            return base_unit
    
    def round_trip_convert(
        self, 
        value: float, 
        from_unit: str, 
        metric_key: str,
        precision: int = 2
    ) -> Tuple[float, float]:
        """
        Realiza uma conversão de ida e volta para validação.
        
        Args:
            value: O valor original
            from_unit: A unidade original
            metric_key: A chave da métrica
            precision: Casas decimais para arredondamento
            
        Returns:
            Tupla (valor_na_base, valor_convertido_de_volta)
        """
        base_value = self.to_base_unit(value, from_unit, metric_key)
        back_value = self.from_base_unit(base_value, from_unit, metric_key)
        return (round(base_value, precision), round(back_value, precision))
