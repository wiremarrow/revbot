# RevitAI: AI Programming Agent for Autodesk Revit

A nimble, API-first AI programming assistant that brings intelligent code generation to Revit 2026, designed for rapid prototyping and real-world impact in the AEC industry.

## 🎯 Project Vision

Create a practical, high-performance AI agent that can:
- Generate accurate Revit API code using state-of-the-art LLMs
- Access Revit documentation instantly through semantic search
- Execute scripts directly in Revit via pyRevit
- Learn from interactions to improve over time

## 🏗️ Lean Architecture (API-First Approach)

### Core Stack
- **LLM**: Claude 3.5 Sonnet API (best-in-class for code generation)
- **Embeddings**: OpenAI text-embedding-3-large
- **Vector Store**: Pinecone (serverless, zero-maintenance)
- **Backend**: FastAPI (async Python)
- **Frontend**: React + Vite (simple chat interface)
- **Revit Bridge**: pyRevit for script execution

### Why This Stack?
- **No GPU needed**: All AI runs via APIs
- **Fast iteration**: Change models with one line of code
- **Production-ready**: APIs handle scaling automatically
- **Cost-effective**: Pay only for what you use
- **Best quality**: Access to cutting-edge models immediately

## 📋 Simple Architecture

```
┌─────────────────┐
│   React Chat    │  ← User sends queries
└────────┬────────┘
         │ WebSocket
┌────────▼────────┐
│   FastAPI       │  ← Orchestrates the flow
│   Backend       │
└────┬───────┬────┘
     │       │
     │       └──────────────┐
     │                      │
┌────▼────┐          ┌──────▼─────┐
│ Pinecone │          │ Claude API │
│ (Search) │          │ (Generate) │
└─────────┘          └────────────┘
     ↑                      │
     │                      │
Revit Docs              pyRevit
(embedded)             (execute)
```

## 🚀 Implementation Plan

### Week 1: Documentation Pipeline
```python
# 1. Scrape Revit 2026 docs
scraper = RevitDocScraper()
docs = scraper.scrape_all()

# 2. Process and chunk
chunks = chunk_documents(docs, max_tokens=500)

# 3. Generate embeddings
embeddings = openai.embed(chunks)

# 4. Store in Pinecone
pinecone.upsert(vectors=embeddings, metadata=chunks)
```

### Week 2: Core API
```python
# Simple FastAPI endpoint
@app.post("/generate")
async def generate_code(query: str):
    # 1. Find relevant docs
    relevant_docs = pinecone.query(query, top_k=5)
    
    # 2. Build context
    context = "\n".join(relevant_docs)
    
    # 3. Generate with Claude
    response = anthropic.messages.create(
        model="claude-3-5-sonnet-20241022",
        messages=[{
            "role": "system",
            "content": "You are a Revit API expert. Generate clean, working code."
        },
        {
            "role": "user",
            "content": f"Context:\n{context}\n\nTask: {query}"
        }]
    )
    
    return {"code": response.content}
```

### Week 3: pyRevit Integration
```python
# Execute generated code safely
@app.post("/execute")
async def execute_script(code: str):
    # 1. Validate code
    validation = validate_revit_code(code)
    if not validation.is_safe:
        return {"error": validation.message}
    
    # 2. Send to pyRevit
    result = pyrevit_bridge.execute(code)
    
    # 3. Return results
    return {"output": result.output, "errors": result.errors}
```

### Week 4: Frontend & Polish
- Simple React chat interface
- Code highlighting with Monaco Editor
- Conversation history
- Error handling and retry logic

## 🔧 Development Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- Revit 2026 + pyRevit installed
- API Keys: Claude, OpenAI, Pinecone

### Quick Start
```bash
# Clone and setup
git clone https://github.com/yourusername/revitai.git
cd revitai

# Backend setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install fastapi uvicorn anthropic openai pinecone-client

# Frontend setup
cd frontend
npm install

# Configure API keys
cp .env.example .env
# Add your API keys to .env

# Run everything
# Terminal 1: Backend
uvicorn main:app --reload

# Terminal 2: Frontend
npm run dev
```

## 📊 Cost Estimation

For prototype with 100 queries/day:
- Claude API: ~$3/day
- OpenAI Embeddings: ~$0.10/day (one-time for docs)
- Pinecone: Free tier sufficient
- **Total**: < $100/month

## 🎯 Minimal Viable Features

### Phase 1: Core Loop (MVP)
- [ ] Scrape and embed Revit 2026 documentation
- [ ] Basic chat interface
- [ ] Generate Revit code with Claude
- [ ] Display generated code with syntax highlighting

### Phase 2: Execution
- [ ] pyRevit bridge for safe execution
- [ ] Error handling and debugging info
- [ ] Save/load conversation history

### Phase 3: Enhancement
- [ ] Code validation before execution
- [ ] Common templates and snippets
- [ ] Multi-turn conversations with context
- [ ] Export scripts as .py files

## 🚦 Success Metrics

- Generate working Revit code in < 3 seconds
- 80%+ success rate on common tasks
- Execute scripts without leaving chat interface
- Handle multi-turn clarification naturally

## 🔐 Security

- API keys stored securely in environment variables
- Code execution sandboxed through pyRevit
- Input validation on all user queries
- Rate limiting to prevent abuse

## 📈 Future Enhancements

Once prototype is validated:
- Fine-tune models on Revit-specific code
- Add visual feedback (screenshots from Revit)
- Build library of verified code patterns
- Community sharing of templates

---

**Key Philosophy**: Start simple, ship fast, iterate based on real usage. This architecture can be built by one developer in 4 weeks and scaled up as needed.