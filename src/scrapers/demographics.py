"""
User name and demographic data generation.
Based on census data patterns for realistic distributions.
"""

import random
from typing import Tuple
from faker import Faker

# Initialize Faker with realistic locales
fake = Faker(['en_US', 'en_GB', 'en_CA', 'en_AU', 'es_ES', 'fr_FR', 'de_DE', 'it_IT', 'pt_BR', 'ja_JP'])


def generate_user_name() -> Tuple[str, str]:
    """
    Generate realistic user name (first, last)
    
    Uses Faker with multiple locales for diversity
    
    Returns:
        Tuple of (first_name, last_name)
    """
    # Weighted locale selection (US/UK/CA/AU more common in B2B SaaS)
    locales = ['en_US'] * 50 + ['en_GB'] * 15 + ['en_CA'] * 10 + ['en_AU'] * 8 + \
              ['es_ES'] * 5 + ['fr_FR'] * 4 + ['de_DE'] * 3 + ['it_IT'] * 2 + ['pt_BR'] * 2 + ['ja_JP'] * 1
    
    locale = random.choice(locales)
    fake_locale = Faker(locale)
    
    first_name = fake_locale.first_name()
    last_name = fake_locale.last_name()
    
    return first_name, last_name


def generate_email(first_name: str, last_name: str, domain: str) -> str:
    """
    Generate realistic email address
    
    Patterns observed in enterprise:
    - first.last@domain.com (60%)
    - firstlast@domain.com (20%)
    - f.last@domain.com (10%)
    - first.l@domain.com (5%)
    - first_last@domain.com (5%)
    
    Args:
        first_name: First name
        last_name: Last name
        domain: Company domain
    
    Returns:
        Email address
    """
    first = first_name.lower()
    last = last_name.lower()
    
    rand = random.random()
    
    if rand < 0.60:
        # first.last@domain.com
        email = f"{first}.{last}@{domain}"
    elif rand < 0.80:
        # firstlast@domain.com
        email = f"{first}{last}@{domain}"
    elif rand < 0.90:
        # f.last@domain.com
        email = f"{first[0]}.{last}@{domain}"
    elif rand < 0.95:
        # first.l@domain.com
        email = f"{first}.{last[0]}@{domain}"
    else:
        # first_last@domain.com
        email = f"{first}_{last}@{domain}"
    
    # Handle special characters
    email = email.replace("'", "").replace(" ", "")
    
    return email

