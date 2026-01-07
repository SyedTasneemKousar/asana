-- Asana RL Environment Seed Data Schema
-- SQLite DDL for complete Asana workspace simulation

-- Organizations/Workspaces: Top-level containers
CREATE TABLE IF NOT EXISTS organizations (
    organization_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    domain TEXT,
    created_at TIMESTAMP NOT NULL,
    is_organization BOOLEAN DEFAULT 1,  -- 1 for organization, 0 for workspace
    UNIQUE(name)
);

-- Users: Members of the workspace
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    organization_id TEXT NOT NULL,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    photo_url TEXT,
    created_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    FOREIGN KEY (organization_id) REFERENCES organizations(organization_id)
);

-- Teams: Groups of users within a workspace
CREATE TABLE IF NOT EXISTS teams (
    team_id TEXT PRIMARY KEY,
    organization_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (organization_id) REFERENCES organizations(organization_id)
);

-- Team Memberships: Many-to-many relationship between users and teams
CREATE TABLE IF NOT EXISTS team_memberships (
    membership_id TEXT PRIMARY KEY,
    team_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    role TEXT DEFAULT 'member',  -- 'admin', 'member', 'limited_member'
    joined_at TIMESTAMP NOT NULL,
    FOREIGN KEY (team_id) REFERENCES teams(team_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    UNIQUE(team_id, user_id)
);

-- Projects: Collections of tasks organized around goals
CREATE TABLE IF NOT EXISTS projects (
    project_id TEXT PRIMARY KEY,
    organization_id TEXT NOT NULL,
    team_id TEXT,
    name TEXT NOT NULL,
    description TEXT,
    color TEXT,  -- Asana project colors
    is_public BOOLEAN DEFAULT 0,
    archived BOOLEAN DEFAULT 0,
    created_at TIMESTAMP NOT NULL,
    modified_at TIMESTAMP NOT NULL,
    FOREIGN KEY (organization_id) REFERENCES organizations(organization_id),
    FOREIGN KEY (team_id) REFERENCES teams(team_id)
);

-- Sections: Subdivisions within a project (e.g., "To Do," "In Progress," "Done")
CREATE TABLE IF NOT EXISTS sections (
    section_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    name TEXT NOT NULL,
    position INTEGER NOT NULL,  -- Order within project
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(project_id),
    UNIQUE(project_id, name)
);

-- Custom Field Definitions: User-defined fields for tracking metadata
CREATE TABLE IF NOT EXISTS custom_field_definitions (
    field_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    name TEXT NOT NULL,
    type TEXT NOT NULL,  -- 'text', 'number', 'enum', 'date', 'people'
    enum_options TEXT,  -- JSON array for enum types
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(project_id),
    UNIQUE(project_id, name)
);

-- Tags: Labels that can be applied across projects
CREATE TABLE IF NOT EXISTS tags (
    tag_id TEXT PRIMARY KEY,
    organization_id TEXT NOT NULL,
    name TEXT NOT NULL,
    color TEXT,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (organization_id) REFERENCES organizations(organization_id),
    UNIQUE(organization_id, name)
);

-- Tasks: The fundamental unit of work
CREATE TABLE IF NOT EXISTS tasks (
    task_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    section_id TEXT,
    name TEXT NOT NULL,
    description TEXT,
    assignee_id TEXT,  -- Can be NULL (unassigned)
    due_date DATE,
    due_on DATE,  -- Alternative due date format
    completed BOOLEAN DEFAULT 0,
    completed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL,
    modified_at TIMESTAMP NOT NULL,
    parent_task_id TEXT,  -- NULL for top-level tasks, references task_id for subtasks
    num_subtasks INTEGER DEFAULT 0,
    num_completed_subtasks INTEGER DEFAULT 0,
    FOREIGN KEY (project_id) REFERENCES projects(project_id),
    FOREIGN KEY (section_id) REFERENCES sections(section_id),
    FOREIGN KEY (assignee_id) REFERENCES users(user_id),
    FOREIGN KEY (parent_task_id) REFERENCES tasks(task_id),
    CHECK (completed_at IS NULL OR completed_at >= created_at),
    CHECK (due_date IS NULL OR due_date >= DATE(created_at))
);

-- Subtasks: Tasks nested within a parent task (handled via parent_task_id in tasks table)
-- Note: Subtasks are stored in the same tasks table with parent_task_id set

-- Custom Field Values: Values for custom fields on tasks
CREATE TABLE IF NOT EXISTS custom_field_values (
    value_id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    field_id TEXT NOT NULL,
    text_value TEXT,
    number_value REAL,
    enum_value TEXT,
    date_value DATE,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (task_id) REFERENCES tasks(task_id),
    FOREIGN KEY (field_id) REFERENCES custom_field_definitions(field_id),
    UNIQUE(task_id, field_id)
);

-- Task-Tag Associations: Many-to-many relationship
CREATE TABLE IF NOT EXISTS task_tags (
    association_id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    tag_id TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (task_id) REFERENCES tasks(task_id),
    FOREIGN KEY (tag_id) REFERENCES tags(tag_id),
    UNIQUE(task_id, tag_id)
);

-- Comments/Stories: Activity and discussion on tasks
CREATE TABLE IF NOT EXISTS comments (
    comment_id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    text TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (task_id) REFERENCES tasks(task_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Attachments: Files attached to tasks
CREATE TABLE IF NOT EXISTS attachments (
    attachment_id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    name TEXT NOT NULL,
    file_type TEXT,  -- 'pdf', 'docx', 'png', etc.
    file_size INTEGER,  -- bytes
    download_url TEXT,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (task_id) REFERENCES tasks(task_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_tasks_section ON tasks(section_id);
CREATE INDEX IF NOT EXISTS idx_tasks_assignee ON tasks(assignee_id);
CREATE INDEX IF NOT EXISTS idx_tasks_parent ON tasks(parent_task_id);
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);
CREATE INDEX IF NOT EXISTS idx_tasks_created ON tasks(created_at);
CREATE INDEX IF NOT EXISTS idx_comments_task ON comments(task_id);
CREATE INDEX IF NOT EXISTS idx_comments_user ON comments(user_id);
CREATE INDEX IF NOT EXISTS idx_team_memberships_team ON team_memberships(team_id);
CREATE INDEX IF NOT EXISTS idx_team_memberships_user ON team_memberships(user_id);
CREATE INDEX IF NOT EXISTS idx_projects_team ON projects(team_id);
CREATE INDEX IF NOT EXISTS idx_sections_project ON sections(project_id);

