"""
core.py — ResumeIQ Backend Engine
==================================
All AI/ML logic lives here:
  - Claude API wrapper
  - PDF / DOCX / TXT text extraction
  - NLP resume parsing  (→ structured JSON)
  - Skill gap analysis  (→ match scores)
  - LLM suggestion generation
  - Job role matching

Nothing in this file imports streamlit.
Import this module into app.py (or any other UI / API layer).
"""

import json
import re
import io
from typing import Any


# ──────────────────────────────────────────────────────────────────────────────
# DEMO DATA  (used when no file is uploaded)
# ──────────────────────────────────────────────────────────────────────────────

DEMO_RESUME = """John Doe | AI/ML Engineer | john.doe@email.com | +91-9876543210 | Bengaluru, India

SUMMARY
Experienced AI/ML Engineer with 4+ years building production ML systems. Passionate about NLP,
computer vision, and deploying scalable ML APIs. Open-source contributor with 2 publications.

SKILLS
Python, TensorFlow, PyTorch, Scikit-learn, Hugging Face Transformers, LangChain, FastAPI,
Docker, Kubernetes, AWS SageMaker, GCP Vertex AI, SQL, PySpark, MLflow, Git, REST APIs,
Streamlit, OpenCV

EXPERIENCE
Senior ML Engineer | TechCorp AI | 2022–Present (2 yrs)
- Built NLP pipeline for document classification (94% accuracy, 10M docs/day)
- Fine-tuned LLaMA 2 on proprietary data; 35% improvement in summarization
- Led MLOps migration to Kubernetes; reduced deployment time by 60%

ML Engineer | StartupAI | 2020–2022 (2 yrs)
- Developed recommendation engine (CTR +22%)
- Deployed CV model for defect detection on edge devices

EDUCATION
B.Tech Computer Science | IIT Bombay | 2020

CERTIFICATIONS
AWS Certified ML Specialty | Google Professional ML Engineer | Deep Learning Specialization (Coursera)
"""

DEMO_JD = """Job Title: Senior Machine Learning Engineer

About the Role:
We are looking for a Senior ML Engineer to join our AI team.
You will build and deploy production ML systems at scale.

Requirements:
- 3+ years ML engineering experience
- Strong Python, PyTorch / TensorFlow
- Experience with LLMs, fine-tuning, prompt engineering
- NLP / Computer Vision experience
- MLOps: Docker, Kubernetes, CI/CD
- Cloud: AWS or GCP
- FastAPI or similar for model serving
- Experience with RAG, LangChain, vector databases

Nice to have:
- Spark / distributed computing
- Publications or open-source contributions
- Experience with RLHF, LoRA fine-tuning

Salary: ₹25–45 LPA | Location: Bengaluru / Remote
"""


# ──────────────────────────────────────────────────────────────────────────────
# 1. CLAUDE API WRAPPER
# ──────────────────────────────────────────────────────────────────────────────

def call_claude(system: str, user: str, max_tokens: int = 1500) -> str:
    """
    Minimal wrapper around the Anthropic Messages API.

    Args:
        system:     System prompt (sets the model's persona / task).
        user:       User-turn message (the actual content / data).
        max_tokens: Upper bound on the response length.

    Returns:
        Raw text string from the first content block.
    """
    import anthropic

    client = anthropic.Anthropic()          # reads ANTHROPIC_API_KEY from env
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return response.content[0].text


