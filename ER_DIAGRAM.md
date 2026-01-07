# Entity-Relationship Diagram

## Visual ER Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        ORGANIZATIONS                             │
├─────────────────────────────────────────────────────────────────┤
│ PK │ organization_id (TEXT/UUID)                                │
│    │ name (TEXT)                                                │
│    │ domain (TEXT)                                              │
│    │ created_at (TIMESTAMP)                                     │
│    │ is_organization (BOOLEAN)                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ 1:N
                              │
┌─────────────────────────────────────────────────────────────────┐
│                            USERS                                │
├─────────────────────────────────────────────────────────────────┤
│ PK │ user_id (TEXT/UUID)                                        │
│ FK │ organization_id (TEXT) → organizations.organization_id    │
│    │ name (TEXT)                                                │
│    │ email (TEXT, UNIQUE)                                       │
│    │ photo_url (TEXT, NULL)                                     │
│    │ created_at (TIMESTAMP)                                     │
│    │ is_active (BOOLEAN)                                        │
└─────────────────────────────────────────────────────────────────┘
         │                                    │
         │                                    │
         │ N:M                                │ N:M
         │                                    │
┌────────┴────────────────────────────────────┴──────────────────┐
│                    TEAM_MEMBERSHIPS                             │
├─────────────────────────────────────────────────────────────────┤
│ PK │ membership_id (TEXT/UUID)                                  │
│ FK │ team_id (TEXT) → teams.team_id                             │
│ FK │ user_id (TEXT) → users.user_id                             │
│    │ role (TEXT) - 'admin', 'member', 'limited_member'         │
│    │ joined_at (TIMESTAMP)                                      │
│    │ UNIQUE(team_id, user_id)                                   │
└─────────────────────────────────────────────────────────────────┘
         │
         │ N:1
         │
┌────────┴────────────────────────────────────────────────────────┐
│                           TEAMS                                  │
├─────────────────────────────────────────────────────────────────┤
│ PK │ team_id (TEXT/UUID)                                        │
│ FK │ organization_id (TEXT) → organizations.organization_id    │
│    │ name (TEXT)                                                │
│    │ description (TEXT, NULL)                                   │
│    │ created_at (TIMESTAMP)                                     │
└─────────────────────────────────────────────────────────────────┘
         │
         │ 1:N
         │
┌────────┴────────────────────────────────────────────────────────┐
│                         PROJECTS                                 │
├─────────────────────────────────────────────────────────────────┤
│ PK │ project_id (TEXT/UUID)                                      │
│ FK │ organization_id (TEXT) → organizations.organization_id    │
│ FK │ team_id (TEXT, NULL) → teams.team_id                       │
│    │ name (TEXT)                                                │
│    │ description (TEXT, NULL)                                   │
│    │ color (TEXT)                                               │
│    │ is_public (BOOLEAN)                                        │
│    │ archived (BOOLEAN)                                         │
│    │ created_at (TIMESTAMP)                                     │
│    │ modified_at (TIMESTAMP)                                    │
└─────────────────────────────────────────────────────────────────┘
         │                                    │
         │ 1:N                                │ 1:N
         │                                    │
┌────────┴──────────────┐      ┌─────────────┴────────────────────┐
│      SECTIONS         │      │  CUSTOM_FIELD_DEFINITIONS      │
├───────────────────────┤      ├────────────────────────────────┤
│ PK │ section_id       │      │ PK │ field_id (TEXT/UUID)      │
│ FK │ project_id       │      │ FK │ project_id → projects      │
│    │ name (TEXT)      │      │    │ name (TEXT)                │
│    │ position (INT)   │      │    │ type (TEXT)                │
│    │ created_at       │      │    │ enum_options (TEXT/JSON)   │
│    │ UNIQUE(project,  │      │    │ created_at                 │
│    │        name)     │      │    │ UNIQUE(project_id, name)   │
└───────────────────────┘      └────────────────────────────────┘
         │                                    │
         │ 1:N                                │ 1:N
         │                                    │
