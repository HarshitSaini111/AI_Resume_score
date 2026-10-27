import os
import json
from io import BytesIO
from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel
from pypdf import PdfReader
from docx import Document
# ============================================================
# ENVIRONMENT
# ============================================================
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY .env file mein nahi mili.")
client = Groq(api_key=GROQ_API_KEY)
MODEL = "openai/gpt-oss-120b"
# ============================================================
# PYDANTIC MODELS
# ============================================================
class JobD(BaseModel):
    role: str
    required_skills: list[str]
    preferred_skills: list[str]
    minimum_experience: float | None
    education_requirements: list[str]
    responsibilities: list[str]
class MatchResult(BaseModel):
    score: float
    details: dict
class Experience(BaseModel):
    company: str | None = None
    role: str | None = None
    duration: str | None = None
    description: str | None = None
    skills_used: list[str] = []
class Resume(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    total_experience_years: float | None = None
    skills: list[str] = []
    experiences: list[Experience] = []
    education: list[str] = []
    projects: list[str] = []
    certifications: list[str] = []
# ============================================================
# JOB DESCRIPTION PARSER
# ============================================================
def parse_job_description(job_description: str) -> JobD:
    job_schema = JobD.model_json_schema()
    system_prompt = f"""
You are an expert HR assistant.
Your job is to analyze a job description and extract
structured information from it.
Return ONLY valid JSON matching this schema:
{job_schema}
IMPORTANT:
1. Do NOT return the schema itself.
2. Do NOT return fields like "properties", "title" or "type".
3. Fill the schema with actual information extracted
   from the job description.
4. If minimum experience is not mentioned, return null.
5. If information for a list is missing, return an empty list.
6. Do not invent information.
"""
    user_prompt = f"""
Analyze the following job description:
{job_description}
"""
    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": user_prompt
        }
    ]
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        response_format={
            "type": "json_object"
        },
        temperature=0
    )
    raw_output = response.choices[0].message.content
    data = json.loads(raw_output)
    return JobD(**data)
def generate_ai_conclusion(
    job_description: str,
    resume_text: str,
    score: int,
    matching_skills: list,
    missing_skills: list,
    experience_years,
    education: list,
    projects: list
):
    prompt = f"""
You are an expert AI Resume Screening Assistant.
Analyze the candidate's resume against the given job description.
JOB DESCRIPTION:
{job_description}
CANDIDATE RESUME:
{resume_text}
MATCH SCORE:
{score}%
MATCHING SKILLS:
{matching_skills}
MISSING IMPORTANT SKILLS:
{missing_skills}
EXPERIENCE:
{experience_years} years
EDUCATION:
{education}
PROJECTS:
{projects}
Generate a specific and professional AI conclusion.
The conclusion must:
\- Explain how well the candidate matches the job.
\- Mention the most important matching skills.
\- Mention important missing skills or gaps.
\- Consider the candidate's experience.
\- Consider relevant education.
\- Consider relevant projects.
\- Mention important strengths.
\- Mention important weaknesses or gaps.
\- Give an overall assessment of the candidate's alignment with the role.
IMPORTANT RULES:
1. Base the conclusion ONLY on the provided resume and job description.
2. Do NOT invent skills, experience, education, projects or achievements.
3. Do NOT simply repeat the job description.
4. Do NOT mention that you are an AI.
5. Do NOT give another score.
6. The score is already calculated as {score}%.
7. Write a natural, professional conclusion.
8. Make the conclusion specific to this candidate.
9. Keep it around 100-180 words.
10. Return ONLY the conclusion text.
"""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are an expert HR resume screening assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )
    return response.choices[0].message.content.strip()
# ============================================================
# RESUME TEXT PARSER
# ============================================================
def parse_resume(resume_text: str) -> Resume:
    resume_schema = Resume.model_json_schema()
    system_prompt = f"""
You are an expert resume parser.
Extract information from the resume based on its meaning,
not only based on exact section headings.
Different resumes may use different headings.
For example:
\- Experience
\- Professional Experience
\- Work History
\- Employment
\- Internships
These may all contain relevant experience.
Skills may appear in:
\- Skills section
\- Work experience
\- Internships
\- Projects
Return ONLY valid JSON matching this schema:
{resume_schema}
Important rules:
1. Do not invent information.
2. If a value is not available, return null.
3. If a list has no information, return an empty list.
4. Include internships inside experiences.
5. Extract skills mentioned across the entire resume.
"""
    user_prompt = f"""
Parse the following resume:
{resume_text}
"""
    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": user_prompt
        }
    ]
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        response_format={
            "type": "json_object"
        },
        temperature=0
    )
    raw_output = response.choices[0].message.content
    data = json.loads(raw_output)
    return Resume(**data)
