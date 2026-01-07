"""
Configuration management for Asana seed data generator.
Loads settings from environment variables with sensible defaults.
"""

import os
import logging
from dotenv import load_dotenv
from typing import Tuple

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class Config:
    """Application configuration"""
    
    # LLM Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
    LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'openai').lower()  # 'openai' or 'anthropic'
    LLM_TEMPERATURE = float(os.getenv('LLM_TEMPERATURE', '0.8'))
    LLM_MAX_TOKENS = int(os.getenv('LLM_MAX_TOKENS', '200'))
    
    # Database Configuration
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'output/asana_simulation.sqlite')
    
    # Generation Parameters (OPTIMIZED for FAST evaluation - still realistic)
    NUM_ORGANIZATIONS = int(os.getenv('NUM_ORGANIZATIONS', '1'))
    NUM_TEAMS_MIN = int(os.getenv('NUM_TEAMS_MIN', '3'))
    NUM_TEAMS_MAX = int(os.getenv('NUM_TEAMS_MAX', '5'))
    NUM_USERS_MIN = int(os.getenv('NUM_USERS_MIN', '50'))
    NUM_USERS_MAX = int(os.getenv('NUM_USERS_MAX', '100'))
    NUM_PROJECTS_MIN = int(os.getenv('NUM_PROJECTS_MIN', '5'))
    NUM_PROJECTS_MAX = int(os.getenv('NUM_PROJECTS_MAX', '10'))
    TASKS_PER_PROJECT_MIN = int(os.getenv('TASKS_PER_PROJECT_MIN', '5'))
    TASKS_PER_PROJECT_MAX = int(os.getenv('TASKS_PER_PROJECT_MAX', '10'))
    DATE_RANGE_MONTHS = int(os.getenv('DATE_RANGE_MONTHS', '6'))
    
    # Realistic Distribution Parameters
    # Task completion rates by project type (from Asana research)
    COMPLETION_RATE_SPRINT = 0.75  # 70-85% for sprint projects
    COMPLETION_RATE_BUG_TRACKING = 0.65  # 60-70% for bug tracking
    COMPLETION_RATE_ONGOING = 0.45  # 40-50% for ongoing projects
    
    # Due date distribution (research-based)
    DUE_DATE_WITHIN_WEEK = 0.25  # 25% within 1 week
    DUE_DATE_WITHIN_MONTH = 0.40  # 40% within 1 month
    DUE_DATE_1_3_MONTHS = 0.20  # 20% 1-3 months out
    DUE_DATE_NONE = 0.10  # 10% no due date
    DUE_DATE_OVERDUE = 0.05  # 5% overdue
    
    # Assignment rates
    UNASSIGNED_TASK_RATE = 0.15  # 15% of tasks unassigned
    
    # Team size distribution (industry benchmarks)
    TEAM_SIZE_MIN = 3
    TEAM_SIZE_MAX = 25
    TEAM_SIZE_MEAN = 8
    TEAM_SIZE_STD = 4
    
    # Project types and their distributions
    PROJECT_TYPES = {
        'engineering_sprint': 0.30,  # 30% engineering sprint projects
        'bug_tracking': 0.15,        # 15% bug tracking
        'marketing_campaign': 0.20,  # 20% marketing campaigns
        'product_roadmap': 0.15,     # 15% product roadmap
        'operations': 0.10,          # 10% operations
        'design': 0.10               # 10% design projects
    }
    
    # Section templates by project type
    SECTION_TEMPLATES = {
        'engineering_sprint': ['Backlog', 'To Do', 'In Progress', 'Code Review', 'Testing', 'Done'],
        'bug_tracking': ['New', 'Triaged', 'In Progress', 'Testing', 'Resolved', 'Closed'],
        'marketing_campaign': ['Planning', 'Content Creation', 'Design', 'Review', 'Published', 'Completed'],
        'product_roadmap': ['Discovery', 'Design', 'Development', 'Testing', 'Launch', 'Post-Launch'],
        'operations': ['Requested', 'In Progress', 'Blocked', 'Completed'],
        'design': ['Brief', 'Research', 'Design', 'Review', 'Handoff', 'Complete']
    }
    
    # Custom field types by project type
    CUSTOM_FIELD_TYPES = {
        'engineering_sprint': ['priority', 'effort', 'sprint'],
        'bug_tracking': ['severity', 'priority', 'reproducibility'],
        'marketing_campaign': ['channel', 'priority', 'status'],
        'product_roadmap': ['priority', 'effort', 'status'],
        'operations': ['priority', 'category'],
        'design': ['priority', 'status']
    }
    
    @classmethod
    def get_user_count_range(cls) -> Tuple[int, int]:
        """Get user count range"""
        return (cls.NUM_USERS_MIN, cls.NUM_USERS_MAX)
    
    @classmethod
    def get_team_count_range(cls) -> Tuple[int, int]:
        """Get team count range"""
        return (cls.NUM_TEAMS_MIN, cls.NUM_TEAMS_MAX)
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration"""
        # LLM is optional - generators will use fallback templates if LLM unavailable
        if cls.LLM_PROVIDER == 'openai' and not cls.OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY not set. LLM features will use fallback templates.")
        elif cls.LLM_PROVIDER == 'anthropic' and not cls.ANTHROPIC_API_KEY:
            logger.warning("ANTHROPIC_API_KEY not set. LLM features will use fallback templates.")
        return True

