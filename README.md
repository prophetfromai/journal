# Autonomous AI System with DeepSeek

This is an autonomous AI system that leverages DeepSeek as its local LLM to perform various tasks related to knowledge extraction, system building, and self-improvement.

## Core Features

- Local LLM Integration with DeepSeek
- Knowledge Graph Management
- Automated AI Agent Workflow Generation
- CI/CD Integration
- Self-Improvement and Knowledge Extraction
- Content Processing (Books, Papers, Videos)

## Project Structure

```
.
├── src/
│   ├── core/                 # Core system components
│   ├── agents/              # AI agent implementations
│   ├── knowledge_graph/     # Knowledge graph management
│   ├── tools/              # Utility tools and helpers
│   └── workflows/          # Automated workflow definitions
├── config/                 # Configuration files
├── data/                  # Data storage
├── docs/                  # Documentation
└── tests/                 # Test suite
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure DeepSeek:
```bash
cp config/deepseek.example.yaml config/deepseek.yaml
# Edit config/deepseek.yaml with your settings
```

3. Initialize the knowledge graph:
```bash
python src/knowledge_graph/init_graph.py
```

## Usage

[Documentation to be added]

## Development

This project follows a systematic approach to autonomous development with rate limiting to ensure controlled evolution.

## License

MIT License 