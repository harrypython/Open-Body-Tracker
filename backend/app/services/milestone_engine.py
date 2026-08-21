"""
Milestone Engine - Fase 3.3

Motor de geração de milestones (marcos) que compara a avaliação atual
com o histórico para gerar "badges" e conquistas.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class MilestoneType(Enum):
    """Tipos de milestones suportados."""
    LOWEST_BODY_FAT = "lowest_body_fat"
    HIGHEST_BODY_FAT = "highest_body_fat"
    WEIGHT_LOSS_5KG = "weight_loss_5kg"
    WEIGHT_GAIN_5KG = "weight_gain_5kg"
    LOWEST_WEIGHT = "lowest_weight"
    HIGHEST_WEIGHT = "highest_weight"
    BMI_IMPROVEMENT = "bmi_improvement"
    WHR_IMPROVEMENT = "whr_improvement"
    ASSESSMENT_COUNT = "assessment_count"
    CONSISTENCY = "consistency"


class Milestone:
    """Representa um milestone/conquista."""
    
    def __init__(
        self,
        milestone_type: MilestoneType,
        title: str,
        description: str,
        achieved_at: datetime,
        value: float,
        previous_value: Optional[float] = None,
        icon: str = "🏆"
    ):
        self.milestone_type = milestone_type
        self.title = title
        self.description = description
        self.achieved_at = achieved_at
        self.value = value
        self.previous_value = previous_value
        self.icon = icon
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o milestone para dicionário."""
        return {
            "type": self.milestone_type.value,
            "title": self.title,
            "description": self.description,
            "achieved_at": self.achieved_at.isoformat(),
            "value": self.value,
            "previous_value": self.previous_value,
            "icon": self.icon
        }


class MilestoneEngine:
    """
    Motor de milestones que analisa o histórico de avaliações
    e gera conquistas baseadas em melhorias e recordes pessoais.
    """
    
    # Configuração dos milestones
    MILESTONE_CONFIGS = {
        MilestoneType.LOWEST_BODY_FAT: {
            "title": "Menor Gordura Corporal",
            "description": "Novo recorde pessoal de menor % de gordura corporal!",
            "icon": "🔥"
        },
        MilestoneType.HIGHEST_BODY_FAT: {
            "title": "Maior Gordura Corporal",
            "description": "Atenção: maior % de gordura corporal registrado.",
            "icon": "⚠️"
        },
        MilestoneType.WEIGHT_LOSS_5KG: {
            "title": "Perdeu 5kg",
            "description": "Parabéns! Você perdeu 5kg desde o início!",
            "icon": "⬇️"
        },
        MilestoneType.WEIGHT_GAIN_5KG: {
            "title": "Ganhou 5kg",
            "description": "Você ganhou 5kg desde o início!",
            "icon": "⬆️"
        },
        MilestoneType.LOWEST_WEIGHT: {
            "title": "Menor Peso",
            "description": "Novo recorde de menor peso!",
            "icon": "🎯"
        },
        MilestoneType.HIGHEST_WEIGHT: {
            "title": "Maior Peso",
            "description": "Maior peso registrado.",
            "icon": "📊"
        },
        MilestoneType.BMI_IMPROVEMENT: {
            "title": "BMI Melhorou",
            "description": "Seu BMI melhorou significativamente!",
            "icon": "💪"
        },
        MilestoneType.WHR_IMPROVEMENT: {
            "title": "WHR Melhorou",
            "description": "Sua relação cintura/quadril melhorou!",
            "icon": "📉"
        },
        MilestoneType.ASSESSMENT_COUNT: {
            "title": "Avaliação #{count}",
            "description": "Você completou {count} avaliações!",
            "icon": "📝"
        },
        MilestoneType.CONSISTENCY: {
            "title": "Consistente!",
            "description": "Avaliou-se regularmente por {days} dias!",
            "icon": "⭐"
        }
    }
    
    def __init__(self):
        """Inicializa o motor de milestones."""
        pass
    
    def check_milestones(
        self,
        current_assessment: Dict[str, Any],
        historical_assessments: List[Dict[str, Any]]
    ) -> List[Milestone]:
        """
        Verifica e gera todos os milestones aplicáveis.
        
        Args:
            current_assessment: Dados da avaliação atual
            historical_assessments: Lista de avaliações anteriores ordenadas por data
            
        Returns:
            Lista de milestones conquistados nesta avaliação
        """
        milestones = []
        
        # Verificar cada tipo de milestone
        milestones.extend(self._check_weight_milestones(
            current_assessment, historical_assessments
        ))
        milestones.extend(self._check_body_fat_milestones(
            current_assessment, historical_assessments
        ))
        milestones.extend(self._check_bmi_milestones(
            current_assessment, historical_assessments
        ))
        milestones.extend(self._check_whr_milestones(
            current_assessment, historical_assessments
        ))
        milestones.extend(self._check_assessment_count_milestone(
            current_assessment, historical_assessments
        ))
        
        return milestones
    
    def _check_weight_milestones(
        self,
        current: Dict[str, Any],
        history: List[Dict[str, Any]]
    ) -> List[Milestone]:
        """Verifica milestones relacionados ao peso."""
        milestones = []
        current_weight = current.get("weight_kg")
        config = self.MILESTONE_CONFIGS
        
        if current_weight is None:
            return milestones
        
        assessment_date = current.get("assessment_date", datetime.now())
        if isinstance(assessment_date, str):
            assessment_date = datetime.fromisoformat(assessment_date.replace('Z', '+00:00'))
        
        if not history:
            # Primeira avaliação - estabelece baseline
            return milestones
        
        # Menor peso
        min_weight = min(h.get("weight_kg", float('inf')) for h in history if h.get("weight_kg"))
        if current_weight < min_weight:
            milestones.append(Milestone(
                milestone_type=MilestoneType.LOWEST_WEIGHT,
                title=config[MilestoneType.LOWEST_WEIGHT]["title"],
                description=config[MilestoneType.LOWEST_WEIGHT]["description"],
                achieved_at=assessment_date,
                value=current_weight,
                previous_value=min_weight,
                icon=config[MilestoneType.LOWEST_WEIGHT]["icon"]
            ))
        
        # Maior peso
        max_weight = max(h.get("weight_kg", 0) for h in history if h.get("weight_kg"))
        if current_weight > max_weight:
            milestones.append(Milestone(
                milestone_type=MilestoneType.HIGHEST_WEIGHT,
                title=config[MilestoneType.HIGHEST_WEIGHT]["title"],
                description=config[MilestoneType.HIGHEST_WEIGHT]["description"],
                achieved_at=assessment_date,
                value=current_weight,
                previous_value=max_weight,
                icon=config[MilestoneType.HIGHEST_WEIGHT]["icon"]
            ))
        
        # Perda de 5kg (comparando com a primeira avaliação)
        first_weight = history[0].get("weight_kg") if history else None
        if first_weight and (first_weight - current_weight) >= 5.0:
            milestones.append(Milestone(
                milestone_type=MilestoneType.WEIGHT_LOSS_5KG,
                title=config[MilestoneType.WEIGHT_LOSS_5KG]["title"],
                description=config[MilestoneType.WEIGHT_LOSS_5KG]["description"],
                achieved_at=assessment_date,
                value=current_weight,
                previous_value=first_weight,
                icon=config[MilestoneType.WEIGHT_LOSS_5KG]["icon"]
            ))
        
        # Ganho de 5kg
        if first_weight and (current_weight - first_weight) >= 5.0:
            milestones.append(Milestone(
                milestone_type=MilestoneType.WEIGHT_GAIN_5KG,
                title=config[MilestoneType.WEIGHT_GAIN_5KG]["title"],
                description=config[MilestoneType.WEIGHT_GAIN_5KG]["description"],
                achieved_at=assessment_date,
                value=current_weight,
                previous_value=first_weight,
                icon=config[MilestoneType.WEIGHT_GAIN_5KG]["icon"]
            ))
        
        return milestones
    
    def _check_body_fat_milestones(
        self,
        current: Dict[str, Any],
        history: List[Dict[str, Any]]
    ) -> List[Milestone]:
        """Verifica milestones relacionados ao % de gordura corporal."""
        milestones = []
        current_bf = current.get("body_fat_percentage")
        config = self.MILESTONE_CONFIGS
        
        if current_bf is None:
            return milestones
        
        assessment_date = current.get("assessment_date", datetime.now())
        if isinstance(assessment_date, str):
            assessment_date = datetime.fromisoformat(assessment_date.replace('Z', '+00:00'))
        
        # Filtrar histórico com BF% válido
        history_with_bf = [h for h in history if h.get("body_fat_percentage") is not None]
        
        if not history_with_bf:
            return milestones
        
        # Menor BF%
        min_bf = min(h.get("body_fat_percentage", float('inf')) for h in history_with_bf)
        if current_bf < min_bf:
            milestones.append(Milestone(
                milestone_type=MilestoneType.LOWEST_BODY_FAT,
                title=config[MilestoneType.LOWEST_BODY_FAT]["title"],
                description=config[MilestoneType.LOWEST_BODY_FAT]["description"],
                achieved_at=assessment_date,
                value=current_bf,
                previous_value=min_bf,
                icon=config[MilestoneType.LOWEST_BODY_FAT]["icon"]
            ))
        
        # Maior BF%
        max_bf = max(h.get("body_fat_percentage", 0) for h in history_with_bf)
        if current_bf > max_bf:
            milestones.append(Milestone(
                milestone_type=MilestoneType.HIGHEST_BODY_FAT,
                title=config[MilestoneType.HIGHEST_BODY_FAT]["title"],
                description=config[MilestoneType.HIGHEST_BODY_FAT]["description"],
                achieved_at=assessment_date,
                value=current_bf,
                previous_value=max_bf,
                icon=config[MilestoneType.HIGHEST_BODY_FAT]["icon"]
            ))
        
        return milestones
    
    def _check_bmi_milestones(
        self,
        current: Dict[str, Any],
        history: List[Dict[str, Any]]
    ) -> List[Milestone]:
        """Verifica milestones relacionados ao BMI."""
        milestones = []
        current_bmi = current.get("bmi")
        config = self.MILESTONE_CONFIGS
        
        if current_bmi is None:
            return milestones
        
        assessment_date = current.get("assessment_date", datetime.now())
        if isinstance(assessment_date, str):
            assessment_date = datetime.fromisoformat(assessment_date.replace('Z', '+00:00'))
        
        # Filtrar histórico com BMI válido
        history_with_bmi = [h for h in history if h.get("bmi") is not None]
        
        if not history_with_bmi:
            return milestones
        
        # Verificar melhoria significativa de BMI (redução de pelo menos 1 ponto)
        first_bmi = history_with_bmi[0].get("bmi")
        if first_bmi and (first_bmi - current_bmi) >= 1.0:
            milestones.append(Milestone(
                milestone_type=MilestoneType.BMI_IMPROVEMENT,
                title=config[MilestoneType.BMI_IMPROVEMENT]["title"],
                description=config[MilestoneType.BMI_IMPROVEMENT]["description"],
                achieved_at=assessment_date,
                value=current_bmi,
                previous_value=first_bmi,
                icon=config[MilestoneType.BMI_IMPROVEMENT]["icon"]
            ))
        
        return milestones
    
    def _check_whr_milestones(
        self,
        current: Dict[str, Any],
        history: List[Dict[str, Any]]
    ) -> List[Milestone]:
        """Verifica milestones relacionados ao WHR."""
        milestones = []
        current_whr = current.get("whr")
        config = self.MILESTONE_CONFIGS
        
        if current_whr is None:
            return milestones
        
        assessment_date = current.get("assessment_date", datetime.now())
        if isinstance(assessment_date, str):
            assessment_date = datetime.fromisoformat(assessment_date.replace('Z', '+00:00'))
        
        # Filtrar histórico com WHR válido
        history_with_whr = [h for h in history if h.get("whr") is not None]
        
        if not history_with_whr:
            return milestones
        
        # Verificar melhoria de WHR (redução indica melhoria)
        first_whr = history_with_whr[0].get("whr")
        if first_whr and (first_whr - current_whr) >= 0.02:
            milestones.append(Milestone(
                milestone_type=MilestoneType.WHR_IMPROVEMENT,
                title=config[MilestoneType.WHR_IMPROVEMENT]["title"],
                description=config[MilestoneType.WHR_IMPROVEMENT]["description"],
                achieved_at=assessment_date,
                value=current_whr,
                previous_value=first_whr,
                icon=config[MilestoneType.WHR_IMPROVEMENT]["icon"]
            ))
        
        return milestones
    
    def _check_assessment_count_milestone(
        self,
        current: Dict[str, Any],
        history: List[Dict[str, Any]]
    ) -> List[Milestone]:
        """Verifica milestones relacionados à contagem de avaliações."""
        milestones = []
        config = self.MILESTONE_CONFIGS
        
        assessment_count = len(history) + 1  # +1 para avaliação atual
        
        # Marcos de contagem: 5, 10, 25, 50, 100
        milestones_counts = [5, 10, 25, 50, 100]
        
        if assessment_count in milestones_counts:
            assessment_date = current.get("assessment_date", datetime.now())
            if isinstance(assessment_date, str):
                assessment_date = datetime.fromisoformat(assessment_date.replace('Z', '+00:00'))
            
            milestones.append(Milestone(
                milestone_type=MilestoneType.ASSESSMENT_COUNT,
                title=config[MilestoneType.ASSESSMENT_COUNT]["title"].format(count=assessment_count),
                description=config[MilestoneType.ASSESSMENT_COUNT]["description"].format(count=assessment_count),
                achieved_at=assessment_date,
                value=float(assessment_count),
                icon=config[MilestoneType.ASSESSMENT_COUNT]["icon"]
            ))
        
        return milestones
