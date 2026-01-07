"""
Comment generation module.
Creates realistic comments/stories on tasks.
"""

import uuid
import random
import logging
from datetime import datetime
from typing import List, Tuple
from src.models.database import Database
from src.utils.dates import generate_created_at
from src.utils.llm import get_llm_generator
from pathlib import Path

logger = logging.getLogger(__name__)


class CommentGenerator:
    """Generator for comments"""
    
    def __init__(self, db: Database, date_range: Tuple[datetime, datetime]):
        """
        Initialize comment generator
        
        Args:
            db: Database connection
            date_range: (start_date, end_date) tuple
        """
        self.db = db
        self.start_date, self.end_date = date_range
        self.llm = get_llm_generator()
        self._load_comment_templates()
    
    def _load_comment_templates(self):
        """Load comment templates"""
        prompts_file = Path(__file__).parent.parent.parent / "prompts" / "comments.txt"
        if prompts_file.exists():
            with open(prompts_file, 'r') as f:
                content = f.read()
                # Extract comment types (simplified)
                self.comment_templates = [
                    "Starting work on this now",
                    "Making good progress",
                    "This is complete and ready for review",
                    "Can someone clarify the requirements?",
                    "Looks good!",
                    "Thanks for the update!",
                    "Updated based on feedback",
                ]
        else:
            self.comment_templates = [
                "Working on this",
                "Update: making progress",
                "Completed",
                "Need clarification",
                "Looks good"
            ]
    
    def generate_comment_text(self, task_name: str, task_completed: bool) -> str:
        """
        Generate realistic comment text
        
        Args:
            task_name: Name of the task
            task_completed: Whether task is completed
        
        Returns:
            Comment text
        """
        # 70% use templates, 30% use LLM
        if random.random() < 0.70:
            template = random.choice(self.comment_templates)
            return template
        else:
            try:
                comment_type = "completion update" if task_completed else "progress update"
                prompt = f"Generate a brief, realistic comment (1-2 sentences) for a task management system. Task: {task_name}. Comment type: {comment_type}. Be conversational and professional."
                comment = self.llm.generate(prompt)
                return comment[:500] if comment else random.choice(self.comment_templates)
            except:
                return random.choice(self.comment_templates)
    
    def generate_comments(
        self,
        task_id: str,
        task_created_at: str,
        task_completed_at: str,
        task_name: str,
        task_completed: bool,
        user_ids: List[str],
        num_comments: int = None
    ) -> List[str]:
        """
        Generate comments for a task
        
        Args:
            task_id: Task ID
            task_created_at: Task creation timestamp
            task_completed_at: Task completion timestamp (if completed)
            task_name: Task name
            task_completed: Whether task is completed
            user_ids: Available user IDs
            num_comments: Number of comments (auto-calculated if None)
        
        Returns:
            List of comment IDs
        """
        if num_comments is None:
            # 40% of tasks have comments, 1-5 comments per task
            if random.random() > 0.40:
                return []
            num_comments = random.randint(1, 5)
        
        if num_comments == 0:
            return []
        
        comments_data = []
        comment_ids = []
        
        task_dt = datetime.fromisoformat(task_created_at)
        end_dt = datetime.fromisoformat(task_completed_at) if task_completed_at else self.end_date
        
        for i in range(num_comments):
            comment_id = str(uuid.uuid4())
            
            # Comment author (random user)
            user_id = random.choice(user_ids) if user_ids else None
            if not user_id:
                continue
            
            # Comment text
            text = self.generate_comment_text(task_name, task_completed and i == num_comments - 1)
            
            # Created at (between task creation and completion/now)
            created_at = generate_created_at(task_dt, end_dt, prefer_weekdays=True)
            
            comments_data.append((
                comment_id,
                task_id,
                user_id,
                text,
                created_at.isoformat()
            ))
            
            comment_ids.append(comment_id)
        
        # Insert comments
        if comments_data:
            self._insert_comments(comments_data)
        
        return comment_ids
    
    def _insert_comments(self, comments_data: List[tuple]):
        """Insert comments into database"""
        sql = """
            INSERT INTO comments (comment_id, task_id, user_id, text, created_at)
            VALUES (?, ?, ?, ?, ?)
        """
        self.db.executemany(sql, comments_data)
        self.db.commit()

