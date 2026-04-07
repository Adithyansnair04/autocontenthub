# CogenLab

CogenLab is a multi-agent AI pipeline that transforms source material into platform-ready, brand-aligned content. It uses specialized AI agents to analyze brand styles, extract facts, identify market trends and draft copy for multiple platforms autonomously.

## Project Structure

```text
.
├── backend/
│   ├── agents/          # AI agents (Brand Analyst, Researcher, Copywriter, Editor)
│   ├── models/          # Data models and schemas
│   ├── services/        # Orchestrator and LLM clients
│   ├── config.py        # Configuration variables
│   ├── main.py          # FastAPI application
│   └── requirements.txt # Python dependencies
└── frontend/
    └── app.py           # Streamlit UI
```

## Setup Instructions

1. **Install Dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   Create a `.env` file in the root directory:
   ```env
   LLM_PROVIDER=nvidia
   NVIDIA_API_KEY=your_api_key
   NVIDIA_MODEL=meta/llama-3.1-8b-instruct
   NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
   ```
   *(Note: Groq and Ollama are also supported as alternative LLM providers).*

## Running the Application

You must start both the backend API and frontend UI in separate terminal windows.

**Start the Backend:**
```bash
cd backend
uvicorn main:app --reload --port 8000
```

**Start the Frontend:**
```bash
cd frontend
streamlit run app.py
```

## How It Works

1. **Input**: Provide source material, brand URL, and target audience.
2. **Analysis**: AI agents determine the brand's voice and gather facts.
3. **Drafting**: Platform-specific content is generated for LinkedIn, X (Twitter), Blogs, and Email.
4. **Review**: An autonomous editor scores and refines the drafts before delivering the final content.
