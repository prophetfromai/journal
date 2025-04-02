# Autonomous AI System with DeepSeek

This is an autonomous AI system that leverages DeepSeek as its local LLM to perform various tasks related to knowledge extraction, system building, and self-improvement.

## Quick Start for AI Code Generation

1. **Install Required Tools:**
   - Download and install [Cursor](https://cursor.sh) - This is your AI-powered IDE
   - Download and install [LM Studio](https://lmstudio.ai) - For running the local LLM

2. **Set Up LM Studio:**
   - Open LM Studio
   - Load the `deepseek-r1-distill-qwen-7b` model
   - Click "Start Server" (it will run on port 1234)

3. **Open in Cursor:**
   - Clone this repo: `git clone https://github.com/prophetfromai/journal.git`
   - Open the `journal` folder in Cursor
   - Use Cursor's AI chat console to interact with the codebase

That's it! The AI will use itself to write and improve the codebase. You can use the chat console to request features, fixes, or improvements.

---

## Detailed Setup (Optional)

If you want to run the system directly (without Cursor AI):

1. Set up Python environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
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

## Development

This project follows a systematic approach to autonomous development with rate limiting to ensure controlled evolution.

1. Create a new feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit:
   ```bash
   git add .
   git commit -m "feat: Your feature description"
   ```

3. Push changes:
   ```bash
   git push origin feature/your-feature-name
   ```

4. Create a pull request on GitHub

## License

MIT License 