# Change Issue Table Name From Issues to Issue
**Problem**: In the ```project_management``` schema, the issues table is called ```issues```, instead of ```issue```. We want to keep a singular table name format for all tables, so that it does not cause mismatches in the crud and service generators.

**ACs**
- [ ] Change ```issues``` table name to ```issue```, with a migration script.
    - **Should we implement a more robust automated db management system for migrations, rollbacks, backups, restores, or just use alembic/pgadmin and rawdog it?**
    - I still need to implement at least some migration management as I don't even have a directory or strategy for rollbacks or migrations or backups, etc other than pgadmin.
- [ ] check all other table names to make sure that they are singular. If not, make them so.
- [ ] refactor service and crud generation scripts to be more clear with singular and plural variables
- [ ] delete all crud and service files and test them: first check if the issues crud and serrvice classes are fully abstracted and copied into the generate scripts beforehand, so we don't lose any progress.
