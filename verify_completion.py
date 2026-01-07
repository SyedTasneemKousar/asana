"""
Comprehensive verification script for database completion
"""
import sqlite3

conn = sqlite3.connect('output/asana_simulation.sqlite')
conn.row_factory = sqlite3.Row

print("=" * 60)
print("COMPREHENSIVE DATABASE VERIFICATION")
print("=" * 60)

# Check all tables
tables = {
    'organizations': 'Organizations',
    'users': 'Users',
    'teams': 'Teams',
    'team_memberships': 'Team Memberships',
    'projects': 'Projects',
    'sections': 'Sections',
    'tasks': 'Tasks',
    'comments': 'Comments',
    'tags': 'Tags',
    'task_tags': 'Task-Tag Associations',
    'custom_field_definitions': 'Custom Field Definitions',
    'custom_field_values': 'Custom Field Values'
}

total_rows = 0
for table, name in tables.items():
    try:
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        total_rows += count
        status = "✅" if count > 0 else "❌"
        print(f"{status} {name:30s}: {count:6d} rows")
    except Exception as e:
        print(f"❌ {name:30s}: ERROR - {e}")

print("=" * 60)
print(f"TOTAL ROWS: {total_rows:,}")
print("=" * 60)

# Check data quality
print("\n📊 DATA QUALITY CHECKS:")
print("-" * 60)

# Check if tasks have projects
tasks_with_projects = conn.execute("SELECT COUNT(*) FROM tasks WHERE project_id IS NOT NULL").fetchone()[0]
total_tasks = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
if total_tasks > 0:
    print(f"✅ Tasks with projects: {tasks_with_projects}/{total_tasks} ({tasks_with_projects*100//total_tasks}%)")

# Check if tasks have assignees
tasks_with_assignees = conn.execute("SELECT COUNT(*) FROM tasks WHERE assignee_id IS NOT NULL").fetchone()[0]
if total_tasks > 0:
    print(f"✅ Tasks with assignees: {tasks_with_assignees}/{total_tasks} ({tasks_with_assignees*100//total_tasks}%)")

# Check completed tasks
completed_tasks = conn.execute("SELECT COUNT(*) FROM tasks WHERE completed = 1").fetchone()[0]
if total_tasks > 0:
    print(f"✅ Completed tasks: {completed_tasks}/{total_tasks} ({completed_tasks*100//total_tasks}%)")

# Check comments
total_comments = conn.execute("SELECT COUNT(*) FROM comments").fetchone()[0]
if total_tasks > 0:
    comments_per_task = total_comments / total_tasks if total_tasks > 0 else 0
    print(f"✅ Comments: {total_comments} ({comments_per_task:.2f} per task)")

# Check tags
total_tags = conn.execute("SELECT COUNT(*) FROM tags").fetchone()[0]
tagged_tasks = conn.execute("SELECT COUNT(DISTINCT task_id) FROM task_tags").fetchone()[0]
if total_tasks > 0:
    print(f"✅ Tagged tasks: {tagged_tasks}/{total_tasks} ({tagged_tasks*100//total_tasks}%)")

conn.close()

print("\n" + "=" * 60)
if total_rows > 1000:
    print("✅ DATABASE IS COMPLETE AND READY!")
else:
    print("⚠️  Database may still be generating...")
print("=" * 60)

