# Project Structure

## Current Organization
```
.
├── .kiro/           # Kiro configuration and steering files
│   └── steering/    # AI assistant guidance documents
```

## Recommended Structure Guidelines
As the project develops, consider organizing code using these patterns:

### Source Code
- Keep source files in a dedicated directory (e.g., `src/`, `lib/`)
- Separate business logic from configuration
- Group related functionality into modules/packages

### Configuration
- Store configuration files in the project root or dedicated config directory
- Use environment-specific configuration files when needed
- Keep sensitive configuration in environment variables

### Documentation
- Maintain a comprehensive README.md in the project root
- Document APIs and interfaces
- Include setup and development instructions

### Testing
- Organize tests to mirror source code structure
- Use descriptive test file naming conventions
- Include both unit and integration tests

## File Naming Conventions
- Use consistent naming patterns across the project
- Prefer lowercase with hyphens or underscores for file names
- Use descriptive names that indicate file purpose