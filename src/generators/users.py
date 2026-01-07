"""
User generation module.
Creates realistic users with proper organization assignment.
"""

import uuid
import random
import logging
from datetime import datetime
from typing import List, Tuple
from src.models.database import Database
from src.scrapers.demographics import generate_user_name, generate_email
from src.utils.dates import generate_created_at, get_date_range

logger = logging.getLogger(__name__)


class UserGenerator:
    """Generator for users"""
    
    def __init__(self, db: Database, organization_id: str, date_range: Tuple[datetime, datetime]):
        """
        Initialize user generator
        
        Args:
            db: Database connection
            organization_id: Organization ID
            date_range: (start_date, end_date) tuple
        """
        self.db = db
        self.organization_id = organization_id
        self.start_date, self.end_date = date_range
        self.domain = None  # Will be set from organization
    
    def set_domain(self, domain: str):
        """Set company domain for email generation"""
        self.domain = domain
    
    def generate_users(self, count: int) -> List[str]:
        """
        Generate users and insert into database
        
        Args:
            count: Number of users to generate
        
        Returns:
            List of user IDs
        """
        logger.info(f"Generating {count} users...")
        
        # Get existing emails from database
        cursor = self.db.execute("SELECT email FROM users")
        existing_emails = set(row[0] for row in cursor.fetchall())
        logger.info(f"Found {len(existing_emails)} existing users in database")
        
        user_ids = []
        users_data = []
        generated_emails = existing_emails.copy()  # Track generated emails to ensure uniqueness
        
        for i in range(count):
            user_id = str(uuid.uuid4())
            first_name, last_name = generate_user_name()
            name = f"{first_name} {last_name}"
            
            # Generate unique email
            max_attempts = 10
            email = None
            for attempt in range(max_attempts):
                candidate_email = generate_email(first_name, last_name, self.domain)
                if candidate_email not in generated_emails:
                    email = candidate_email
                    generated_emails.add(email)
                    break
            
            # If still no unique email, add random suffix
            if email is None:
                email = f"{first_name.lower()}.{last_name.lower()}.{random.randint(1000, 9999)}@{self.domain}"
                generated_emails.add(email)
            
            created_at = generate_created_at(
                self.start_date,
                self.end_date,
                prefer_weekdays=True,
                hour_distribution='business_hours'
            )
            
            # 95% active users, 5% inactive
            is_active = random.random() > 0.05
            
            users_data.append((
                user_id,
                self.organization_id,
                name,
                email,
                None,  # photo_url
                created_at.isoformat(),
                1 if is_active else 0
            ))
            
            user_ids.append(user_id)
            
            # Batch insert every 50 users (faster)
            if len(users_data) >= 50:
                self._insert_users(users_data)
                users_data = []
        
        # Insert remaining users
        if users_data:
            self._insert_users(users_data)
        
        logger.info(f"Generated {len(user_ids)} users")
        return user_ids
    
    def _insert_users(self, users_data: List[tuple]):
        """Insert users into database"""
        sql = """
            INSERT INTO users (user_id, organization_id, name, email, photo_url, created_at, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        self.db.executemany(sql, users_data)
        self.db.commit()