┌────────┴────────────────────────────────────┴──────────────────┐
│                            TASKS                                │
├─────────────────────────────────────────────────────────────────┤
│ PK │ task_id (TEXT/UUID)                                        │
│ FK │ project_id (TEXT) → projects.project_id                    │
│ FK │ section_id (TEXT, NULL) → sections.section_id             │
│ FK │ assignee_id (TEXT, NULL) → users.user_id                  │
│ FK │ parent_task_id (TEXT, NULL) → tasks.task_id (self-ref)   │
│    │ name (TEXT)                                                │
│    │ description (TEXT, NULL)                                  │
│    │ due_date (DATE, NULL)                                      │
│    │ due_on (DATE, NULL)                                        │
│    │ completed (BOOLEAN)                                        │
│    │ completed_at (TIMESTAMP, NULL)                            │
│    │ created_at (TIMESTAMP)                                     │
│    │ modified_at (TIMESTAMP)                                    │
│    │ num_subtasks (INTEGER)                                     │
│    │ num_completed_subtasks (INTEGER)                           │
│    │ CHECK: completed_at >= created_at                         │
│    │ CHECK: due_date >= DATE(created_at)                        │
└─────────────────────────────────────────────────────────────────┘
         │                                    │
         │ 1:N                                │ 1:N
         │                                    │
┌────────┴──────────────┐      ┌─────────────┴────────────────────┐
│      COMMENTS        │      │   CUSTOM_FIELD_VALUES            │
├───────────────────────┤      ├────────────────────────────────┤
│ PK │ comment_id      │      │ PK │ value_id (TEXT/UUID)       │
│ FK │ task_id         │      │ FK │ task_id → tasks             │
│ FK │ user_id         │      │ FK │ field_id → definitions      │
│    │ text (TEXT)     │      │    │ text_value (TEXT, NULL)     │
│    │ created_at      │      │    │ number_value (REAL, NULL)   │
└───────────────────────┘      │    │ enum_value (TEXT, NULL)    │
                               │    │ date_value (DATE, NULL)     │
                               │    │ created_at                  │
                               │    │ UNIQUE(task_id, field_id)   │
                               └────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                            TAGS                                 │
├─────────────────────────────────────────────────────────────────┤
│ PK │ tag_id (TEXT/UUID)                                         │
│ FK │ organization_id (TEXT) → organizations.organization_id    │
│    │ name (TEXT)                                                │
│    │ color (TEXT)                                               │
│    │ created_at (TIMESTAMP)                                     │
│    │ UNIQUE(organization_id, name)                             │
└─────────────────────────────────────────────────────────────────┘
         │
         │ N:M
         │
┌────────┴────────────────────────────────────────────────────────┐
│                        TASK_TAGS                                │
├─────────────────────────────────────────────────────────────────┤
│ PK │ association_id (TEXT/UUID)                                 │
│ FK │ task_id (TEXT) → tasks.task_id                            │
│ FK │ tag_id (TEXT) → tags.tag_id                               │
│    │ created_at (TIMESTAMP)                                     │
│    │ UNIQUE(task_id, tag_id)                                    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                        ATTACHMENTS                              │
├─────────────────────────────────────────────────────────────────┤
│ PK │ attachment_id (TEXT/UUID)                                  │
│ FK │ task_id (TEXT) → tasks.task_id                            │
│    │ name (TEXT)                                                │
│    │ file_type (TEXT)                                           │
│    │ file_size (INTEGER)                                        │
│    │ download_url (TEXT)                                        │
│    │ created_at (TIMESTAMP)                                     │
└─────────────────────────────────────────────────────────────────┘
```

## Key Relationships

1. **Organizations → Users**: One organization has many users
2. **Organizations → Teams**: One organization has many teams
3. **Teams ↔ Users**: Many-to-many via team_memberships
4. **Organizations → Projects**: One organization has many projects
5. **Teams → Projects**: One team can have many projects (optional)
6. **Projects → Sections**: One project has many sections
7. **Projects → Tasks**: One project has many tasks
8. **Sections → Tasks**: One section has many tasks (optional)
9. **Users → Tasks**: One user can be assigned many tasks (via assignee_id)
10. **Tasks → Tasks**: Self-referential for subtasks (parent_task_id)
11. **Tasks → Comments**: One task has many comments
12. **Users → Comments**: One user can write many comments
13. **Projects → Custom Fields**: One project has many custom field definitions
14. **Tasks → Custom Field Values**: One task can have many custom field values
15. **Organizations → Tags**: One organization has many tags
16. **Tasks ↔ Tags**: Many-to-many via task_tags
17. **Tasks → Attachments**: One task can have many attachments

## Design Notes

- **Subtasks**: Implemented via self-referential foreign key (parent_task_id)
- **Custom Fields**: Flexible schema supporting text, number, enum, and date types
- **Temporal Consistency**: All timestamps maintain logical ordering constraints
- **Referential Integrity**: All foreign keys properly reference existing entities

