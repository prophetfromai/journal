# AI Code Generation Coordination System

## Purpose
This document serves as a central coordination point for AI code generation agents working on this repository. It helps prevent conflicts by clearly defining work areas and their current status.

## Work Area Naming Convention
Each work area follows the format: `AREA-XXX` where:
- AREA: A descriptive category (e.g., FEAT, FIX, DOCS, TEST)
- XXX: A three-digit number (001-999)

Example: `FEAT-001`, `FIX-002`, `DOCS-003`

## Work Area Categories
1. FEAT: New features and enhancements
2. FIX: Bug fixes and corrections
3. DOCS: Documentation updates
4. TEST: Test suite improvements
5. REF: Code refactoring
6. PERF: Performance optimizations
7. SEC: Security improvements
8. DEP: Dependency management
9. CI: CI/CD improvements
10. API: API changes and improvements

## Current Work Areas

### Active Work Areas
| Area ID | Description | Status | Assigned To | Last Updated |
|---------|-------------|---------|-------------|--------------|
| FEAT-001 | Core system setup | COMPLETED | System | 2024-03-20 |
| FEAT-002 | AI Coordination System | IN_PROGRESS | System | 2024-03-20 |

### Available Work Areas
| Area ID | Description | Priority | Dependencies |
|---------|-------------|----------|--------------|
| FEAT-003 | Knowledge Graph Optimization | HIGH | FEAT-001 |
| FEAT-004 | Workflow Generation Enhancement | HIGH | FEAT-001 |
| TEST-001 | Unit Test Coverage | MEDIUM | FEAT-001 |
| DOCS-001 | API Documentation | MEDIUM | FEAT-001 |

## Work Area Status Definitions
- AVAILABLE: Ready for assignment
- IN_PROGRESS: Currently being worked on
- COMPLETED: Work finished and merged
- BLOCKED: Temporarily blocked by dependencies
- REVIEW: Under review
- FAILED: Failed to complete

## AI Agent Workflow

1. **Select Work Area**
   - Review the "Available Work Areas" section
   - Choose an area that:
     - Has no dependencies or all dependencies are completed
     - Matches your capabilities
     - Has appropriate priority level

2. **Create Branch**
   ```bash
   git checkout -b feature/AREA-XXX
   ```
   Example: `git checkout -b feature/FEAT-003`

3. **Update Status**
   - Change the area status to "IN_PROGRESS"
   - Add your identifier to "Assigned To"
   - Update "Last Updated" timestamp
   - Commit these changes to the AI_COORDINATION.md file

4. **Complete Work**
   - Implement the feature/fix
   - Run tests
   - Update documentation
   - Create pull request

5. **Update Status Again**
   - Change status to "COMPLETED" or "FAILED"
   - Update timestamp
   - Add any relevant notes

## Conflict Resolution
If you encounter a conflict:
1. Check if another AI agent is working on the same area
2. If yes, choose a different available area
3. If no, resolve the conflict and document the resolution

## Best Practices
1. Always check AI_COORDINATION.md before starting work
2. Update the file immediately when starting or completing work
3. Keep work areas focused and atomic
4. Document dependencies clearly
5. Update timestamps when making changes
6. Use clear, descriptive area descriptions

## Area Creation Rules
1. New areas must follow the naming convention
2. Areas must be categorized correctly
3. Dependencies must be listed
4. Priority must be specified
5. Description must be clear and specific

## Version Control Guidelines
1. Always work in feature branches
2. Keep commits atomic and focused
3. Use conventional commit messages
4. Update AI_COORDINATION.md in the same commit as feature changes

## Emergency Protocol
If you encounter a critical issue:
1. Mark the area as "BLOCKED"
2. Document the issue
3. Create a new area for the emergency fix
4. Follow the normal workflow for the emergency fix

## Maintenance
This file should be:
1. Updated with each status change
2. Reviewed regularly for accuracy
3. Cleaned up of completed/obsolete areas
4. Backed up before major changes

## Notes
- Always pull the latest changes before starting work
- Keep area descriptions up to date
- Document any blockers or issues
- Follow the established naming conventions
- Respect dependencies between areas 