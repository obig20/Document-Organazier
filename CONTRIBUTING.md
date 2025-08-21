# Contributing to AI Document Organizer

Thank you for your interest in contributing to the AI Document Organizer! We welcome contributions from everyone.

## 🛠️ Development Setup

1. **Fork the repository**

   
   ```bash
   # Clone your fork
   git clone https://github.com/yourusername/ai-document-organizer.git
   cd ai-document-organizer
   
   # Add upstream remote
   git remote add upstream https://github.com/original-owner/ai-document-organizer.git
   ```


2. **Set up the development environment**

   
   ```bash
   # Create and activate virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install development dependencies
   pip install -r requirements-dev.txt
   ```


3. **Set up pre-commit hooks**

   
   ```bash
   pre-commit install
   ```


## 🚦 Development Workflow

1. **Create a new branch** for your feature or bugfix

   
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b bugfix/issue-number-description
   ```


2. **Make your changes** following the code style guidelines

3. **Run tests** to ensure everything works

   
   ```bash
   pytest
   ```


4. **Commit your changes** with a descriptive message

   
   ```bash
   git commit -m "feat: add new feature"
   # or
   git commit -m "fix: resolve issue with document processing"
   ```


5. **Push your changes** to your fork

   
   ```bash
   git push origin your-branch-name
   ```


6. **Create a Pull Request** from your fork to the main repository

## 📝 Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code
- Use type hints for all function parameters and return values
- Keep lines under 100 characters
- Use docstrings for all public functions and classes
- Write tests for new features and bug fixes

## 🧪 Testing

- Write unit tests for new features
- Ensure all tests pass before submitting a PR
- Update tests when adding new features or fixing bugs

## 📖 Documentation

- Update the README.md when adding new features
- Add docstrings to all new functions and classes
- Document any environment variables or configuration changes

## 🐛 Reporting Issues

When reporting issues, please include:

1. A clear title and description
2. Steps to reproduce the issue
3. Expected vs. actual behavior
4. Any relevant error messages or logs
5. System information (OS, Python version, etc.)

## 🤝 Code of Conduct

Please note that this project is governed by the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## 📬 Questions?

If you have any questions, feel free to open an issue or reach out to the maintainers.
