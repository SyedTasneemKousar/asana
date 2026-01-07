"""
Subtask generation module.
Creates subtasks for parent tasks.
"""

import uuid
import random
import logging
from datetime import datetime
from typing import List, Tuple
from src.models.database import Database
from src.utils.dates import generate_created_at, generate_due_date, generate_completed_at

logger = logging.getLogger(__name__)


class SubtaskGenerator:
    """Generator for subtasks"""
    
    def __init__(self, db: Database, date_range: Tuple[datetime, datetime]):
        """
        Initialize subtask generator
        
        Args:
            db: Database connection
            date_range: (start_date, end_date) tuple
        """
        self.db = db
        self.start_date, self.end_date = date_range
    
    def generate_subtasks(
        self,
        parent_task_id: str,
        parent_created_at: str,
        parent_due_date: str,
        parent_completed: bool,
        parent_completed_at: str,
        assignee_id: str = None,
        num_subtasks: int = None
    ) -> List[str]:
        """Generate subtasks - handles empty parent_due_date gracefully"""
        """
        Generate subtasks for a parent task
        
        Args:
            parent_task_id: Parent task ID
            parent_created_at: Parent task creation timestamp
            parent_due_date: Parent task due date
            parent_completed: Whether parent is completed
            parent_completed_at: Parent task completion timestamp
            assignee_id: Assignee (inherited from parent if None)
            num_subtasks: Number of subtasks (auto-calculated if None)
        
        Returns:
            List of subtask IDs
        """
        if num_subtasks is None:
            # 30% of tasks have subtasks, 1-5 subtasks per task
            if random.random() > 0.30:
                return []
            num_subtasks = random.randint(1, 5)
        
        if num_subtasks == 0:
            return []
        
        logger.debug(f"Generating {num_subtasks} subtasks for task {parent_task_id}...")
        
        subtasks_data = []
        subtask_ids = []
        
        parent_dt = datetime.fromisoformat(parent_created_at)
        # Handle empty string or None for parent_due_date
        if parent_due_date and parent_due_date != "":
            try:
                parent_due = datetime.fromisoformat(parent_due_date).date()
            except (ValueError, AttributeError):
                parent_due = None
        else:
            parent_due = None
        
        # Subtask name templates
        subtask_templates = [
            "Review {component}",
            "Test {feature}",
            "Update {documentation}",
            "Verify {requirement}",
            "Implement {part}",
            "Fix {issue}",
            "Refactor {component}",
            "Document {feature}"
        ]
        
        components = ["code", "design", "API", "UI", "tests", "documentation"]
        features = ["functionality", "integration", "authentication", "dashboard"]
        
        for i in range(num_subtasks):
            subtask_id = str(uuid.uuid4())
            
            # Generate subtask name
            template = random.choice(subtask_templates)
            name = template.format(
                component=random.choice(components),
                feature=random.choice(features),
                documentation="docs",
                requirement="requirements",
                part="component",
                issue="bug"
            )
            
            # Description (50% have descriptions)
            description = None
            if random.random() < 0.50:
                description = f"Subtask: {name}"
            
            # Created at (same or slightly after parent)
            created_at = generate_created_at(parent_dt, self.end_date, prefer_weekdays=True)
            
            # Due date (before or same as parent due date)
            due_date = None
            if parent_due and parent_due != "":
                try:
                    # Subtask due date is before parent due date
                    from datetime import timedelta, date
                    # Parse parent_due if it's a string
                    if isinstance(parent_due, str):
                        parent_due_obj = date.fromisoformat(parent_due)
                    else:
                        parent_due_obj = parent_due
                    days_before = random.randint(0, 7)
                    due_date = parent_due_obj - timedelta(days=days_before)
                    # Ensure it's a date object (not datetime)
                    if isinstance(due_date, datetime):
                        due_date = due_date.date()
                except Exception as e:
                    logger.debug(f"Error parsing parent due date: {e}, using generated date")
                    due_date = generate_due_date(created_at, "engineering_sprint")
            else:
                due_date = generate_due_date(created_at, "engineering_sprint")
            
            # Completion (higher rate if parent completed)
            completion_rate = 0.90 if parent_completed else 0.70
            completed = random.random() < completion_rate
            completed_at = None
            
            if completed:
                # Completed before or at parent completion
                if parent_completed and parent_completed_at:
                    parent_completed_dt = datetime.fromisoformat(parent_completed_at)
                    completed_at = generate_created_at(created_at, parent_completed_dt, prefer_weekdays=True)
                else:
                    completed_at = generate_completed_at(created_at, due_date, completion_rate)
            
            # Modified at
            if completed_at:
                modified_at = generate_created_at(created_at, completed_at, prefer_weekdays=True)
            else:
                modified_at = generate_created_at(created_at, self.end_date, prefer_weekdays=True)
            
            subtasks_data.append((
                subtask_id,
                None,  # project_id (inherited from parent, but we'll update)
                None,  # section_id
                name,
                description,
                assignee_id,  # Same as parent
                due_date.isoformat() if due_date else None,
                due_date.isoformat() if due_date else None,
                1 if completed else 0,
                completed_at.isoformat() if completed_at else None,
                created_at.isoformat(),
                modified_at.isoformat(),
                parent_task_id,
                0,  # num_subtasks (subtasks don't have subtasks)
                0   # num_completed_subtasks
            ))
            
            subtask_ids.append(subtask_id)
        
        # Get parent task's project_id and section_id
        cursor = self.db.execute(
            "SELECT project_id, section_id FROM tasks WHERE task_id = ?",
            (parent_task_id,)
        )
        parent_info = cursor.fetchone()
        
        if parent_info:
            project_id, section_id = parent_info
            
            # Update subtasks with project and section
            updated_data = []
            for subtask_data in subtasks_data:
                updated_data.append((
                    subtask_data[0],  # task_id
                    project_id,  # project_id
                    section_id,  # section_id
                    *subtask_data[3:]  # rest of fields
                ))
            
            # Insert subtasks
            self._insert_subtasks(updated_data)
            
            # Update parent task's subtask counts
            num_completed = sum(1 for s in subtasks_data if s[8] == 1)
            self.db.execute(
                """
                UPDATE tasks 
                SET num_subtasks = ?, num_completed_subtasks = ?
                WHERE task_id = ?
                """,
                (num_subtasks, num_completed, parent_task_id)
            )
            self.db.commit()
        
        return subtask_ids
    
    def _insert_subtasks(self, subtasks_data: List[tuple]):
        """Insert subtasks into database"""
        sql = """
            INSERT INTO tasks (
                task_id, project_id, section_id, name, description,
                assignee_id, due_date, due_on, completed, completed_at,
                created_at, modified_at, parent_task_id, num_subtasks, num_completed_subtasks
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.db.executemany(sql, subtasks_data)
        self.db.commit()