# ============================================================
# PDF READER
# ============================================================
def read_pdf(file_bytes: bytes) -> str:
    pdf_file = BytesIO(file_bytes)
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text
# ============================================================
# DOCX READER
# ============================================================
def read_docx(file_bytes: bytes) -> str:
    docx_file = BytesIO(file_bytes)
    document = Document(docx_file)
    text = ""
    # Normal paragraphs
    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            text += paragraph.text + "\n"
    # Tables
    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                if cell.text.strip():
                    text += cell.text + "\n"
    return text
# ============================================================
# FILE READER
# ============================================================
def read_resume(file_bytes: bytes, filename: str) -> str:
    extension = filename.lower().split(".")[-1]
    if extension == "pdf":
        return read_pdf(file_bytes)
    elif extension == "docx":
        return read_docx(file_bytes)
    else:
        raise ValueError(
            f"Unsupported file type: {filename}. "
            "Only PDF and DOCX are supported."
        )
# ============================================================
# RESUME + JOB MATCHING
# ============================================================
def final_score(job: JobD, resume: Resume) -> MatchResult:
    """Calculate a repeatable score from parsed JobD and Resume data."""

    import re

    def normalize(value: str) -> str:
        value = value.lower().strip()
        value = value.replace("javascript", "javascript")
        value = value.replace("github", "github")
        return re.sub(r"[^a-z0-9]+", "", value)

    def skill_matches(required_skill: str, candidate_skills: set[str]) -> bool:
        target = normalize(required_skill)
        aliases = {
            "react": {"react", "reactjs"},
            "reactjs": {"react", "reactjs"},
            "node": {"node", "nodejs"},
            "nodejs": {"node", "nodejs"},
            "express": {"express", "expressjs"},
            "expressjs": {"express", "expressjs"},
            "javascript": {"javascript", "js"},
            "gitgithub": {"gitgithub", "git", "github"},
            "restapi": {"restapi", "restapis", "restfulapi", "restfulapis"},
            "restapis": {"restapi", "restapis", "restfulapi", "restfulapis"},
            "mongodb": {"mongodb", "mongo"},
            "ds": {"ds", "dsa", "datastructuresalgorithms"},
            "dsa": {"ds", "dsa", "datastructuresalgorithms"},
        }
        target_aliases = aliases.get(target, {target})
        for candidate in candidate_skills:
            candidate_aliases = aliases.get(candidate, {candidate})
            if target_aliases & candidate_aliases:
                return True
            # Allow common exact token forms, but avoid broad substring matches.
            if target and target == candidate:
                return True
        return False

    candidate_skills = {
        normalize(skill) for skill in resume.skills if skill and skill.strip()
    }

    required_skills = list(dict.fromkeys(
        skill.strip() for skill in job.required_skills if skill and skill.strip()
    ))
    preferred_skills = list(dict.fromkeys(
        skill.strip() for skill in job.preferred_skills if skill and skill.strip()
    ))

    matching_required = [
        skill for skill in required_skills
        if skill_matches(skill, candidate_skills)
    ]
    missing_required = [
        skill for skill in required_skills
        if not skill_matches(skill, candidate_skills)
    ]
    matching_preferred = [
        skill for skill in preferred_skills
        if skill_matches(skill, candidate_skills)
    ]
    missing_preferred = [
        skill for skill in preferred_skills
        if not skill_matches(skill, candidate_skills)
    ]

    # Fixed weights: required skills 70, preferred skills 10,
    # experience 15, education 5. Total possible score = 100.
    required_score = (
        70 * len(matching_required) / len(required_skills)
        if required_skills else 70.0
    )
    preferred_score = (
        10 * len(matching_preferred) / len(preferred_skills)
        if preferred_skills else 10.0
    )

    minimum_exp = job.minimum_experience
    actual_exp = resume.total_experience_years
    if minimum_exp is None or minimum_exp <= 0:
        experience_score = 15.0
        experience_met = None
    elif actual_exp is None:
        experience_score = 0.0
        experience_met = False
    else:
        experience_score = min(max(actual_exp, 0.0) / minimum_exp, 1.0) * 15
        experience_met = actual_exp >= minimum_exp

    # Conservative, deterministic education comparison.
    education_text = normalize(" ".join(resume.education or []))
    education_requirements = job.education_requirements or []
    if not education_requirements:
        education_score = 5.0
        education_matched = []
        education_missing = []
    else:
        education_matched = []
        education_missing = []
        for requirement in education_requirements:
            req_norm = normalize(requirement)
            # Match the complete normalized requirement, or its meaningful
            # terms when the JD contains a longer qualification sentence.
            req_terms = [
                normalize(word) for word in requirement.split()
                if len(normalize(word)) > 3
            ]
            matched = bool(req_norm and req_norm in education_text)
            if not matched and req_terms:
                matched = any(term in education_text for term in req_terms)
            (education_matched if matched else education_missing).append(requirement)
        education_score = 5 * len(education_matched) / len(education_requirements)

    total_score = max(0, min(100, round(
        required_score + preferred_score + experience_score + education_score
    )))

    details = {
        "matching_skills": matching_required + matching_preferred,
        "missing_important_skills": missing_required,
        "missing_preferred_skills": missing_preferred,
        "experience_requirement_met": experience_met,
        "score_breakdown": {
            "required_skills": round(required_score, 2),
            "preferred_skills": round(preferred_score, 2),
            "experience": round(experience_score, 2),
            "education": round(education_score, 2),
        },
        "education_matched": education_matched,
        "education_missing": education_missing,
        "final_verdict": (
            "Strong Match" if total_score >= 80
            else "Moderate Match" if total_score >= 60
            else "Low Match"
        ),
    }
    return MatchResult(score=total_score, details=details)

