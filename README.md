# ResumeScore --- AI-Powered Resume Screening

[![Live
Demo](https://img.shields.io/badge/Live%20Demo-Vercel-black?logo=vercel)](https://ai-resume-score-nine.vercel.app)
[![Backend
API](https://img.shields.io/badge/API-Render-46E3B7?logo=render)](https://ai-resume-score-08ih.onrender.com/docs)
[![Frontend](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-646CFF?logo=vite)](https://vite.dev/)

ResumeScore is a full-stack web application that evaluates how closely a
candidate's resume aligns with a job description. Upload a PDF or DOCX
resume, enter the job requirements, and receive a match score with
structured candidate insights and an AI-generated assessment.

> **Responsible use:** This project is a screening aid for learning and
> decision support. Its score and AI-generated assessment may be
> imperfect and should not be used as the sole basis for hiring
> decisions.

## Live Application

-   **Frontend:** https://ai-resume-score-nine.vercel.app
-   **Backend API documentation:**
    https://ai-resume-score-08ih.onrender.com/docs

## Features

-   **PDF and DOCX uploads** --- extract text from supported resume
    documents.
-   **Job description analysis** --- structure role requirements for
    comparison.
-   **AI-assisted resume parsing** --- extract candidate details such as
    skills, experience, education, projects, and certifications when
    present.
-   **Resume-to-job matching** --- generate a compatibility score and
    supporting analysis.
-   **Matching skills** --- highlight skills identified as relevant to
    the job description.
-   **Missing important skills** --- show important requirements not
    identified in the resume.
-   **AI-generated verdict** --- produce a readable summary of the
    candidate's apparent fit.
-   **Candidate overview** --- present the analysis in a web interface.
-   **REST API** --- FastAPI endpoint with interactive Swagger
    documentation.

## Technology Stack

  Layer                       Technologies
  --------------------------- ----------------------------------------------------
  Frontend                    React, Vite, JavaScript, CSS
  Backend                     Python, FastAPI, Uvicorn
  AI integration              Groq API (configured model: `openai/gpt-oss-120b`)
  Data validation             Pydantic
  PDF parsing                 `pypdf`
  DOCX parsing                `python-docx`
  Environment configuration   `python-dotenv`
  File uploads                `python-multipart`, FastAPI `UploadFile`
  Deployment                  Vercel (frontend), Render (backend)
  Version control             Git and GitHub

## How It Works

1.  The user enters a job description and uploads a PDF or DOCX resume.
2.  The React frontend submits the form data to the FastAPI backend.
3.  The backend extracts text from the uploaded document.
4.  AI-assisted parsing structures relevant information from the resume
    and job description.
5.  The matching workflow evaluates the candidate profile against the
    role requirements.
6.  The backend prepares a score, matching and missing-skill details,
    and an AI-generated verdict.
7.  The frontend displays the analysis results.

## Architecture

``` text
User
 |
 v
React + Vite frontend (Vercel)
 |
 | POST /api/analyze
 | multipart/form-data
 v
FastAPI backend (Render)
 |
 +--> PDF/DOCX text extraction
 |
 +--> Groq API for AI-assisted parsing and evaluation
 |
 v
Structured analysis response
 |
 v
Results displayed in the frontend
```

## Project Structure

``` text
AI_Resume_score/
├── backend/
│   ├── main.py
│   ├── resume_parser.py
│   ├── pyproject.toml
│   └── uv.lock
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.js
└── README.md
```

This tree highlights the main application files; supporting
configuration and styling files may also be present.

## Run Locally

### Prerequisites

-   Python version compatible with `backend/pyproject.toml`
-   Node.js and npm
-   A Groq API key

### 1. Clone the repository

``` bash
git clone https://github.com/HarshitSaini111/AI_Resume_score.git
cd AI_Resume_score
```

### 2. Set up the backend

``` bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

On Windows, activate the virtual environment with:

``` powershell
.venv\Scripts\activate
```

Create a file named `backend/.env` and add your Groq API key:

``` env
GROQ_API_KEY=your_groq_api_key_here
```

Start the API from the `backend/` directory:

``` bash
uvicorn main:app --reload
```

The backend should be available at `http://127.0.0.1:8000`.

-   API status: `http://127.0.0.1:8000/`
-   Interactive API docs: `http://127.0.0.1:8000/docs`

### 3. Set up the frontend

Open a second terminal from the repository root:

``` bash
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite, usually `http://localhost:5173`.

### 4. Configure frontend/backend communication

The frontend must call the backend API endpoint:

``` text
POST /api/analyze
```

For local development, use:

``` text
http://127.0.0.1:8000/api/analyze
```

For production, the frontend should use the deployed Render URL with
`/api/analyze` appended. The backend CORS allowlist must include the
exact deployed Vercel origin:

``` text
https://ai-resume-score-nine.vercel.app
```

The origin should not have a trailing slash.

## API Reference

### `GET /`

Returns a status message indicating that the API is running.

### `POST /api/analyze`

Analyzes a resume against a job description.

-   **Content type:** `multipart/form-data`
-   **Job description field:** `job_description`
-   **Resume field:** `resume`
-   **Supported file types:** PDF and DOCX

Example request:

``` bash
curl -X POST \
  "http://127.0.0.1:8000/api/analyze" \
  -F "job_description=Junior Software Developer with Python and SQL skills" \
  -F "resume=@resume.pdf"
```

For the exact request and response schema, open the backend's `/docs`
page.

## Deployment

### Frontend --- Vercel

-   Import the GitHub repository.
-   Set **Root Directory** to `frontend`.
-   Select **Vite** as the framework preset.
-   Install command: `npm install`
-   Build command: `npm run build`
-   Output directory: `dist`

### Backend --- Render

-   Create a Web Service from the GitHub repository.
-   Set **Root Directory** to `backend`.
-   Install dependencies using the project configuration
    (`pip install -e .`).
-   Start command:

``` bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

-   Set `GROQ_API_KEY` in Render's environment variables.
-   Configure CORS to allow the deployed frontend origin.

Free hosting instances may take time to wake after being idle, so the
first request can be slower than subsequent requests.

## Security and Privacy

-   Never commit `.env` files or API keys to GitHub.
-   Keep the Groq API key on the backend; do not expose it in frontend
    code or a `VITE_*` variable.
-   Treat uploaded resumes as confidential personal information.
-   Avoid logging or sharing sensitive candidate data.
-   Verify AI-generated claims against the original resume.
-   Use the score as one signal for review, not as a definitive measure
    of candidate quality.

## Limitations

-   Results depend on the quality of extracted resume text and the
    supplied job description.
-   AI parsing and generated conclusions can be incomplete or incorrect.
-   Scanned/image-only PDFs may not yield useful text unless OCR is
    added.
-   A missing skill in the extracted resume does not prove that the
    candidate lacks that skill.
-   Match scores are estimates produced by the application's current
    matching workflow.

## Future Improvements

-   Configure the backend URL through an environment variable.
-   Add automated tests for parsing, matching, uploads, and API
    responses.
-   Improve score transparency with a clearer score breakdown.
-   Add OCR support for scanned resumes.
-   Add batch screening and candidate comparison.
-   Improve validation, upload limits, and error reporting.
-   Add authentication and recruiter-specific workflows where needed.

## Author

**Harshit Saini**\
GitHub: [HarshitSaini111](https://github.com/HarshitSaini111)

------------------------------------------------------------------------

Built as a practical full-stack project exploring AI-assisted document
parsing, resume matching, REST API development, and cloud deployment.
