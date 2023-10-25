# Blitzkrieg

**Quickly set up and manage databases for your projects with a beautiful CLI interface.**

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Prerequisites](#prerequisites)
4. [Installation](#installation)
5. [Usage](#usage)
6. [Contributing](#contributing)
7. [Support](#support)
8. [License](#license)

## Overview

Setting up databases, especially in development environments, can be a tedious process. `Blitzkrieg` is designed to simplify and automate this process, allowing developers to focus on what matters most: building great applications. With just a few commands, you can have a fully functional PostgreSQL instance up and running, along with a pgAdmin interface for easy database management.

### Use Cases

- **Rapid Prototyping**: Quickly get a database up and running for prototyping or testing new ideas.
- **Development Environments**: Ensure every member of your team has a consistent database setup.
- **Learning and Tutorials**: Perfect for educators or learners who want to focus on database concepts without getting bogged down in setup details.

## Features

- **Easy Setup**: Just a few commands to get a fully functional PostgreSQL instance.
- **Beautiful CLI**: An interactive and intuitive command-line interface powered by Rich and Questionary.
- **Docker Integration**: All databases run in Docker containers for easy management and portability.
- **Extensibility**: Designed to be extended with more database options in the future.

## Prerequisites

- Python 3.7+
- Docker

## Installation

```bash
pip install blitzkrieg
```

## Usage

To set up a PostgreSQL database:

```bash
blitz setup postgres
```

Then, follow the on-screen prompts to customize your setup.

## Contributing

We welcome contributions from the community! Please read our [contributing guidelines](./CONTRIBUTING.md) for more information.

## Support

If you encounter any issues or have feature requests, please [open an issue](https://github.com/yourusername/Blitzkrieg/issues) on our GitHub repository.

## License

`Blitzkrieg` is licensed under the [MIT License](./LICENSE).

---
