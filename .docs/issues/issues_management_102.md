8c1587dd-22eb-457b-89da-5778065fe402
8177b0c7-e0cc-490d-803e-684b6d2fc936

# Issues Management 102

## The Problem
We need a way to create, view, and update the issues.

## The Solution
We will take advantage of the user's workflow being in an IDE with directories and markdown editors at hand.

### Issues Generation Features
- 1. When a user adds a markdown file to the .docs/issues in their local project directory, the issue is parsed and stored as an issue in the database, when updated with ```make update-issues```