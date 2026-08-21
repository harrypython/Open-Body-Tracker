"""
Serviços de Lógica de Negócio e Motor de Cálculo.

Este módulo contém os serviços responsáveis pela conversão de unidades,
cálculos de composição corporal e geração de milestones.
"""

from .unit_converter import UnitConverter
from .body_composition_calculator import BodyCompositionCalculator
from .milestone_engine import MilestoneEngine

__all__ = [
    "UnitConverter",
    "BodyCompositionCalculator",
    "MilestoneEngine",
]
