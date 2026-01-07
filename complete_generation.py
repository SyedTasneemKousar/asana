"""
Complete the database generation - generate tags and task_tags
Run this after main.py to complete missing data
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.models.database import Database
from src.generators.tags import TagGenerator
from src.config import Config
from src.utils.dates import get_date_range
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def complete_generation():
    """Complete tag generation"""
    db = Database(Config.DATABASE_PATH)
    date_range = get_date_range(Config.DATE_RANGE_MONTHS)
    
    # Get organization ID
    cursor = db.execute("SELECT organization_id FROM organizations LIMIT 1")
    org_result = cursor.fetchone()
    if not org_result:
        logger.error("No organization found!")
        return
    organization_id = org_result[0]
    
    # Get all task IDs
    cursor = db.execute("SELECT task_id FROM tasks")
    task_ids = [row[0] for row in cursor.fetchall()]
    
    logger.info(f"Found {len(task_ids)} tasks")
    
    if len(task_ids) == 0:
        logger.warning("No tasks found! Cannot generate tags.")
        return
    
    # Generate tags
    logger.info("=" * 60)
    logger.info("Generating Tags")
    logger.info("=" * 60)
    
    tag_gen = TagGenerator(db, organization_id, date_range)
    tag_ids = tag_gen.generate_tags()
    
    logger.info(f"Generated {len(tag_ids)} tags")
    
    # Assign tags to tasks
    logger.info("=" * 60)
    logger.info("Assigning Tags to Tasks")
    logger.info("=" * 60)
    
    tag_gen.assign_tags_to_tasks(task_ids, tag_ids, assignment_rate=0.30)
    
    # Print summary
    logger.info("=" * 60)
    logger.info("Generation Summary")
    logger.info("=" * 60)
    
    tables = ['tags', 'task_tags']
    for table in tables:
        count = db.get_table_count(table)
        logger.info(f"  {table:30s}: {count:6d}")
    
    logger.info("=" * 60)
    logger.info("Tag generation complete!")
    logger.info("=" * 60)
    
    db.close()

if __name__ == "__main__":
    complete_generation()

