cc5f8853-6186-4813-8b3c-dcde1de0131d
# Issues Generation

## The Problem
We need a way to create, view, and update the issues.

## The Solution
We will take advantage of the user's workflow being in an IDE with directories and markdown editors at hand.

### Issues Generation Features
- 1. When a user adds a markdown file to the .docs/issues in their local project directory, the issue is parsed and stored as an issue in the database, when updated with ```make update-issues```