# ──────────────────────────────────────────────────────────────────────────────
# 2. FILE TEXT EXTRACTION
# ──────────────────────────────────────────────────────────────────────────────

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract plain text from a PDF file (given as raw bytes).
    Uses pypdf — no system dependencies required.
    Returns empty string on failure.
    """
    try:
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages).strip()
    except Exception as exc:
        print(f"[PDF extraction error] {exc}")
        return ""


def extract_text_from_docx(file_bytes: bytes) -> str:
    """
    Extract plain text from a .docx file (given as raw bytes).
    Uses python-docx.
    Returns empty string on failure.
    """
    try:
        import docx
        doc = docx.Document(io.BytesIO(file_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs).strip()
    except Exception as exc:
        print(f"[DOCX extraction error] {exc}")
        return ""


def extract_resume_text(uploaded_file) -> str:
    """
    Dispatch file extraction based on file extension.

    Args:
        uploaded_file: A Streamlit UploadedFile object
                       (has .name and .read() method).

    Returns:
        Plain text string of the resume content.
    """
    raw_bytes = uploaded_file.read()
    name = uploaded_file.name.lower()

    if name.endswith(".pdf"):
        return extract_text_from_pdf(raw_bytes)
    elif name.endswith(".docx"):
        return extract_text_from_docx(raw_bytes)
    else:
        # plain .txt or any other text file
        return raw_bytes.decode("utf-8", errors="ignore").strip()


# ──────────────────────────────────────────────────────────────────────────────
# 3. NLP RESUME PARSING
# ──────────────────────────────────────────────────────────────────────────────

def parse_resume(resume_text: str) -> dict[str, Any]:
    """
    Send resume text to Claude and extract structured profile data.

    Prompt uses a strict JSON schema so the output is always machine-readable.
    Markdown code fences (```json … ```) are stripped before parsing.

    Returns a dict with keys:
        name, email, phone, location, summary,
        total_experience_years, skills, tools_technologies,
        education, experience, certifications, languages
    """
    prompt = f"""You are a precise resume parser.
Extract all information from the resume text below.
Return ONLY valid JSON — no markdown, no explanation, no code fences.

Required schema:
{{
  "name": "string",
  "email": "string",
  "phone": "string",
  "location": "string",
  "summary": "2-3 sentence professional summary",
  "total_experience_years": <number>,
  "skills": ["skill1", "skill2", ...],
  "tools_technologies": ["tool1", "tool2", ...],
  "education": [
    {{"degree": "string", "institution": "string", "year": "string"}}
  ],
  "experience": [
    {{
      "title": "string",
      "company": "string",
      "duration": "string",
      "highlights": ["achievement1", "achievement2"]
    }}
  ],
  "certifications": ["cert1", "cert2"],
  "languages": ["lang1"]
}}

Resume text:
{resume_text[:6000]}
"""
    raw = call_claude(
        system="You are a precise resume parser. Return only valid JSON with no extra text.",
        user=prompt,
        max_tokens=2000,
    )
    cleaned = re.sub(r"```json\s*|```", "", raw).strip()
    return json.loads(cleaned)


# ──────────────────────────────────────────────────────────────────────────────
# 4. SKILL GAP ANALYSIS & SCORING
# ──────────────────────────────────────────────────────────────────────────────

def extract_skills_analysis(resume_text: str, jd_text: str) -> dict[str, Any]:
    """
    Compare resume against a job description using Claude.

    Returns a dict with:
        matched_skills        — skills present in both resume and JD
        missing_skills        — skills required by JD but absent from resume
        bonus_skills          — extra skills in resume not mentioned in JD
        skill_match_score     — 0-100
        experience_match_score— 0-100
        education_match_score — 0-100
        overall_score         — 0-100 weighted composite
        ats_score             — 0-100 ATS compatibility estimate
        keyword_density       — 0-100
        score_breakdown       — {skills, experience, keywords, format, education}
    """
    prompt = f"""You are an expert technical recruiter and ATS specialist.
Compare the resume and job description below.
Return ONLY valid JSON — no markdown, no explanation, no code fences.

Required schema:
{{
  "matched_skills": ["skill1", "skill2"],
  "missing_skills": ["skill1", "skill2"],
  "bonus_skills": ["skill1", "skill2"],
  "skill_match_score": <0-100>,
  "experience_match_score": <0-100>,
  "education_match_score": <0-100>,
  "overall_score": <0-100>,
  "ats_score": <0-100>,
  "keyword_density": <0-100>,
  "score_breakdown": {{
    "skills": <0-100>,
    "experience": <0-100>,
    "keywords": <0-100>,
    "format": <0-100>,
    "education": <0-100>
  }}
}}

Resume:
{resume_text[:3000]}

