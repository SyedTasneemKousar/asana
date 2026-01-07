"""
Statistical distribution utilities for realistic data generation.
Based on real-world benchmarks and research.
"""

import random
import numpy as np
from typing import List, Tuple


def truncated_normal(mean: float, std: float, min_val: float, max_val: float) -> float:
    """
    Generate value from truncated normal distribution
    
    Args:
        mean: Mean of distribution
        std: Standard deviation
        min_val: Minimum value
        max_val: Maximum value
    
    Returns:
        Sampled value
    """
    value = np.random.normal(mean, std)
    return max(min_val, min(max_val, value))


def sample_team_size(mean: float = 8, std: float = 4, min_size: int = 3, max_size: int = 25) -> int:
    """
    Sample team size from realistic distribution
    
    Based on industry benchmarks: average team size ~8, with std ~4
    
    Args:
        mean: Average team size
        std: Standard deviation
        min_size: Minimum team size
        max_size: Maximum team size
    
    Returns:
        Team size
    """
    size = int(truncated_normal(mean, std, min_size, max_size))
    return max(min_size, min(max_size, size))


def weighted_choice(choices: List[Tuple[str, float]]) -> str:
    """
    Choose from weighted list
    
    Args:
        choices: List of (value, weight) tuples
    
    Returns:
        Selected value
    """
    values, weights = zip(*choices)
    return random.choices(values, weights=weights)[0]


def sample_project_type() -> str:
    """
    Sample project type based on realistic distribution
    
    Returns:
        Project type string
    """
    from src.config import Config
    choices = [(pt, weight) for pt, weight in Config.PROJECT_TYPES.items()]
    return weighted_choice(choices)


def log_normal_cycle_time(mean_log: float = 1.5, std_log: float = 0.5, min_days: int = 1) -> int:
    """
    Generate cycle time (days to completion) using log-normal distribution
    
    Based on research: task completion times follow log-normal distribution
    
    Args:
        mean_log: Mean of log(cycle_time)
        std_log: Standard deviation of log(cycle_time)
        min_days: Minimum days
    
    Returns:
        Cycle time in days
    """
    log_time = np.random.normal(mean_log, std_log)
    cycle_time = max(min_days, int(np.exp(log_time)))
    return cycle_time

