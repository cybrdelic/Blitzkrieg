d6bdc969-ac35-4925-97dc-fe25a5707639
# README.md Generator GPT Assistant and Project Extrapolation

We want to implement the following feature: When a user inputs a project name, and a project description, the following occurs:

- a new project is created in the db with the associated data.
- the project name and project description is injected into a prompt telling GPT-4 to extrapolate the following and store them in the database:
1. project features
- id
- shorthand
- extended title
- description
2. project feature documents
3. objective (can be kunje)
- parent_id (can be project or feature)
4. hero
- id
- use
- body
5. CTAs
6. context
- parent_id (cand be project or feature)
- the chat responses are captured and stored in the database
- user input is