Job Description:
{jd_text[:2000]}
"""
    raw = call_claude(
        system="You are a precise resume-JD matcher. Return only valid JSON.",
        user=prompt,
        max_tokens=1200,
    )
    cleaned = re.sub(r"```json\s*|```", "", raw).strip()
    return json.loads(cleaned)


# ──────────────────────────────────────────────────────────────────────────────
# 5. LLM SUGGESTION ENGINE
# ──────────────────────────────────────────────────────────────────────────────

def get_llm_suggestions(
    resume_text: str,
    jd_text: str,
    analysis: dict[str, Any],
) -> list[str]:
    """
    Ask Claude to generate 8 specific, actionable career coaching suggestions
    tailored to the gap between this resume and this job description.

    Returns a list of 8 plain-text strings.
    """
    missing = ", ".join(analysis.get("missing_skills", [])[:8])
    overall = analysis.get("overall_score", 0)

    prompt = f"""You are an expert AIML career coach and hiring manager.
The candidate's resume scored {overall}/100 against the job description.
Key missing skills: {missing}.

Provide exactly 8 specific, actionable suggestions to improve this resume
for this specific job. Each suggestion should be 1-3 sentences and concrete.

Return ONLY a JSON array of 8 strings — no markdown, no explanation, no code fences.
Example format: ["Suggestion one...", "Suggestion two...", ...]

Resume:
{resume_text[:2000]}

Job Description:
{jd_text[:1500]}
"""
    raw = call_claude(
        system="You are a career coach. Return a JSON array of exactly 8 suggestion strings.",
        user=prompt,
        max_tokens=1200,
    )
    cleaned = re.sub(r"```json\s*|```", "", raw).strip()
    return json.loads(cleaned)


# ──────────────────────────────────────────────────────────────────────────────
# 6. JOB ROLE MATCHING
# ──────────────────────────────────────────────────────────────────────────────

def get_job_matches(
    resume_text: str,
    skills: list[str],
) -> list[dict[str, Any]]:
    """
    Recommend 6 best-fit job roles for the candidate based on their profile.

    Returns a list of dicts, each with:
        title, company_type, location, match_score, salary_range, why_fit
    """
    skill_str = ", ".join(skills[:15])

    prompt = f"""You are a job placement specialist focused on AI/ML roles.
Based on the candidate's skills ({skill_str}) and experience below,
recommend exactly 6 relevant AI/ML job roles they should target.

Return ONLY a JSON array — no markdown, no explanation, no code fences.

Required schema:
[
  {{
    "title": "Job Title",
    "company_type": "e.g. FAANG / AI Startup / Research Lab / Consulting",
    "location": "e.g. Remote / Bengaluru / USA",
    "match_score": <0-100>,
    "salary_range": "e.g. ₹18-30 LPA or $120k-160k",
    "why_fit": "One sentence explaining why this candidate fits this role."
  }}
]

Resume:
{resume_text[:1500]}
"""
    raw = call_claude(
        system="You are a job placement expert. Return only a valid JSON array.",
        user=prompt,
        max_tokens=1200,
    )
    cleaned = re.sub(r"```json\s*|```", "", raw).strip()
    return json.loads(cleaned)


# ──────────────────────────────────────────────────────────────────────────────
# 7. ORCHESTRATOR  (runs the full pipeline in one call)
# ──────────────────────────────────────────────────────────────────────────────

def run_full_analysis(resume_text: str, jd_text: str) -> dict[str, Any]:
    """
    Convenience function that runs all four Claude pipelines sequentially
    and returns a single results dict.

    Args:
        resume_text: Plain text of the candidate's resume.
        jd_text:     Plain text of the target job description.

    Returns:
        {
            "parsed":       dict  — structured resume profile,
            "analysis":     dict  — skill gap & match scores,
            "suggestions":  list  — 8 coaching strings,
            "job_matches":  list  — 6 role recommendation dicts,
        }
    """
    parsed      = parse_resume(resume_text)
    analysis    = extract_skills_analysis(resume_text, jd_text)
    suggestions = get_llm_suggestions(resume_text, jd_text, analysis)
    job_matches = get_job_matches(resume_text, parsed.get("skills", []))

    return {
        "parsed":      parsed,
        "analysis":    analysis,
        "suggestions": suggestions,
        "job_matches": job_matches,
    }
