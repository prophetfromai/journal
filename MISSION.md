# Autonomous AI System Mission Document

## Project Context
This repository contains an autonomous AI system that leverages DeepSeek as its local LLM to perform various tasks related to knowledge extraction, system building, and self-improvement. The system is designed to be a collaborative platform where multiple users can work on their own branches while contributing to a shared knowledge base.

## Core Mission
The system aims to:
1. Build and maintain tools in its own git repositories to assist with various tasks
2. Process and integrate diverse content (text, video, papers) into a centralized knowledge graph
3. Generate and execute AI agent workflows automatically
4. Perform CI/CD tasks including code reviews
5. Systematically extract and organize knowledge about AI code generation
6. Process and integrate books, papers, and videos into actionable knowledge

## System Architecture
The system is built with the following key components:
- DeepSeekClient: Handles LLM interactions with rate limiting
- KnowledgeGraphManager: Manages Neo4j-based knowledge storage
- WorkflowManager: Handles AI agent workflow generation and execution
- ContentProcessor: Processes various content types (books, papers, videos)

## Knowledge Graph Structure
The knowledge graph uses the following schema:
- Nodes: Knowledge (content, type, metadata)
- Relationships: RELATES_TO (type, properties)
- Indexes: type, created_at, updated_at
- Constraints: unique id

## Workflow Types
The system supports the following workflow types:
1. Code Generation
2. Knowledge Extraction
3. Git Operations
4. Content Processing

## Rate Limiting and Safety
The system implements rate limiting to ensure controlled evolution:
- Max requests per minute: 60
- Max tokens per request: 4000
- Cooldown period: 5 seconds
- Max concurrent workflows: 5

## Content Processing Capabilities
The system can process:
- Books (text files)
- Scientific papers
- YouTube videos (with transcripts)
- Web pages
- Generated code

## Git Integration
The system uses Git for:
- Version control
- Branch management
- Code review automation
- Workflow storage

## Self-Improvement Mechanisms
The system includes:
- Knowledge extraction intervals
- Validation thresholds
- Update rate limiting
- Automated testing

## API Endpoints
The system exposes the following endpoints:
- /process-content: Process various content types
- /generate-workflow: Generate AI agent workflows
- /execute-workflow: Execute workflows
- /active-workflows: Monitor active workflows
- /knowledge: Query the knowledge graph

## Development Guidelines
1. All code changes must be made in feature branches
2. Rate limiting must be respected
3. Knowledge graph updates must be validated
4. Workflows must be tested before execution
5. Content processing must respect size limits

## Integration Points
The system integrates with:
- DeepSeek LLM
- Neo4j Database
- Git Repositories
- YouTube API
- Web Scraping Tools

## Safety Constraints
1. Rate limiting on all external API calls
2. Content size limits
3. Validation thresholds
4. Concurrent operation limits
5. Error handling and recovery

## Knowledge Extraction Rules
1. Extract structured knowledge from content
2. Maintain relationships between knowledge nodes
3. Update metadata with timestamps
4. Validate extracted knowledge
5. Respect rate limits

## Workflow Generation Rules
1. Generate step-by-step workflows
2. Include validation steps
3. Implement error handling
4. Respect rate limits
5. Store workflows in knowledge graph

## Content Processing Rules
1. Validate content types
2. Respect size limits
3. Extract structured knowledge
4. Store in knowledge graph
5. Maintain relationships

## Git Operation Rules
1. Use feature branches
2. Implement proper commit messages
3. Include code reviews
4. Respect concurrent operation limits
5. Maintain workflow history

## Testing Requirements
1. Unit tests for all components
2. Integration tests for workflows
3. Knowledge graph validation
4. Rate limit testing
5. Error handling testing

## Documentation Requirements
1. API documentation
2. Workflow documentation
3. Knowledge graph schema
4. Rate limiting rules
5. Safety constraints

## Mission Continuation
AI agents working on this project should:
1. Respect all rate limits and safety constraints
2. Maintain knowledge graph integrity
3. Follow development guidelines
4. Implement proper testing
5. Document all changes
6. Work within feature branches
7. Validate all operations
8. Handle errors gracefully
9. Update documentation as needed
10. Contribute to system improvement

## Version Control Guidelines
1. Create feature branches for all changes
2. Use descriptive commit messages
3. Include tests with changes
4. Update documentation
5. Follow code review process

## Knowledge Graph Guidelines
1. Maintain node relationships
2. Update metadata
3. Validate content
4. Respect rate limits
5. Handle errors

## Workflow Guidelines
1. Generate structured workflows
2. Include validation steps
3. Handle errors
4. Respect rate limits
5. Document workflows

## Content Processing Guidelines
1. Validate content types
2. Respect size limits
3. Extract knowledge
4. Update graph
5. Handle errors

## Safety Guidelines
1. Respect rate limits
2. Validate operations
3. Handle errors
4. Monitor resources
5. Log operations

## Integration Guidelines
1. Validate inputs
2. Handle errors
3. Respect rate limits
4. Update documentation
5. Test integrations 