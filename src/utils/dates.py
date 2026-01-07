"""
Date and timestamp generation utilities.
Ensures temporal consistency across entities.
"""

from datetime import datetime, timedelta, date
import random
import numpy as np
from typing import Optional, Tuple
try:
    import pytz
except ImportError:
    pytz = None

# Business days (Monday=0 to Friday=4)
BUSINESS_DAYS = [0, 1, 2, 3, 4]


def generate_created_at(
    start_date: datetime,
    end_date: datetime,
    prefer_weekdays: bool = True,
    hour_distribution: str = 'business_hours'
) -> datetime:
    """
    Generate a realistic creation timestamp
    
    Args:
        start_date: Earliest possible date
        end_date: Latest possible date
        prefer_weekdays: Prefer weekdays (85% probability)
        hour_distribution: 'business_hours' (9-17) or 'uniform' (0-23)
    
    Returns:
        Datetime object
    """
    # Generate base date
    if prefer_weekdays:
        # 85% chance of weekday, 15% weekend
        if random.random() < 0.85:
            # Pick a weekday
            days_range = (end_date - start_date).days
            random_days = random.randint(0, days_range)
            candidate_date = start_date + timedelta(days=random_days)
            # If weekend, move to nearest weekday
            while candidate_date.weekday() > 4:
                candidate_date += timedelta(days=1)
                if candidate_date > end_date:
                    candidate_date = start_date + timedelta(days=random.randint(0, days_range))
                    while candidate_date.weekday() > 4:
                        candidate_date -= timedelta(days=1)
        else:
            # Weekend
            days_range = (end_date - start_date).days
            random_days = random.randint(0, days_range)
            candidate_date = start_date + timedelta(days=random_days)
            # Ensure it's a weekend
            while candidate_date.weekday() <= 4:
                candidate_date = start_date + timedelta(days=random.randint(0, days_range))
    else:
        days_range = (end_date - start_date).days
        random_days = random.randint(0, days_range)
        candidate_date = start_date + timedelta(days=random_days)
    
    # Generate time
    if hour_distribution == 'business_hours':
        # Higher activity during business hours (9 AM - 5 PM)
        # Weighted distribution: 70% business hours, 30% other
        if random.random() < 0.70:
            hour = random.randint(9, 17)
        else:
            hour = random.randint(0, 23)
    else:
        hour = random.randint(0, 23)
    
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    
    return candidate_date.replace(hour=hour, minute=minute, second=second)


def generate_due_date(
    created_at: datetime,
    project_type: str,
    overdue_probability: float = 0.05
) -> Optional[date]:
    """
    Generate realistic due date based on task creation and project type
    
    Distribution based on research:
    - 25% within 1 week
    - 40% within 1 month
    - 20% 1-3 months out
    - 10% no due date
    - 5% overdue (but ensure it's >= created_at.date() for constraint)
    
    Args:
        created_at: Task creation timestamp
        project_type: Type of project (affects distribution)
        overdue_probability: Probability of overdue task
    
    Returns:
        Date object or None
    """
    rand = random.random()
    created_date = created_at.date() if hasattr(created_at, 'date') else created_at
    
    # 10% no due date
    if rand < 0.10:
        return None
    
    # 5% overdue (but ensure constraint: due_date >= created_at.date())
    # For overdue, we'll set it to created_at.date() or 1 day after to satisfy constraint
    if rand < 0.15:
        # Set to same day or 1 day after creation (appears overdue relative to project timeline)
        due_date = created_date + timedelta(days=random.randint(0, 1))
        # Avoid weekends for 85% of tasks
        if random.random() < 0.85 and due_date.weekday() > 4:
            # Move to nearest weekday
            while due_date.weekday() > 4:
                due_date += timedelta(days=1)
        return due_date
    
    # 25% within 1 week
    if rand < 0.40:
        days_ahead = random.randint(1, 7)
    # 40% within 1 month (cumulative: 0.40 to 0.80)
    elif rand < 0.80:
        days_ahead = random.randint(8, 30)
    # 20% 1-3 months out (cumulative: 0.80 to 1.00)
    else:
        days_ahead = random.randint(31, 90)
    
    due_date = (created_at + timedelta(days=days_ahead)).date()
    
    # Avoid weekends for 85% of tasks
    if random.random() < 0.85 and due_date.weekday() > 4:
        # Move to nearest weekday
        while due_date.weekday() > 4:
            due_date += timedelta(days=1)
    
    return due_date


def generate_completed_at(
    created_at: datetime,
    due_date: Optional[date],
    completion_rate: float = 0.70
) -> Optional[datetime]:
    """
    Generate completion timestamp if task is completed
    
    Based on cycle time research: completion typically 1-14 days after creation
    (log-normal distribution)
    
    Args:
        created_at: Task creation timestamp
        due_date: Task due date (if any)
        completion_rate: Probability of task being completed
    
    Returns:
        Datetime object or None
    """
    if random.random() > completion_rate:
        return None
    
    # Log-normal distribution for cycle time (mean ~5 days, std ~3 days)
    # Convert to normal: log(cycle_time) ~ N(1.5, 0.5)
    log_cycle_time = np.random.normal(1.5, 0.5)
    cycle_time = max(1, int(np.exp(log_cycle_time)))  # At least 1 day
    
    completed_at = created_at + timedelta(days=cycle_time)
    
    # Ensure completion is before due date (if exists) and after creation
    if due_date:
        due_datetime = datetime.combine(due_date, datetime.min.time())
        # Make timezone-aware if created_at is timezone-aware
        if created_at.tzinfo is not None and due_datetime.tzinfo is None:
            if pytz:
                due_datetime = pytz.UTC.localize(due_datetime)
            else:
                # If pytz not available, make both naive
                completed_at = completed_at.replace(tzinfo=None)
        elif created_at.tzinfo is None and due_datetime.tzinfo is not None:
            due_datetime = due_datetime.replace(tzinfo=None)
        
        if completed_at > due_datetime:
            # Complete on or before due date (80% on time, 20% slightly late)
            if random.random() < 0.80:
                completed_at = due_datetime - timedelta(hours=random.randint(1, 24))
            else:
                # Slightly late (1-3 days)
                completed_at = due_datetime + timedelta(days=random.randint(1, 3))
    
    # Ensure completion is after creation
    if completed_at <= created_at:
        completed_at = created_at + timedelta(hours=random.randint(1, 24))
    
    return completed_at


def get_date_range(months_back: int = 6) -> Tuple[datetime, datetime]:
    """
    Get date range for data generation
    
    Args:
        months_back: Number of months to go back from now
    
    Returns:
        Tuple of (start_date, end_date)
    """
    if pytz:
        end_date = datetime.now(pytz.UTC)
    else:
        end_date = datetime.now()
    start_date = end_date - timedelta(days=months_back * 30)
    return start_date, end_date


def is_weekday(dt: datetime) -> bool:
    """Check if datetime is a weekday"""
    return dt.weekday() < 5

