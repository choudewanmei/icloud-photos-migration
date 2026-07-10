# Contributing to iCloud Photos Migration Assistant

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing.

## How to Contribute

### Reporting Issues

1. Check existing [issues](https://github.com/YOUR_USERNAME/icloud-photos-migration/issues) to avoid duplicates
2. Create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots (if applicable)
   - System information (macOS version, Python version)

### Suggesting Features

1. Open an issue with the "feature request" label
2. Describe the feature and its use case
3. Explain why it would be beneficial

### Submitting Code

1. **Fork the Repository**
   ```bash
   # Fork on GitHub, then clone
   git clone https://github.com/YOUR_USERNAME/icloud-photos-migration.git
   cd icloud-photos-migration
   ```

2. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

3. **Make Changes**
   - Follow the coding style
   - Add comments for complex logic
   - Update documentation if needed

4. **Test Your Changes**
   ```bash
   # Run tests
   python3 test_full.py
   
   # Test the GUI
   python3 main.py
   ```

5. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add new feature" # Use conventional commits
   ```

6. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a Pull Request on GitHub.

## Coding Guidelines

### Python Style

- Follow [PEP 8](https://peps.python.org/pep-0008/)
- Use type hints where appropriate
- Write docstrings for functions and classes
- Keep functions focused and small

### Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style (no logic change)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance

Examples:
```
feat(download): add multi-thread support
fix(auth): handle two-factor authentication timeout
docs(readme): update installation instructions
```

### Code Structure

```
project/
├── core/           # Core functionality
│   ├── __init__.py
│   ├── module1.py
│   └── module2.py
├── gui/            # GUI components
│   ├── __init__.py
│   ├── page1.py
│   └── page2.py
├── tests/          # Test files
└── docs/           # Documentation
```

## Development Setup

1. **Clone Repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/icloud-photos-migration.git
   cd icloud-photos-migration
   ```

2. **Create Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip3 install -r requirements.txt
   ```

4. **Run Application**
   ```bash
   python3 main.py
   ```

## Pull Request Process

1. Update documentation for any new features
2. Add tests for new functionality
3. Ensure all tests pass
4. Request review from maintainers
5. Address review comments

## Community

- Be respectful and inclusive
- Help others when possible
- Follow the [Code of Conduct](CODE_OF_CONDUCT.md)

## Questions?

Feel free to open an issue for any questions about contributing.

Thank you for contributing! 🎉
