"""
Tag generation module.
Creates tags for the organization.
"""

import uuid
import random
import logging
from datetime import datetime
from typing import List, Tuple
from src.models.database import Database
from src.utils.dates import generate_created_at

logger = logging.getLogger(__name__)

# Realistic tag names for B2B SaaS
TAG_NAMES = [
    # Priority
    "high-priority", "low-priority", "urgent", "blocked",
    
    # Status
    "needs-review", "in-review", "ready", "on-hold",
    
    # Categories
    "bug", "feature", "enhancement", "documentation", "refactor",
    
    # Teams/Areas
    "frontend", "backend", "mobile", "infrastructure", "security",
    
    # Types
    "api", "ui", "database", "testing", "deployment",
    
    # Custom
    "customer-request", "internal", "external", "breaking-change"
]


class TagGenerator:
    """Generator for tags"""
    
    def __init__(self, db: Database, organization_id: str, date_range: Tuple[datetime, datetime]):
        """
        Initialize tag generator
        
        Args:
            db: Database connection
            organization_id: Organization ID
            date_range: (start_date, end_date) tuple
        """
        self.db = db
        self.organization_id = organization_id
        self.start_date, self.end_date = date_range
    
    def generate_tags(self, count: int = None) -> List[str]:
        """
        Generate tags for organization
        
        Args:
            count: Number of tags to generate (uses all available if None)
        
        Returns:
            List of tag IDs
        """
        if count is None:
            count = len(TAG_NAMES)
        else:
            count = min(count, len(TAG_NAMES))
        
        logger.info(f"Generating {count} tags...")
        
        tags_data = []
        tag_ids = []
        
        selected_names = random.sample(TAG_NAMES, count)
        
        colors = ['blue', 'green', 'orange', 'red', 'purple', 'pink', 'yellow', 'cyan', 'teal']
        
        for name in selected_names:
            tag_id = str(uuid.uuid4())
            color = random.choice(colors)
            created_at = generate_created_at(self.start_date, self.end_date, prefer_weekdays=True)
            
            tags_data.append((
                tag_id,
                self.organization_id,
                name,
                color,
                created_at.isoformat()
            ))
            
            tag_ids.append(tag_id)
        
        # Insert tags
        self._insert_tags(tags_data)
        
        logger.info(f"Generated {len(tag_ids)} tags")
        return tag_ids
    
    def assign_tags_to_tasks(self, task_ids: List[str], tag_ids: List[str], assignment_rate: float = 0.30):
        """
        Assign tags to tasks
        
        Args:
            task_ids: List of task IDs
            tag_ids: List of tag IDs
            assignment_rate: Probability of assigning a tag to a task
        """
        logger.info(f"Assigning tags to tasks...")
        
        associations_data = []
        
        for task_id in task_ids:
            # Each task gets 0-3 tags
            num_tags = random.randint(0, 3) if random.random() < assignment_rate else 0
            
            if num_tags > 0:
                selected_tags = random.sample(tag_ids, min(num_tags, len(tag_ids)))
                
                for tag_id in selected_tags:
                    association_id = str(uuid.uuid4())
                    created_at = generate_created_at(self.start_date, self.end_date, prefer_weekdays=True)
                    
                    associations_data.append((
                        association_id,
                        task_id,
                        tag_id,
                        created_at.isoformat()
                    ))
        
        # Insert associations
        if associations_data:
            self._insert_task_tags(associations_data)
            logger.info(f"Assigned tags to {len(set(t[1] for t in associations_data))} tasks")
    
    def _insert_tags(self, tags_data: List[tuple]):
        """Insert tags into database"""
        sql = """
            INSERT INTO tags (tag_id, organization_id, name, color, created_at)
            VALUES (?, ?, ?, ?, ?)
        """
        self.db.executemany(sql, tags_data)
        self.db.commit()
    
    def _insert_task_tags(self, associations_data: List[tuple]):
        """Insert task-tag associations into database"""
        sql = """
            INSERT INTO task_tags (association_id, task_id, tag_id, created_at)
            VALUES (?, ?, ?, ?)
        """
        self.db.executemany(sql, associations_data)
        self.db.commit()

