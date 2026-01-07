"""
Section generation module.
Creates sections within projects based on project type.
"""

import uuid
import logging
from typing import List, Tuple
from src.models.database import Database
from src.config import Config
from src.utils.dates import generate_created_at

logger = logging.getLogger(__name__)


class SectionGenerator:
    """Generator for sections"""
    
    def __init__(self, db: Database, date_range: Tuple):
        """
        Initialize section generator
        
        Args:
            db: Database connection
            date_range: (start_date, end_date) tuple
        """
        self.db = db
        self.start_date, self.end_date = date_range
    
    def generate_sections(
        self,
        project_id: str,
        project_type: str,
        project_created_at: str
    ) -> List[str]:
        """
        Generate sections for a project
        
        Args:
            project_id: Project ID
            project_type: Type of project
            project_created_at: Project creation timestamp
        
        Returns:
            List of section IDs
        """
        # Get section template for project type
        section_names = Config.SECTION_TEMPLATES.get(
            project_type,
            ['To Do', 'In Progress', 'Done']
        )
        
        sections_data = []
        section_ids = []
        
        for position, section_name in enumerate(section_names):
            section_id = str(uuid.uuid4())
            
            # Section created at same time or slightly after project
            from datetime import datetime
            project_dt = datetime.fromisoformat(project_created_at)
            created_at = generate_created_at(project_dt, self.end_date, prefer_weekdays=True)
            
            sections_data.append((
                section_id,
                project_id,
                section_name,
                position,
                created_at.isoformat()
            ))
            
            section_ids.append(section_id)
        
        # Insert sections
        self._insert_sections(sections_data)
        
        return section_ids
    
    def _insert_sections(self, sections_data: List[tuple]):
        """Insert sections into database"""
        sql = """
            INSERT INTO sections (section_id, project_id, name, position, created_at)
            VALUES (?, ?, ?, ?, ?)
        """
        self.db.executemany(sql, sections_data)
        self.db.commit()

