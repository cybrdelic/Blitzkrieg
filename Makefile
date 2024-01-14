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
seed-projects:
	cd blitzkrieg/project_management/db/make && python3 seed_projects.py
copy-last:
	bash copy_last.sh
generate-crud:
	cd blitzkrieg/project_management/db/crud && python3 .generate.py
