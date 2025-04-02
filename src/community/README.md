# Vibe Coding Community Platform

A platform for developers to collaborate, learn, and grow together using AI Code Generation.

## Features

- User profiles and authentication
- Project sharing and collaboration
- Community resources and guides
- Events and workshops
- Discussions and Q&A
- Achievement system
- AI-assisted development tools

## Getting Started

### Prerequisites

- Python 3.8+
- SQLite3
- Virtual environment

### Installation

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Initialize the database:
   ```bash
   python -m src.community.platform.database
   ```

4. Start the development server:
   ```bash
   uvicorn src.main:app --reload
   ```

The API will be available at `http://localhost:8000`

## API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Community Guidelines

1. **Be Respectful**
   - Treat all community members with respect
   - Use inclusive language
   - Be constructive in feedback

2. **Share Knowledge**
   - Document your experiences
   - Share useful resources
   - Help others learn

3. **Collaborate**
   - Work on projects together
   - Review each other's code
   - Share feedback

4. **Learn Together**
   - Participate in events
   - Share learning resources
   - Mentor others

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Events

### Weekly Meetups
- Every Wednesday at 7 PM UTC
- Focus on AI-assisted development
- Show and tell sessions
- Q&A and discussions

### Workshops
- Monthly deep-dive sessions
- Hands-on coding exercises
- Best practices sharing
- Tool demonstrations

### Hackathons
- Quarterly events
- Collaborative projects
- Learning opportunities
- Networking

## Resources

### Learning Materials
- Getting started guides
- Video tutorials
- Code examples
- Best practices

### Tools & Templates
- Prompt templates
- Project templates
- Configuration files
- Code snippets

### Community Support
- Discussion forums
- Discord server
- GitHub discussions
- Office hours

## Achievement System

Earn badges and recognition for:
- Contributing to projects
- Sharing resources
- Helping others
- Participating in events
- Creating content

## Contact

- Email: community@vibecoding.dev
- Discord: [Join our server](https://discord.gg/vibecoding)
- GitHub: [Follow us](https://github.com/vibecoding)

## License

MIT License - See LICENSE file for details 