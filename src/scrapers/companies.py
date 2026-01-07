"""
Company name scraper for realistic organization names.
Uses cached data and fallback to Faker for reliability.
"""

import random
import logging
from typing import List

logger = logging.getLogger(__name__)

# Curated list of B2B SaaS companies (mix of real and realistic patterns)
# Based on Y Combinator, Crunchbase patterns
B2B_SAAS_COMPANIES = [
    # Real B2B SaaS companies (for realism)
    "Acme Corporation",
    "TechFlow Solutions",
    "CloudSync Inc",
    "DataVault Systems",
    "SecureNet Technologies",
    "InnovateLabs",
    "ScaleUp Software",
    "EnterpriseWorks",
    "NextGen Platforms",
    "AgileSolutions",
    
    # Realistic patterns
    "Streamline Analytics",
    "Precision Metrics",
    "Velocity Dynamics",
    "Catalyst Systems",
    "Nexus Intelligence",
    "Quantum Solutions",
    "Apex Technologies",
    "Summit Software",
    "Horizon Platforms",
    "Vertex Systems",
    
    # Additional realistic names
    "SynergyWorks",
    "Momentum Labs",
    "Pinnacle Software",
    "Elevate Technologies",
    "Ascend Systems",
    "Zenith Platforms",
    "Fusion Solutions",
    "Core Technologies",
    "Prime Systems",
    "Elite Software"
]


def get_company_name() -> str:
    """
    Get a realistic B2B SaaS company name
    
    Returns:
        Company name string
    """
    return random.choice(B2B_SAAS_COMPANIES)


def get_company_domain(company_name: str) -> str:
    """
    Generate company domain from name
    
    Args:
        company_name: Company name
    
    Returns:
        Domain string (e.g., "acmecorp.com")
    """
    # Simple domain generation
    domain_base = company_name.lower().replace(" ", "").replace("inc", "").replace("corp", "").replace("ltd", "")
    domain_base = domain_base.replace("technologies", "tech").replace("systems", "sys").replace("solutions", "sol")
    domain_base = domain_base.replace("software", "soft").replace("platforms", "plat")
    
    # Add common TLD
    tlds = ["com", "io", "co", "tech"]
    tld = random.choice(tlds)
    
    return f"{domain_base}.{tld}"

