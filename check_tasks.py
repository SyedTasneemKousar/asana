import sqlite3
conn = sqlite3.connect('output/asana_simulation.sqlite')
cursor = conn.execute('SELECT COUNT(*) FROM projects')
total_projects = cursor.fetchone()[0]
cursor = conn.execute('SELECT COUNT(*) FROM tasks')
total_tasks = cursor.fetchone()[0]
cursor = conn.execute('SELECT project_id, COUNT(*) as task_count FROM tasks GROUP BY project_id')
projects_with_tasks = cursor.fetchall()
print(f"Total projects: {total_projects}")
print(f"Total tasks: {total_tasks}")
print(f"Projects with tasks: {len(projects_with_tasks)}")
print(f"Expected tasks: {total_projects * 5}-{total_projects * 15} (5-15 per project)")
if projects_with_tasks:
    print("\nTask distribution (first 10 projects):")
    for p in projects_with_tasks[:10]:
        print(f"  {p[0][:8]}...: {p[1]} tasks")
conn.close()

