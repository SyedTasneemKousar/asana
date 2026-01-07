"""
Team generation module.
Creates teams with realistic names and memberships.
"""

import uuid
import random
import logging
from datetime import datetime
from typing import List, Tuple, Dict
from src.models.database import Database
from src.utils.dates import generate_created_at
from src.utils.distributions import sample_team_size

logger = logging.getLogger(__name__)

# Realistic team names for B2B SaaS company
TEAM_NAMES = [
    # Engineering teams
    "Platform Engineering", "Frontend Team", "Backend Services", "DevOps", "Infrastructure",
    "Mobile Engineering", "Data Engineering", "Security Team", "QA Engineering",
    
    # Product teams
    "Product Management", "Product Design", "User Experience", "Product Analytics",
    
    # Marketing teams
    "Growth Marketing", "Content Marketing", "Product Marketing", "Demand Generation",
    "Brand Marketing", "Marketing Operations",
    
    # Sales teams
    "Enterprise Sales", "SMB Sales", "Sales Engineering", "Customer Success",
    
    # Operations teams
    "People Operations", "Finance", "Legal", "IT Operations", "Facilities",
    
    # Cross-functional
    "Customer Support", "Business Development", "Partnerships"
]


class TeamGenerator:
    """Generator for teams"""
    
    def __init__(self, db: Database, organization_id: str, date_range: Tuple[datetime, datetime]):
        """
        Initialize team generator
        
        Args:
            db: Database connection
            organization_id: Organization ID
            date_range: (start_date, end_date) tuple
        """
        self.db = db
        self.organization_id = organization_id
        self.start_date, self.end_date = date_range
    
    def generate_teams(self, count: int, user_ids: List[str]) -> List[Tuple[str, List[str]]]:
        """
        Generate teams and assign members
        
        Args:
            count: Number of teams to generate
            user_ids: Available user IDs for membership
        
        Returns:
            List of (team_id, member_user_ids) tuples
        """
        logger.info(f"Generating {count} teams...")
        
        teams_data = []
        team_memberships = []
        
        # Use available team names or generate generic ones
        available_names = TEAM_NAMES.copy()
        random.shuffle(available_names)
        
        for i in range(count):
            team_id = str(uuid.uuid4())
            
            # Get team name
            if available_names:
                name = available_names.pop()
            else:
                name = f"Team {i + 1}"
            
            # Generate description (30% have descriptions)
            description = None
            if random.random() < 0.30:
                description = f"Team responsible for {name.lower()}"
            
            # Team color (Asana project colors)
            colors = ['blue', 'green', 'orange', 'red', 'purple', 'pink', 'yellow', 'cyan']
            color = random.choice(colors)
            
            created_at = generate_created_at(
                self.start_date,
                self.end_date,
                prefer_weekdays=True
            )
            
            teams_data.append((
                team_id,
                self.organization_id,
                name,
                description,
                created_at.isoformat()
            ))
            
            # Assign team members
            team_size = sample_team_size()
            member_user_ids = random.sample(user_ids, min(team_size, len(user_ids)))
            
            # Create memberships
            for user_id in member_user_ids:
                membership_id = str(uuid.uuid4())
                # 10% admins, 90% members
                role = 'admin' if random.random() < 0.10 else 'member'
                joined_at = generate_created_at(created_at, self.end_date, prefer_weekdays=True)
                
                team_memberships.append((
                    membership_id,
                    team_id,
                    user_id,
                    role,
                    joined_at.isoformat()
                ))
        
        # Insert teams
        self._insert_teams(teams_data)
        
        # Insert memberships
        membership_data = [m for m in team_memberships]
        if membership_data:
            self._insert_memberships(membership_data)
        
        # Return team IDs with their member lists
        team_info = {}
        for team_id, _, user_id, _, _ in membership_data:
            if team_id not in team_info:
                team_info[team_id] = []
            team_info[team_id].append(user_id)
        
        result = [(team_id, team_info.get(team_id, [])) for team_id, _, _, _, _ in teams_data]
        return result
    
    def _insert_teams(self, teams_data: List[tuple]):
        """Insert teams into database"""
        sql = """
            INSERT INTO teams (team_id, organization_id, name, description, created_at)
            VALUES (?, ?, ?, ?, ?)
        """
        self.db.executemany(sql, teams_data)
        self.db.commit()
    
    def _insert_memberships(self, memberships_data: List[tuple]):
        """Insert team memberships into database"""
        sql = """
            INSERT INTO team_memberships (membership_id, team_id, user_id, role, joined_at)
            VALUES (?, ?, ?, ?, ?)
        """
        self.db.executemany(sql, memberships_data)
        self.db.commit()

