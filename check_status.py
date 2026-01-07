import sqlite3
conn = sqlite3.connect('output/asana_simulation.sqlite')
tables = ['organizations', 'users', 'teams', 'projects', 'sections', 'tasks', 'comments', 'tags', 'task_tags']
print("=" * 50)
print("DATABASE GENERATION STATUS")
print("=" * 50)
for table in tables:
    try:
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"{table:25s}: {count:6d} rows")
    except:
        pass
conn.close()

