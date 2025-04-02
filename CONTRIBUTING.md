# Contributing to the Autonomous AI System

## Getting Started

1. Fork the repository
2. Clone your fork
3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Run the setup script:
   ```bash
   ./scripts/setup.py
   ```

## Development Workflow

1. Create a new branch for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following the project guidelines:
   - Follow PEP 8 style guide
   - Add docstrings to all functions and classes
   - Write unit tests for new functionality
   - Update documentation as needed

3. Run tests:
   ```bash
   pytest
   ```

4. Commit your changes:
   ```bash
   git add .
   git commit -m "feat: description of your changes"
   ```

5. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

6. Create a Pull Request

## Code Style

- Follow PEP 8 guidelines
- Use type hints
- Write clear docstrings
- Keep functions focused and small
- Use meaningful variable names
- Comment complex logic

## Testing

- Write unit tests for new functionality
- Ensure all tests pass before submitting PR
- Maintain or improve test coverage
- Include integration tests for new features

## Documentation

- Update relevant documentation
- Add docstrings to new functions/classes
- Update API documentation if endpoints change
- Keep README.md up to date

## Pull Request Process

1. Update the README.md with details of changes if needed
2. Update the documentation with any new features
3. Ensure all tests pass
4. Request review from maintainers

## Rate Limiting

- Respect rate limits in all API calls
- Use the provided rate limiting utilities
- Test rate limiting in your changes

## Knowledge Graph

- Follow the schema defined in MISSION.md
- Validate all knowledge graph operations
- Include proper error handling
- Update metadata appropriately

## Workflow Development

- Follow the workflow generation rules
- Include validation steps
- Implement proper error handling
- Document workflow changes

## Content Processing

- Validate content types
- Respect size limits
- Follow content processing rules
- Update knowledge graph appropriately

## Git Guidelines

- Use feature branches
- Write clear commit messages
- Keep commits focused and atomic
- Follow the commit message format:
  - feat: New feature
  - fix: Bug fix
  - docs: Documentation changes
  - style: Code style changes
  - refactor: Code refactoring
  - test: Adding tests
  - chore: Maintenance tasks

## Questions?

If you have any questions, please:
1. Check the documentation
2. Review existing issues
3. Create a new issue if needed
4. Contact the maintainers

## License

By contributing, you agree that your contributions will be licensed under the project's license. 