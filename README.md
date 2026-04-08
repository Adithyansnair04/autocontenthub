# CogenLab

**Deployed Link:** [https://cogenlab.streamlit.app/](https://cogenlab.streamlit.app/)

## The Problem
Creating and formatting content for various digital platforms (like LinkedIn, X/Twitter, and Emails) is incredibly time-consuming. Maintaining a consistent brand voice across all mediums while ensuring the content feels fresh requires significant manual editorial effort.

## The Solution
CogenLab is an autonomous content factory that solves this by orchestrating specialized AI agents. It uses a Brand Analyst to scrape and emulate the company's voice, a Researcher to extract and verify facts, a Trend Analyst to analyse latest trends in different channel and market and a Copywriter to draft platform-optimized posts. Finally, an autonomous Editor agent reviews and refines the copy to ensure high-quality, publication-ready output.

## Additional Features
* **5-Agent Pipeline:** Utilizes five distinct agents operating in sequence:
  * **Brand Analyser:** Visits brand URLs and scrapes websites to accurately acquire and emulate the company's unique voice and tone.
  * **Researcher:** Sifts through raw source materials to aggregate and verify essential factual information.
  * **Trend Analyser:** Injects real-time channel trends and current market contexts directly into the generation pipeline.
  * **Copywriter:** Takes the brand playbook, researched facts, and trend contexts to draft initial platform-specific versions of the content.
  * **Editor:** Autonomously reviews drafts, scores the content, and refines the language through targeted revision loops prior to finalizing the content.
* **Special Filtering for Channels:** Features specialized filtering rules to uniquely constrain and format copy appropriately for different output platforms (e.g., LinkedIn, Twitter, Email, Blogs).
* **Automated Content Scoring:** The Editor agent calculates and provides a final numerical content score to evaluate the draft's overall quality and brand alignment before finalization.

## Tech Stack
* **Programming Languages:** Python
* **Frameworks:** FastAPI (Backend API), Streamlit (Frontend UI), Pydantic (Data validation)
* **Databases:** None (Stateless execution)
* **APIs or third-party tools:** NVIDIA NIM API (Primary LLM using Meta LLaMA 3.1), Groq Cloud API, Ollama, BeautifulSoup4 & Requests (Web scraping), Uvicorn (ASGI Server)

## Project Structure
```text
.
├── backend/
│   ├── agents/          # AI agents (Brand Analyst, Researcher, Trend Analyst, Copywriter, Editor)
│   ├── models/          # Data models and schemas (Pydantic)
│   ├── services/        # Core services (Orchestrator, Scraper, LLM clients)
│   ├── config.py        # Configuration variables
│   ├── main.py          # FastAPI application
│   └── requirements.txt # Python dependencies
└── frontend/
    └── app.py           # Streamlit UI
```

## Setup Instructions

1. **Install Dependencies**
   Navigate to the backend directory and install the necessary Python packages:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   Create a `.env` file in the root directory with the appropriate keys:
   ```env
   LLM_PROVIDER=nvidia
   NVIDIA_API_KEY=your_api_key
   NVIDIA_MODEL=meta/llama-3.1-8b-instruct
   NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
   ```

3. **Run the Project Locally**
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
