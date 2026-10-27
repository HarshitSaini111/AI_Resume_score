from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

from resume_parser import analyze_resumes


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="AI Resume Screening API",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():

    return {
        "message": "AI Resume Screening API is running"
    }


# ============================================================
# ANALYZE ONE RESUME
# ============================================================

@app.post("/api/analyze")
async def analyze(
    job_description: str = Form(...),
    resume: UploadFile = File(...)
):

    # --------------------------------------------------------
    # Check file
    # --------------------------------------------------------

    if not resume.filename:

        return {
            "success": False,
            "error": "No resume selected."
        }

    # --------------------------------------------------------
    # Check extension
    # --------------------------------------------------------

    if not resume.filename.lower().endswith(
        (".pdf", ".docx")
    ):

        return {
            "success": False,
            "error": "Only PDF and DOCX files are supported."
        }

    # --------------------------------------------------------
    # Read file into memory
    # --------------------------------------------------------

    file_bytes = await resume.read()

    # --------------------------------------------------------
    # Analyze
    # --------------------------------------------------------

    try:

        result = analyze_resumes(
            job_description,
            [
                (
                    resume.filename,
                    file_bytes
                )
            ]
        )

        return {
            "success": True,
            **result
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }