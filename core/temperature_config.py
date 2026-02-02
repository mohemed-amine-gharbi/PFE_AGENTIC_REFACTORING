# core/temperature_config.py

class TemperatureConfig:
    """
    Configuration optimisée de la température pour chaque type d'agent.
    """
    
    OPTIMAL_TEMPERATURES = {
        "RenameAgent": {
            "default": 0.1,
            "description": "Renommage nécessite de la précision et de la cohérence",
            "range": (0.1, 0.3)
        },
        "ImportAgent": {
            "default": 0.2,
            "description": "Optimisation d'imports est une tâche mécanique",
            "range": (0.1, 0.4)
        },
        "ComplexityAgent": {
            "default": 0.4,
            "description": "Simplification algorithmique nécessite de la créativité",
            "range": (0.3, 0.6)
        },
        "DuplicationAgent": {
            "default": 0.5,
            "description": "Factorisation de code nécessite de l'innovation",
            "range": (0.4, 0.7)
        },
        "LongFunctionAgent": {
            "default": 0.3,
            "description": "Découpage de fonctions nécessite un bon équilibre",
            "range": (0.2, 0.5)
        }
    }
    
    @classmethod
    def get_temperature(cls, agent_name):
        """Retourne la température optimale pour un agent"""
        agent_config = cls.OPTIMAL_TEMPERATURES.get(agent_name, {})
        return agent_config.get("default", 0.3)
    
    @classmethod
    def get_all_configs(cls):
        """Retourne toutes les configurations"""
        return cls.OPTIMAL_TEMPERATURES