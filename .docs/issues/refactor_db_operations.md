# Refactor DB Operations:

**ACs**:

- [ ] Create ```DBClassGenerator``` class to generate ```{camel_case_model_name}CRUD``` and ```{camel_case_model_name}Serivce``` classes when using ```make update```: this modularizes and contains all the generate logic into their own

- [ ] adds BlitzBaseModel with the following fields:
    - [ ] created_by
    - [ ] created_at
    - [ ] updated_at
    - [ ] updated_by
    - [ ] deleted_at
    - [ ] deleted_by
    - [ ] is_deleted
    - [ ] id
    - [ ] name
    - [ ] index

- [ ] envision and implement a new system for incorporating the ```db``` module into the ```blitz``` CLI, instead of using the following Makefile:
```
        test-config:
            cd blitzkrieg/project_management/config && python3 test.py
        test-create-repo:
            cd blitzkrieg/project_management/github && python3 test.py
        test-delete-repo:
            cd blitzkrieg/project_management/github && python3 test_delete_github_repo.py
        test-create-project:
            cd blitzkrieg/project_management/dir_management && python3 test_create_project.py
        test-delete-project:
            cd blitzkrieg/project_management/dir_management && python3 test_delete_project.py
        create-schemas:
            cd blitzkrieg/project_management/db/make && python3 create_schemas.py
        create-tables:
            cd blitzkrieg/project_management/db/make && python3 create_tables.py
        create-enums:
            cd blitzkrieg/project_management/db/make && python3 create_enums.py
        create-db:
            make create-schemas && make create-enums && make create-tables
        create-projects:
            cd blitzkrieg/project_management/db/make && python3 create_projects.py
        create-issues:
            cd blitzkrieg/project_management/db/make && python3 create_issues.py
        seed-projects:
            cd blitzkrieg/project_management/db/make && python3 seed_projects.py
        copy-last:
            bash copy_last.sh
        generate-crud:
            cd blitzkrieg/project_management/db/crud && python3 .generate.py
        generate-services:
            cd blitzkrieg/project_management/db/services && python3 .generate.py
        update:
            make create-tables && make generate-crud && make generate-services
        drop-tables:
            cd blitzkrieg/project_management/db/make && python3 drop_tables.py

```
