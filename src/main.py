"""
Main orchestration script for Asana seed data generation.
Coordinates all generators to create a complete, realistic dataset.
"""

import logging
import random
import uuid
from datetime import datetime
from pathlib import Path
from tqdm import tqdm

from src.config import Config
from src.models.database import Database
from src.scrapers.companies import get_company_name, get_company_domain
from src.generators.users import UserGenerator
from src.generators.teams import TeamGenerator
from src.generators.projects import ProjectGenerator
from src.generators.sections import SectionGenerator
from src.generators.tasks import TaskGenerator
from src.generators.subtasks import SubtaskGenerator
from src.generators.comments import CommentGenerator
from src.generators.tags import TagGenerator
from src.generators.custom_fields import CustomFieldGenerator
from src.utils.dates import get_date_range, generate_created_at

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AsanaDataGenerator:
    """Main data generator orchestrator"""
    
    def __init__(self):
        """Initialize generator"""
        # Validate configuration
        Config.validate()
        
        # Initialize database
        self.db = Database(Config.DATABASE_PATH)
        self.db.initialize_schema()
        
        # Get date range
        self.date_range = get_date_range(Config.DATE_RANGE_MONTHS)
        logger.info(f"Date range: {self.date_range[0]} to {self.date_range[1]}")
        
        # Storage for generated IDs
        self.organization_id = None
        self.user_ids = []
        self.team_ids = []
        self.project_info = []  # List of (project_id, project_type, team_id)
        self.tag_ids = []
    
    def generate_organizations(self):
        """Generate organizations/workspaces"""
        logger.info("=" * 60)
        logger.info("Generating Organizations")
        logger.info("=" * 60)
        
        # Check if organizations already exist
        cursor = self.db.execute("SELECT COUNT(*) FROM organizations")
        existing_count = cursor.fetchone()[0]
        
        if existing_count > 0:
            logger.info(f"Found {existing_count} existing organization(s), reusing...")
            cursor = self.db.execute("SELECT organization_id FROM organizations LIMIT 1")
            result = cursor.fetchone()
            if result:
                self.organization_id = result[0]
            return self.organization_id
        
        org_data = []
        generated_names = set()
        
        for i in range(Config.NUM_ORGANIZATIONS):
            org_id = str(uuid.uuid4())
            # Ensure unique organization name
            max_attempts = 20
            name = None
            for attempt in range(max_attempts):
                candidate_name = get_company_name()
                if candidate_name not in generated_names:
                    name = candidate_name
                    generated_names.add(name)
                    break
            if name is None:
                name = f"Organization {i+1}"
            
            domain = get_company_domain(name)
            created_at = generate_created_at(
                self.date_range[0],
                self.date_range[1],
                prefer_weekdays=True
            )
            
            org_data.append((
                org_id,
                name,
                domain,
                created_at.isoformat(),
                1  # is_organization
            ))
            
            self.organization_id = org_id
        
        # Insert organizations
        sql = """
            INSERT INTO organizations (organization_id, name, domain, created_at, is_organization)
            VALUES (?, ?, ?, ?, ?)
        """
        self.db.executemany(sql, org_data)
        self.db.commit()
        
        logger.info(f"Generated {len(org_data)} organization(s)")
        return self.organization_id
    
    def generate_users(self):
        """Generate users"""
        logger.info("=" * 60)
        logger.info("Generating Users")
        logger.info("=" * 60)
        
        # Get user count
        user_count = random.randint(Config.NUM_USERS_MIN, Config.NUM_USERS_MAX)
        
        # Get organization domain
        cursor = self.db.execute(
            "SELECT domain FROM organizations WHERE organization_id = ?",
            (self.organization_id,)
        )
        org_info = cursor.fetchone()
        domain = org_info[0] if org_info else "company.com"
        
        # Generate users
        user_gen = UserGenerator(self.db, self.organization_id, self.date_range)
        user_gen.set_domain(domain)
        self.user_ids = user_gen.generate_users(user_count)
        
        return self.user_ids
    
    def generate_teams(self):
        """Generate teams"""
        logger.info("=" * 60)
        logger.info("Generating Teams")
        logger.info("=" * 60)
        
        team_count = random.randint(Config.NUM_TEAMS_MIN, Config.NUM_TEAMS_MAX)
        
        team_gen = TeamGenerator(self.db, self.organization_id, self.date_range)
        team_results = team_gen.generate_teams(team_count, self.user_ids)
        
        # Extract team IDs
        self.team_ids = [team_id for team_id, _ in team_results]
        
        logger.info(f"Generated {len(self.team_ids)} teams")
        return self.team_ids
    
    def generate_projects(self):
        """Generate projects"""
        logger.info("=" * 60)
        logger.info("Generating Projects")
        logger.info("=" * 60)
        
        # Generate projects based on config (optimized for fast evaluation)
        project_count = random.randint(Config.NUM_PROJECTS_MIN, Config.NUM_PROJECTS_MAX)
        
        project_gen = ProjectGenerator(self.db, self.organization_id, self.date_range)
        self.project_info = project_gen.generate_projects(project_count, self.team_ids)
        
        logger.info(f"Generated {len(self.project_info)} projects")
        return self.project_info
    
    def generate_sections(self):
        """Generate sections for all projects"""
        logger.info("=" * 60)
        logger.info("Generating Sections")
        logger.info("=" * 60)
        
        section_gen = SectionGenerator(self.db, self.date_range)
        project_sections = {}  # project_id -> [section_ids]
        
        for project_id, project_type, team_id in tqdm(self.project_info, desc="Sections"):
            # Get project created_at
            cursor = self.db.execute(
                "SELECT created_at FROM projects WHERE project_id = ?",
                (project_id,)
            )
            result = cursor.fetchone()
            project_created_at = result[0] if result else self.date_range[0].isoformat()
            
            section_ids = section_gen.generate_sections(project_id, project_type, project_created_at)
            project_sections[project_id] = section_ids
        
        logger.info(f"Generated sections for {len(project_sections)} projects")
        return project_sections
    
    def generate_tasks(self, project_sections: dict):
        """Generate tasks for all projects"""
        logger.info("=" * 60)
        logger.info("Generating Tasks")
        logger.info("=" * 60)
        
        task_gen = TaskGenerator(self.db, self.date_range)
        subtask_gen = SubtaskGenerator(self.db, self.date_range)
        comment_gen = CommentGenerator(self.db, self.date_range)
        custom_field_gen = CustomFieldGenerator(self.db, self.date_range)
        
        all_task_ids = []
        project_tasks = {}  # project_id -> [task_ids]
        
        for project_id, project_type, team_id in tqdm(self.project_info, desc="Tasks"):
            try:
                section_ids = project_sections.get(project_id, [])
                
                # Get team members for assignment
                if team_id:
                    cursor = self.db.execute(
                        "SELECT user_id FROM team_memberships WHERE team_id = ?",
                        (team_id,)
                    )
                    team_user_ids = [row[0] for row in cursor.fetchall()]
                else:
                    team_user_ids = self.user_ids
                
                # Get project created_at
                cursor = self.db.execute(
                    "SELECT created_at FROM projects WHERE project_id = ?",
                    (project_id,)
                )
                result = cursor.fetchone()
                project_created_at = result[0] if result else self.date_range[0].isoformat()
                
                # Generate tasks
                try:
                    task_ids = task_gen.generate_tasks(
                        project_id,
                        project_type,
                        section_ids,
                        team_user_ids,
                        project_created_at
                    )
                    
                    project_tasks[project_id] = task_ids
                    all_task_ids.extend(task_ids)
                except Exception as e:
                    logger.error(f"Error generating tasks for project {project_id}: {e}")
                    continue  # Skip this project and continue
            except Exception as e:
                logger.error(f"Error processing project {project_id}: {e}")
                continue  # Skip this project and continue
            
            # Generate custom fields for project
            field_ids = custom_field_gen.generate_custom_fields(
                project_id,
                project_type,
                project_created_at
            )
            
            # Generate subtasks, comments, and custom field values for each task
            for task_id in task_ids:
                try:
                    # Get task info
                    cursor = self.db.execute(
                        """
                        SELECT created_at, due_date, completed, completed_at, name, assignee_id
                        FROM tasks WHERE task_id = ?
                        """,
                        (task_id,)
                    )
                    task_info = cursor.fetchone()
                    
                    if task_info:
                        task_created_at, task_due_date, task_completed, task_completed_at, task_name, assignee_id = task_info
                        
                        # Generate subtasks (30% of tasks have subtasks)
                        try:
                            if random.random() < 0.30:
                                subtask_gen.generate_subtasks(
                                    task_id,
                                    task_created_at,
                                    task_due_date or "",
                                    bool(task_completed),
                                    task_completed_at or "",
                                    assignee_id
                                )
                        except Exception as e:
                            logger.warning(f"Error generating subtasks for task {task_id}: {e}")
                        
                        # Generate comments
                        try:
                            comment_gen.generate_comments(
                                task_id,
                                task_created_at,
                                task_completed_at or "",
                                task_name,
                                bool(task_completed),
                                team_user_ids
                            )
                        except Exception as e:
                            logger.warning(f"Error generating comments for task {task_id}: {e}")
                        
                        # Assign custom field values
                        try:
                            if field_ids:
                                field_types = {}
                                for field_id in field_ids:
                                    cursor = self.db.execute(
                                        "SELECT type FROM custom_field_definitions WHERE field_id = ?",
                                        (field_id,)
                                    )
                                    result = cursor.fetchone()
                                    field_types[field_id] = result[0] if result else 'text'
                                
                                custom_field_gen.assign_custom_field_values(
                                    task_id,
                                    field_ids,
                                    field_types
                                )
                        except Exception as e:
                            logger.warning(f"Error assigning custom fields for task {task_id}: {e}")
                except Exception as e:
                    logger.warning(f"Error processing task {task_id}: {e}")
                    continue  # Continue with next task
        
        logger.info(f"Generated {len(all_task_ids)} tasks")
        return all_task_ids
    
    def generate_tags(self):
        """Generate tags"""
        logger.info("=" * 60)
        logger.info("Generating Tags")
        logger.info("=" * 60)
        
        tag_gen = TagGenerator(self.db, self.organization_id, self.date_range)
        self.tag_ids = tag_gen.generate_tags()
        
        return self.tag_ids
    
    def assign_tags_to_tasks(self, task_ids: list):
        """Assign tags to tasks"""
        logger.info("=" * 60)
        logger.info("Assigning Tags to Tasks")
        logger.info("=" * 60)
        
        tag_gen = TagGenerator(self.db, self.organization_id, self.date_range)
        tag_gen.assign_tags_to_tasks(task_ids, self.tag_ids, assignment_rate=0.30)
    
    def generate_all(self):
        """Generate complete dataset"""
        logger.info("Starting Asana seed data generation...")
        logger.info(f"Configuration:")
        logger.info(f"  - Organizations: {Config.NUM_ORGANIZATIONS}")
        logger.info(f"  - Teams: {Config.NUM_TEAMS_MIN}-{Config.NUM_TEAMS_MAX}")
        logger.info(f"  - Users: {Config.NUM_USERS_MIN}-{Config.NUM_USERS_MAX}")
        logger.info(f"  - Date Range: {Config.DATE_RANGE_MONTHS} months")
        logger.info("")
        
        try:
            # Generate in order (respecting dependencies)
            self.generate_organizations()
            self.generate_users()
            self.generate_teams()
            self.generate_projects()
            project_sections = self.generate_sections()
            task_ids = self.generate_tasks(project_sections)
            self.generate_tags()
            self.assign_tags_to_tasks(task_ids)
            
            # Print summary
            self.print_summary()
            
            logger.info("=" * 60)
            logger.info("Generation complete!")
            logger.info(f"Database saved to: {Config.DATABASE_PATH}")
            logger.info("=" * 60)
        
        except Exception as e:
            logger.error(f"Error during generation: {e}", exc_info=True)
            raise
        finally:
            self.db.close()
    
    def print_summary(self):
        """Print generation summary"""
        logger.info("=" * 60)
        logger.info("Generation Summary")
        logger.info("=" * 60)
        
        tables = [
            'organizations', 'users', 'teams', 'team_memberships',
            'projects', 'sections', 'tasks', 'comments',
            'tags', 'task_tags', 'custom_field_definitions', 'custom_field_values'
        ]
        
        for table in tables:
            count = self.db.get_table_count(table)
            logger.info(f"  {table:30s}: {count:6d}")


if __name__ == "__main__":
    generator = AsanaDataGenerator()
    generator.generate_all()

