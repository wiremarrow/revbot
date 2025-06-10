# RevBot Backend

A modular, maintainable backend for the RevBot project that provides Claude-powered code generation and execution for Autodesk Revit.

## Features

- **Claude Integration with Tool Use**: Leverages Anthropic's Claude API with custom tools for code generation and execution
- **Modular Architecture**: Clean separation of concerns with services, models, and API layers
- **pyRevit Integration**: Execute generated code directly in Revit via pyRevit
- **Type Safety**: Full Pydantic models for request/response validation
- **Error Handling**: Comprehensive error handling and logging
- **Async Support**: Built on FastAPI with full async/await support

## Project Structure

```
backend/
├── app/
│   ├── api/           # API endpoints and routing
│   ├── core/          # Core functionality (Claude client, logging)
│   ├── models/        # Pydantic models for requests/responses
│   ├── services/      # Business logic layer
│   └── tools/         # Claude tools (code generator, pyRevit executor)
├── config/            # Configuration management
├── tests/             # Unit and integration tests
├── main.py           # FastAPI application entry point
├── requirements.txt  # Python dependencies
└── .env.example      # Environment variables template
```

## Setup

### Prerequisites
- Python 3.8+ (recommended: Python 3.11+)
- pip (Python package manager)
- Git
- Anthropic API key ([Get one here](https://console.anthropic.com/))

### Quick Start

#### Option 1: Automated Setup (Recommended)

**macOS/Linux:**
```bash
cd backend
./run.sh
```

**Windows:**
```cmd
cd backend
run.bat
```

#### Option 2: Manual Setup

**1. Navigate to backend:**
```bash
cd backend
```

**2. Create virtual environment:**

*macOS/Linux:*
```bash
python -m venv revbot
source revbot/bin/activate
```

*Windows:*
```cmd
python -m venv revbot
revbot\Scripts\activate
```

**3. Install dependencies:**
```bash
pip install -r requirements.txt
```

**4. Configure environment:**

*macOS/Linux:*
```bash
cp .env.example .env
# Edit .env and add your Anthropic API key
```

*Windows:*
```cmd
copy .env.example .env
REM Edit .env and add your Anthropic API key
```

**5. Add your API key:**
Edit the `.env` file and replace `your_anthropic_api_key_here` with your actual Anthropic API key.

**6. Run the server:**
```bash
python main.py
```

### Platform-Specific Notes

#### macOS
- Ensure you have Command Line Tools: `xcode-select --install`
- Consider using Homebrew for Python: `brew install python`

#### Windows
- Install Python from [python.org](https://python.org) or Microsoft Store
- Ensure Python is added to PATH during installation
- Use Command Prompt or PowerShell (both work)

#### Linux
- Install Python via package manager: `sudo apt install python3 python3-pip python3-venv`
- May need to install additional packages: `sudo apt install python3-dev`

## API Endpoints

### Generate Code
```bash
POST /api/v1/generate
Content-Type: application/json

{
    "prompt": "Create a wall from (0,0,0) to (10,0,0)",
    "context": {
        "active_view": "Level 1"
    },
    "temperature": 0.2
}
```

### Execute Code
```bash
POST /api/v1/execute
Content-Type: application/json

{
    "code": "# Your Python code here",
    "safe_mode": true,
    "timeout": 30
}
```

### Chat (Combined Generation + Execution)
```bash
POST /api/v1/chat?execute_code=true
Content-Type: application/json

{
    "prompt": "Create a simple room with four walls"
}
```

### List Available Tools
```bash
GET /api/v1/tools
```

## Configuration

Key configuration options in `.env`:

- `ANTHROPIC_API_KEY`: Your Anthropic API key (required)
- `CLAUDE_MODEL`: Claude model to use (default: claude-3-5-sonnet-20241022)
- `PYREVIT_PORT`: Port for pyRevit WebSocket communication
- `LOG_LEVEL`: Logging level (INFO, DEBUG, ERROR)

## Tools Available to Claude

### 1. generate_revit_code
Generates Revit API code based on natural language descriptions. Features:
- Automatic import generation
- Transaction wrapping
- Context awareness
- Code validation

### 2. execute_pyrevit_script
Executes Python scripts in Revit via pyRevit. Features:
- Safe mode validation
- Output capture
- Timeout protection
- WebSocket or CLI execution

## Example Usage

See `example_usage.py` for complete examples:

```python
import httpx

async with httpx.AsyncClient() as client:
    # Generate code
    response = await client.post(
        "http://localhost:8000/api/v1/generate",
        json={"prompt": "Create a wall on Level 1"}
    )
    
    code = response.json()["code"]
    
    # Execute code
    exec_response = await client.post(
        "http://localhost:8000/api/v1/execute",
        json={"code": code}
    )
```

## 🧪 Testing Steps

### 1. Start the Backend

**Option A: Automated Setup (Recommended)**

*Windows:*
```cmd
cd backend
run.bat
```

*macOS/Linux:*
```bash
cd backend
./run.sh
```

**Option B: Manual Setup**

*Windows:*
```cmd
cd backend
revbot\Scripts\activate.bat
python main.py
```

*macOS/Linux:*
```bash
cd backend
source revbot/bin/activate
python main.py
```

This will start the server on `http://localhost:8000`.

### 2. Test Claude Integration

*Windows:*
```cmd
cd backend
revbot\Scripts\activate.bat
python test_claude.py
```

*macOS/Linux:*
```bash
cd backend
source revbot/bin/activate
python test_claude.py
```

This verifies your API key works and Claude can respond.

### 3. Test Full API

*Windows:*
```cmd
cd backend
revbot\Scripts\activate.bat
python example_usage.py
```

*macOS/Linux:*
```bash
cd backend
source revbot/bin/activate
python example_usage.py
```

This tests all endpoints:
- Code generation from natural language
- Tool listing
- Code execution (simulation)
- Chat endpoint

### 4. Manual API Testing
You can also test with curl:

**Generate Code:**
```bash
curl -X POST "http://localhost:8000/api/v1/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create a wall from point (0,0,0) to (10,0,0)"}'
```

**List Tools:**
```bash
curl "http://localhost:8000/api/v1/tools"
```

### 5. View API Documentation
Visit `http://localhost:8000/docs` for interactive Swagger UI.

### 6. Environment Management

**Activate virtual environment:**
- Windows: `revbot\Scripts\activate.bat`
- macOS/Linux: `source revbot/bin/activate`

**Deactivate virtual environment:**
```bash
deactivate
```

## Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black .
ruff check .
```

### Adding New Tools

1. Create tool class in `app/tools/`
2. Inherit from `BaseTool`
3. Define tool parameters and execution logic
4. Register in `app/tools/__init__.py`

## Security Considerations

- Code validation before execution
- Timeout protection on all executions
- No dangerous operations allowed (exec, eval, file system access)
- API key stored securely in environment variables

## Troubleshooting

### Platform-Specific Issues

#### Windows
- **Python not found**: Ensure Python is in PATH or use `py` instead of `python`
- **Virtual environment activation fails**: Use `revbot\Scripts\activate.bat` or try PowerShell: `revbot\Scripts\Activate.ps1`
- **Permission errors**: Run Command Prompt as Administrator
- **SSL certificate errors**: Update certificates: `pip install --upgrade certifi`

#### macOS
- **Permission denied**: Use `chmod +x run.sh` to make script executable
- **Python version issues**: Use `python3` instead of `python`
- **SSL errors**: Update certificates: `/Applications/Python\ 3.x/Install\ Certificates.command`

#### Linux
- **Module not found**: Install dev packages: `sudo apt install python3-dev build-essential`
- **Permission errors**: Don't use `sudo` with pip in virtual environments
- **Port conflicts**: Change port in `.env` file if 8000 is occupied

### API Issues

#### pyRevit Connection Issues
- Ensure pyRevit is installed and running
- Check WebSocket port configuration (default: 8080)
- Try CLI fallback mode by commenting out `PYREVIT_PORT` in `.env`
- Windows: Ensure pyRevit CLI is in PATH

#### Code Generation Issues
- Verify Anthropic API key is correct
- Check API rate limits (you may hit limits during testing)
- Review generated code for context accuracy
- Ensure internet connection for API calls

#### Common Error Messages
- `ImportError: cannot import name 'X'`: Update packages with `pip install --upgrade -r requirements.txt`
- `AuthenticationError`: Check your API key in `.env` file
- `ConnectionError`: Check internet connection and firewall settings
- `ModuleNotFoundError`: Ensure virtual environment is activated

## Next Steps

1. Add more sophisticated code generation patterns
2. Implement code caching for common operations
3. Add user authentication and rate limiting
4. Create frontend interface
5. Add more Revit-specific tools