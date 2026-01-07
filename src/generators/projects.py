"""
Project generation module.
Creates projects with realistic names and types.
"""

import uuid
import random
import logging
from datetime import datetime
from typing import List, Tuple, Optional
from src.models.database import Database
from src.config import Config
from src.utils.dates import generate_created_at
from src.utils.distributions import sample_project_type

logger = logging.getLogger(__name__)

# Project name templates by type
PROJECT_NAME_TEMPLATES = {
    'engineering_sprint': [
        "Q1 2024 Sprint {n}", "Sprint {n} - Platform", "Engineering Sprint {n}",
        "Backend Services Sprint {n}", "Frontend Sprint {n}", "Infrastructure Sprint {n}"
    ],
    'bug_tracking': [
        "Bug Tracking - {month}", "Production Issues", "Critical Bugs",
        "Platform Bugs", "Customer Reported Issues"
    ],
    'marketing_campaign': [
        "Q{n} Marketing Campaign", "Product Launch Campaign", "Brand Awareness {year}",
        "Growth Campaign - {month}", "Content Marketing {quarter}"
    ],
    'product_roadmap': [
        "Product Roadmap {year}", "Feature Development {quarter}", "Platform Evolution",
        "Product Strategy {year}", "Innovation Pipeline"
    ],
    'operations': [
        "Operations {quarter}", "Process Improvement", "Infrastructure Updates",
        "Compliance {year}", "Internal Tools"
    ],
    'design': [
        "Design System", "UI/UX Improvements", "Design Sprint {n}",
        "User Experience {quarter}", "Visual Identity"
    ]
}


class ProjectGenerator:
    """Generator for projects"""
    
    def __init__(self, db: Database, organization_id: str, date_range: Tuple[datetime, datetime]):
        """
        Initialize project generator
        
        Args:
            db: Database connection
            organization_id: Organization ID
            date_range: (start_date, end_date) tuple
        """
        self.db = db
        self.organization_id = organization_id
        self.start_date, self.end_date = date_range
        self.project_counters = {pt: 1 for pt in Config.PROJECT_TYPES.keys()}
    
    def generate_projects(
        self,
        count: int,
        team_ids: List[str]
    ) -> List[Tuple[str, str, str]]:
        """
        Generate projects and insert into database
        
        Args:
            count: Number of projects to generate
            team_ids: Available team IDs (can be None)
        
        Returns:
            List of (project_id, project_type, team_id) tuples
        """
        logger.info(f"Generating {count} projects...")
        
        projects_data = []
        project_info = []
        
        for i in range(count):
            project_id = str(uuid.uuid4())
            project_type = sample_project_type()
            
            # Generate project name
            templates = PROJECT_NAME_TEMPLATES.get(project_type, ["Project {n}"])
            template = random.choice(templates)
            name = template.format(
                n=self.project_counters[project_type],
                month=random.choice(["January", "February", "March", "April", "May", "June"]),
                year=2024,
                quarter=random.choice(["Q1", "Q2", "Q3", "Q4"])
            )
            self.project_counters[project_type] += 1
            
            # Assign to team (80% have teams, 20% organization-level)
            team_id = None
            if team_ids and random.random() < 0.80:
                team_id = random.choice(team_ids)
            
            # Generate description (60% have descriptions)
            description = None
            if random.random() < 0.60:
                description = f"Project for {project_type.replace('_', ' ')}"
            
            # Project color
            colors = ['blue', 'green', 'orange', 'red', 'purple', 'pink', 'yellow', 'cyan', 'teal', 'brown']
            color = random.choice(colors)
            
            # Public/private (10% public)
            is_public = random.random() < 0.10
            
            # Archived (5% archived)
            archived = random.random() < 0.05
            
            created_at = generate_created_at(
                self.start_date,
                self.end_date,
                prefer_weekdays=True
            )
            
            # Modified at is same or later than created_at
            modified_at = generate_created_at(created_at, self.end_date, prefer_weekdays=True)
            
            projects_data.append((
                project_id,
                self.organization_id,
                team_id,
                name,
                description,
                color,
                1 if is_public else 0,
                1 if archived else 0,
                created_at.isoformat(),
                modified_at.isoformat()
            ))
            
            project_info.append((project_id, project_type, team_id))
        
        # Insert projects
        self._insert_projects(projects_data)
        
        logger.info(f"Generated {len(projects_data)} projects")
        return project_info
    
    def _insert_projects(self, projects_data: List[tuple]):
        """Insert projects into database"""
        sql = """
            INSERT INTO projects (
                project_id, organization_id, team_id, name, description,
                color, is_public, archived, created_at, modified_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.db.executemany(sql, projects_data)
        self.db.commit()