# ============================================================
# PROCESS ONE UPLOADED RESUME
# ============================================================
def process_resume(
    file_bytes: bytes,
    filename: str,
    job: JobD
):
    # Read PDF/DOCX
    resume_text = read_resume(
        file_bytes,
        filename
    )
    if not resume_text.strip():
        raise ValueError(
            f"Could not extract text from {filename}"
        )
    # AI Resume Parsing
    parsed_resume = parse_resume(
        resume_text
    )
    # AI Job Matching
    result = final_score(
        job,
        parsed_resume
    )
    # Extract matching information
    matching_skills = result.details.get(
        "matching_skills",
        []
    )
    missing_skills = result.details.get(
        "missing_important_skills",
        []
    )
    experience_years = (
        parsed_resume.total_experience_years
    )
    # ==========================================
    # AI GENERATED CONCLUSION
    # ==========================================
    ai_conclusion = generate_ai_conclusion(
        job_description=job.model_dump_json(),
        resume_text=resume_text,
        score=int(result.score),
        matching_skills=matching_skills,
        missing_skills=missing_skills,
        experience_years=experience_years,
        education=parsed_resume.education,
        projects=parsed_resume.projects
    )
    # Put AI conclusion inside details
    result.details["final_verdict"] = ai_conclusion
    # ==========================================
    # FINAL RESPONSE
    # ==========================================
    return {
        "name": parsed_resume.name,
        "email": parsed_resume.email,
        "phone": parsed_resume.phone,
        "score": result.score,
        "details": result.details,
        "skills": parsed_resume.skills,
        "experience_years": (
            parsed_resume.total_experience_years
        ),
        "education": parsed_resume.education,
        "projects": parsed_resume.projects,
        "certifications": parsed_resume.certifications
    }
# ============================================================
# ANALYZE MULTIPLE RESUMES
# ============================================================
def analyze_resumes(
    job_description: str,
    uploaded_files: list[tuple[str, bytes]]
):
    if not job_description.strip():
        raise ValueError(
            "Job description cannot be empty."
        )
    if not uploaded_files:
        raise ValueError(
            "At least one resume is required."
        )
    # Parse Job Description using AI
    job = parse_job_description(
        job_description
    )
    all_results = []
    # Process every uploaded resume
    for filename, file_bytes in uploaded_files:
        try:
            result = process_resume(
                file_bytes,
                filename,
                job
            )
            all_results.append(result)
        except Exception as e:
            # Don't stop all candidates
            # if one resume has an error
            all_results.append({
                "name": filename,
                "score": 0,
                "error": str(e)
            })
    # Highest score first
    all_results.sort(
        key=lambda candidate: candidate.get(
            "score",
            0
        ),
        reverse=True
    )
    return {
        "job": job.model_dump(),
        "total_candidates": len(all_results),
        "candidates": all_results
    }
