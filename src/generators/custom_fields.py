"""
Custom field generation module.
Creates custom fields for projects and their values on tasks.
"""

import uuid
import random
import json
import logging
from datetime import datetime, date
from typing import List, Tuple, Dict
from src.models.database import Database
from src.config import Config
from src.utils.dates import generate_created_at

logger = logging.getLogger(__name__)

# Custom field value options by type
CUSTOM_FIELD_OPTIONS = {
    'priority': ['Low', 'Medium', 'High', 'Critical'],
    'effort': ['Small', 'Medium', 'Large', 'Extra Large'],
    'sprint': ['Sprint 1', 'Sprint 2', 'Sprint 3', 'Sprint 4'],
    'severity': ['Low', 'Medium', 'High', 'Critical'],
    'reproducibility': ['Always', 'Sometimes', 'Rarely', 'Once'],
    'channel': ['Email', 'Social Media', 'Blog', 'Website', 'Paid Ads'],
    'status': ['Draft', 'In Review', 'Approved', 'Published'],
    'category': ['Infrastructure', 'Process', 'Policy', 'Tooling']
}


class CustomFieldGenerator:
    """Generator for custom fields"""
    
    def __init__(self, db: Database, date_range: Tuple[datetime, datetime]):
        """
        Initialize custom field generator
        
        Args:
            db: Database connection
            date_range: (start_date, end_date) tuple
        """
        self.db = db
        self.start_date, self.end_date = date_range
    
    def generate_custom_fields(
        self,
        project_id: str,
        project_type: str,
        project_created_at: str
    ) -> List[str]:
        """
        Generate custom fields for a project
        
        Args:
            project_id: Project ID
            project_type: Type of project
            project_created_at: Project creation timestamp
        
        Returns:
            List of field IDs
        """
        # Get custom field types for project type
        field_types = Config.CUSTOM_FIELD_TYPES.get(project_type, [])
        
        if not field_types:
            return []
        
        logger.debug(f"Generating custom fields for project {project_id}...")
        
        fields_data = []
        field_ids = []
        
        project_dt = datetime.fromisoformat(project_created_at)
        
        for field_type in field_types:
            field_id = str(uuid.uuid4())
            field_name = field_type.replace('_', ' ').title()
            
            # Determine field type and enum options
            if field_type in ['priority', 'severity', 'status', 'category']:
                db_type = 'enum'
                enum_options = CUSTOM_FIELD_OPTIONS.get(field_type, ['Option 1', 'Option 2'])
            elif field_type in ['effort', 'sprint']:
                db_type = 'enum'
                enum_options = CUSTOM_FIELD_OPTIONS.get(field_type, ['Option 1', 'Option 2'])
            elif field_type == 'channel':
                db_type = 'enum'
                enum_options = CUSTOM_FIELD_OPTIONS.get(field_type, ['Option 1', 'Option 2'])
            else:
                db_type = 'text'
                enum_options = None
            
            created_at = generate_created_at(project_dt, self.end_date, prefer_weekdays=True)
            
            fields_data.append((
                field_id,
                project_id,
                field_name,
                db_type,
                json.dumps(enum_options) if enum_options else None,
                created_at.isoformat()
            ))
            
            field_ids.append(field_id)
        
        # Insert custom fields
        if fields_data:
            self._insert_custom_fields(fields_data)
        
        return field_ids
    
    def assign_custom_field_values(
        self,
        task_id: str,
        field_ids: List[str],
        field_types: Dict[str, str]
    ):
        """
        Assign custom field values to a task
        
        Args:
            task_id: Task ID
            field_ids: List of field IDs
            field_types: Dict mapping field_id to field type
        """
        values_data = []
        
        for field_id in field_ids:
            field_type = field_types.get(field_id, 'text')
            
            # Generate value based on field type
            if field_type == 'enum':
                # Get enum options from field definition
                cursor = self.db.execute(
                    "SELECT enum_options FROM custom_field_definitions WHERE field_id = ?",
                    (field_id,)
                )
                result = cursor.fetchone()
                if result and result[0]:
                    options = json.loads(result[0])
                    enum_value = random.choice(options)
                else:
                    enum_value = "Option 1"
                
                values_data.append((
                    str(uuid.uuid4()),
                    task_id,
                    field_id,
                    None,  # text_value
                    None,  # number_value
                    enum_value,
                    None,  # date_value
                    datetime.now().isoformat()
                ))
            elif field_type == 'number':
                number_value = random.randint(1, 100)
                values_data.append((
                    str(uuid.uuid4()),
                    task_id,
                    field_id,
                    None,
                    number_value,
                    None,
                    None,
                    datetime.now().isoformat()
                ))
            elif field_type == 'date':
                date_value = generate_created_at(self.start_date, self.end_date, prefer_weekdays=True).date()
                values_data.append((
                    str(uuid.uuid4()),
                    task_id,
                    field_id,
                    None,
                    None,
                    None,
                    date_value.isoformat(),
                    datetime.now().isoformat()
                ))
            else:  # text
                text_value = f"Value for {field_id[:8]}"
                values_data.append((
                    str(uuid.uuid4()),
                    task_id,
                    field_id,
                    text_value,
                    None,
                    None,
                    None,
                    datetime.now().isoformat()
                ))
        
        # Insert values (70% of tasks have custom field values)
        if values_data and random.random() < 0.70:
            self._insert_custom_field_values(values_data)
    
    def _insert_custom_fields(self, fields_data: List[tuple]):
        """Insert custom fields into database"""
        sql = """
            INSERT INTO custom_field_definitions (
                field_id, project_id, name, type, enum_options, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """
        self.db.executemany(sql, fields_data)
        self.db.commit()
    
    def _insert_custom_field_values(self, values_data: List[tuple]):
        """Insert custom field values into database"""
        sql = """
            INSERT INTO custom_field_values (
                value_id, task_id, field_id, text_value, number_value,
                enum_value, date_value, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.db.executemany(sql, values_data)
        self.db.commit()

