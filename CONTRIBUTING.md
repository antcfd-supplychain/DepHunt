# Contributing to DepHunt

Thank you for considering contributing to DepHunt! This document outlines the process for contributing to this project.

## Development Setup

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/DepHunt.git`
3. Create a virtual environment: `python -m venv venv`
4. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
5. Install development dependencies: `pip install -r requirements-dev.txt`

## Code Style

- Follow PEP 8 guidelines for Python code
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Include type hints where possible
- Run `black` and `flake8` before submitting PRs

## Testing

- Write tests for all new features and bug fixes
- Ensure all tests pass before submitting a PR: `pytest`
- Aim for increasing test coverage with each contribution

## Pull Request Process

1. Create a new branch for your feature: `git checkout -b feature/your-feature-name`
2. Make your changes and commit them with clear, descriptive messages
3. Push your changes to your fork: `git push origin feature/your-feature-name`
4. Submit a PR to the main repository
5. Update the README.md if needed with details of changes

## Reporting Issues

- Use the provided issue templates when filing bugs or feature requests
- Include detailed steps to reproduce for bug reports
- For feature requests, explain the use case and benefits

## Documentation

- Update documentation to reflect any changes you make
- Document any new command-line options
- Provide examples for new features

## Adding Support for New Package Ecosystems

When adding support for a new package ecosystem:

1. Create a new module in the ecosystems directory
2. Implement the required interface methods
3. Add tests for the new ecosystem
4. Update the README.md with information about the new ecosystem
5. Add any new dependencies to requirements.txt

## License

By contributing, you agree that your contributions will be licensed under the project's MIT License.
