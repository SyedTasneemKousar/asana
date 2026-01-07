"""
Task generation module.
Creates realistic tasks with proper assignments, due dates, and descriptions.
"""

import uuid
import random
import logging
from datetime import datetime, date
from typing import List, Tuple, Optional, Dict
from src.models.database import Database
from src.config import Config
from src.utils.dates import generate_created_at, generate_due_date, generate_completed_at
from src.utils.llm import get_llm_generator
from pathlib import Path

logger = logging.getLogger(__name__)


class TaskGenerator:
    """Generator for tasks"""
    
    def __init__(self, db: Database, date_range: Tuple[datetime, datetime]):
        """
        Initialize task generator
        
        Args:
            db: Database connection
            date_range: (start_date, end_date) tuple
        """
        self.db = db
        self.start_date, self.end_date = date_range
        self.llm = get_llm_generator()
        self._load_prompts()
    
    def _load_prompts(self):
        """Load LLM prompt templates"""
        prompts_dir = Path(__file__).parent.parent.parent / "prompts"
        
        # Load task name templates
        task_names_file = prompts_dir / "task_names.txt"
        if task_names_file.exists():
            with open(task_names_file, 'r') as f:
                self.task_name_prompts = f.read()
        else:
            self.task_name_prompts = "Generate a realistic task name for a {project_type} project."
        
        # Load task description templates
        task_desc_file = prompts_dir / "task_descriptions.txt"
        if task_desc_file.exists():
            with open(task_desc_file, 'r') as f:
                self.task_desc_prompts = f.read()
        else:
            self.task_desc_prompts = "Generate a realistic task description."
    
    def generate_task_name(self, project_type: str) -> str:
        """
        Generate realistic task name using LLM or fallback
        
        Args:
            project_type: Type of project
        
        Returns:
            Task name string
        """
        try:
            # Use LLM for realistic names (with caching/fallback)
            prompt = f"Generate a single, concise task name (max 60 chars) for a {project_type.replace('_', ' ')} project. Return only the task name, no explanation."
            name = self.llm.generate(prompt)
            # Clean up and truncate
            name = name.strip().strip('"').strip("'")
            if len(name) > 60:
                name = name[:57] + "..."
            return name if name else self._fallback_task_name(project_type)
        except Exception as e:
            logger.debug(f"LLM task name generation failed: {e}")
            return self._fallback_task_name(project_type)
    
    def _fallback_task_name(self, project_type: str) -> str:
        """Fallback task name generation"""
        templates = {
            'engineering_sprint': [
                "Implement {feature}", "Fix bug in {component}", "Refactor {module}",
                "Add {feature} to {component}", "Optimize {component}", "Update {component}"
            ],
            'bug_tracking': [
                "Fix {issue} in {component}", "Resolve {problem}", "Patch {vulnerability}",
                "Fix crash on {scenario}", "Resolve data issue"
            ],
            'marketing_campaign': [
                "Create {content} for {campaign}", "Design {asset}", "Write {content_type}",
                "Schedule {activity}", "Analyze {metric}"
            ],
            'product_roadmap': [
                "Research {feature}", "Design {feature}", "Plan {feature}",
                "Document {feature}", "Validate {feature}"
            ],
            'operations': [
                "Update {process}", "Review {policy}", "Process {request}",
                "Audit {system}", "Implement {improvement}"
            ],
            'design': [
                "Design {element}", "Create {asset}", "Update {component} design",
                "Refine {element}", "Create design system {part}"
            ]
        }
        
        template = random.choice(templates.get(project_type, ["Complete {task}"]))
        components = ["API", "UI", "backend", "frontend", "database", "service", "module"]
        features = ["authentication", "dashboard", "reporting", "integration", "analytics"]
        
        return template.format(
            feature=random.choice(features),
            component=random.choice(components),
            issue="performance issue",
            problem="data sync",
            vulnerability="security",
            scenario="login",
            content="blog post",
            campaign="Q1 launch",
            asset="landing page",
            content_type="email",
            activity="social posts",
            metric="campaign performance",
            process="onboarding",
            policy="security policy",
            request="access request",
            system="billing",
            improvement="workflow",
            element="user interface",
            part="component"
        )
    
    def generate_task_description(self, task_name: str, project_type: str) -> Optional[str]:
        """
        Generate realistic task description
        
        Args:
            task_name: Name of the task
            project_type: Type of project
        
        Returns:
            Description string or None
        """
        # 20% empty, 50% short (1-3 sentences), 30% detailed
        rand = random.random()
        
        if rand < 0.20:
            return None
        elif rand < 0.70:
            # Short description
            try:
                prompt = f"Generate a brief 1-2 sentence description for this task: {task_name} (project type: {project_type})."
                desc = self.llm.generate(prompt)
                return desc[:200] if desc else None
            except:
                return f"Task: {task_name}"
        else:
            # Detailed description
            try:
                prompt = f"Generate a detailed task description (3-5 sentences with bullet points) for: {task_name} (project type: {project_type}). Include context, requirements, and acceptance criteria."
                desc = self.llm.generate(prompt)
                return desc[:1000] if desc else f"Detailed task: {task_name}"
            except:
                return f"Task: {task_name}\n\nRequirements:\n- Complete implementation\n- Add tests\n- Update documentation"
    
    def generate_tasks(
        self,
        project_id: str,
        project_type: str,
        section_ids: List[str],
        user_ids: List[str],
        project_created_at: str,
        num_tasks: int = None
    ) -> List[str]:
        """
        Generate tasks for a project
        
        Args:
            project_id: Project ID
            project_type: Type of project
            section_ids: Available section IDs
            user_ids: Available user IDs for assignment
            project_created_at: Project creation timestamp
            num_tasks: Number of tasks to generate (auto-calculated if None)
        
        Returns:
            List of task IDs
        """
        if num_tasks is None:
            # Realistic task count per project: use config values
            num_tasks = random.randint(Config.TASKS_PER_PROJECT_MIN, Config.TASKS_PER_PROJECT_MAX)
        
        logger.info(f"Generating {num_tasks} tasks for project {project_id}...")
        
        tasks_data = []
        task_ids = []
        
        # Get completion rate for project type
        completion_rate = {
            'engineering_sprint': Config.COMPLETION_RATE_SPRINT,
            'bug_tracking': Config.COMPLETION_RATE_BUG_TRACKING,
            'marketing_campaign': 0.70,
            'product_roadmap': 0.60,
            'operations': 0.65,
            'design': 0.70
        }.get(project_type, 0.65)
        
        project_dt = datetime.fromisoformat(project_created_at)
        
        for i in range(num_tasks):
            task_id = str(uuid.uuid4())
            
            # Generate task name
            task_name = self.generate_task_name(project_type)
            
            # Generate description
            description = self.generate_task_description(task_name, project_type)
            
            # Assign to section (distribute across sections)
            section_id = random.choice(section_ids) if section_ids else None
            
            # Assignee (15% unassigned)
            assignee_id = None
            if user_ids and random.random() > Config.UNASSIGNED_TASK_RATE:
                assignee_id = random.choice(user_ids)
            
            # Created at (after project creation)
            created_at = generate_created_at(project_dt, self.end_date, prefer_weekdays=True)
            
            # Due date
            due_date = generate_due_date(created_at, project_type)
            
            # Completion
            completed = random.random() < completion_rate
            completed_at = None
            if completed:
                completed_at = generate_completed_at(created_at, due_date, completion_rate)
            
            # Modified at (same or after created_at, before or at completed_at if completed)
            if completed_at:
                modified_at = generate_created_at(created_at, completed_at, prefer_weekdays=True)
            else:
                modified_at = generate_created_at(created_at, self.end_date, prefer_weekdays=True)
            
            tasks_data.append((
                task_id,
                project_id,
                section_id,
                task_name,
                description,
                assignee_id,
                due_date.isoformat() if due_date else None,
                due_date.isoformat() if due_date else None,  # due_on (same as due_date)
                1 if completed else 0,
                completed_at.isoformat() if completed_at else None,
                created_at.isoformat(),
                modified_at.isoformat(),
                None,  # parent_task_id (for subtasks, handled separately)
                0,  # num_subtasks
                0   # num_completed_subtasks
            ))
            
            task_ids.append(task_id)
            
            # Batch insert every 50 tasks
            if len(tasks_data) >= 50:
                self._insert_tasks(tasks_data)
                tasks_data = []
        
        # Insert remaining tasks
        if tasks_data:
            self._insert_tasks(tasks_data)
        
        logger.info(f"Generated {len(task_ids)} tasks")
        return task_ids
    
    def _insert_tasks(self, tasks_data: List[tuple]):
        """Insert tasks into database"""
        sql = """
            INSERT INTO tasks (
                task_id, project_id, section_id, name, description,
                assignee_id, due_date, due_on, completed, completed_at,
                created_at, modified_at, parent_task_id, num_subtasks, num_completed_subtasks
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.db.executemany(sql, tasks_data)
        self.db.commit()

