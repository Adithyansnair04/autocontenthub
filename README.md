# CogenLab

**CogenLab** — A multi-agent AI pipeline that transforms source material (text or URLs) into platform-ready, brand-aligned content. The system leverages specialized AI agents to analyze brand styles, extract facts, identify industry trends, draft content for multiple platforms, and autonomously review and revise the output. It features a FastAPI backend and a sleek, minimalist Streamlit frontend.

## 🚀 Key Features

*   **Multi-Agent Architecture**: The pipeline is powered by distinct AI agents handling specific parts of the workflow:
    *   **Brand Analyst**: Analyzes brand websites to deduce voice, tone, and stylistic characteristics.
    *   **Researcher**: Ingests source material (text or a URL), extracts a "Source of Truth" (core facts, product info), and flags ambiguous statements.
    *   **Trend Analyst**: Provides real-time industry trend context, identifying dominant tensions and fresh angles to make the content timely and resonant.
    *   **Copywriter**: Generates platform-specific content drafts relying on facts, brand guidelines, and trend contexts.
    *   **Editor**: Evaluates drafts using a strict scoring system, checking for hallucinations, tone inconsistencies, and genericness. It can trigger autonomous revision loops.
*   **Multiple Output Channels**: Automatically generates specifically formatted content for **LinkedIn**, **Twitter**, **Blogs**, and **Email**.
*   **Flexible LLM Integration**: The factory supports multiple LLM providers:
    *   **NVIDIA NIM** (e.g., `meta/llama-3.1-8b-instruct`)
    *   **Ollama** for local running (e.g., `llama3.1`)
    *   **Groq** (e.g., `llama-3.1-70b-versatile`)
*   **Modern Frontend UI**: Built with Streamlit, presenting a dark-themed, minimalist, Apple-inspired interface with real-time agent logging.
*   **Robust Backend**: Async FastAPI backend that handles the pipeline orchestrations smoothly.

## 📁 Project Structure

```
.
├── backend/
│   ├── agents/          # AI agents (Brand Analyst, Researcher, Copywriter, etc.)
│   ├── models/          # Pydantic schemas and data models
│   ├── services/        # Orchestrator, web scrapers, and LLM clients
│   ├── config.py        # Environment variables and settings
│   ├── main.py          # FastAPI application entry point
│   └── requirements.txt # Python dependencies
├── frontend/
│   ├── app.py           # Streamlit UI implementation
└── README.md
```

## 🛠️ Setup Instructions

### 1. Prerequisites

*   Python 3.11 (or higher)
*   Virtual environment (recommended)

### 2. Installation

Clone the repository and install the backend dependencies (which also power the frontend):

```bash
cd backend
pip install -r requirements.txt
```

### 3. Environment Variables

Create a `.env` file in the root navigation with your configuration:

```env
# Choose your provider: "nvidia", "ollama", or "groq"
LLM_PROVIDER=nvidia

# NVIDIA NIM (Default)
NVIDIA_API_KEY=your_nvidia_api_key_here
NVIDIA_MODEL=meta/llama-3.1-8b-instruct
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1

# Groq
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-70b-versatile

# Ollama (Local)
OLLAMA_MODEL=llama3.1

# Editor Settings
MAX_EDITOR_RETRIES=2
```

## ⚙️ Running the Application

You'll need two terminal windows to run both the backend API and the frontend UI.

### Start the Backend (Terminal 1)

```bash
cd backend
uvicorn main:app --reload --port 8000
```
*The FastAPI server will be available at `http://localhost:8000`. You can test endpoints via `http://localhost:8000/docs`.*

### Start the Frontend (Terminal 2)

```bash
cd frontend
streamlit run app.py
```
*The Streamlit application will automatically launch in your default web browser.*

## 🧠 How It Works

1.  **Input:** The user provides source material (a link or raw text), an optional brand URL, the target audience, and selects the desired platform domains.
2.  **Analyzation:** The Orchestrator kicks off the **Brand Analyst** to figure out the tone of voice and the **Researcher** to extract a unified Fact Sheet.
3.  **Contextualization:** The **Trend Analyst** researches the current landscape to anchor the generated content in timely relevance.
4.  **Creation:** The **Copywriter** drafts the posts, leveraging the combined outputs of the previous agents.
5.  **Review & Polish:** The **Editor** steps in to review the copywriter's drafts. If a draft doesn't meet the score threshold, the Editor leaves specific feedback, causing the Copywriter to revise the draft autonomously. 
6.  **Delivery:** Final, platform-ready outputs and detailed pipeline logs are presented to the user.
