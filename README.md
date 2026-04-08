# ⚡ ResumeIQ — AI Resume Analyzer & Job Matcher

> Python · Streamlit ·  NLP · LLM

---

## 📁 Project Structure

```
resumeiq/
├── app.py               ← Streamlit entry point  (UI shell only)
├── core.py              ← All AI/ML backend logic (no Streamlit)
├── ui_components.py     ← All reusable UI renderers (imports only streamlit)
└── requirements.txt     ← 4 dependencies
```

### Dependency flow (one-way)

```
app.py
  ├── imports core.py           (AI pipeline functions)
  └── imports ui_components.py  (render helpers)
```

`core.py` and `ui_components.py` never import each other —
keeping concerns cleanly separated.

---

## 🗂 File Responsibilities

### `core.py` — Backend Engine
| Function | Purpose |
|---|---|
| `call_claude()` | Generic Claude API wrapper |
| `extract_text_from_pdf()` | PDF bytes → plain text via pypdf |
| `extract_text_from_docx()` | DOCX bytes → plain text via python-docx |
| `extract_resume_text()` | Dispatcher: routes file by extension |
| `parse_resume()` | NLP parsing → structured JSON profile |
| `extract_skills_analysis()` | Skill gap + 5-dimension scoring |
| `get_llm_suggestions()` | 8 coaching tips from Claude |
| `get_job_matches()` | 6 best-fit role recommendations |
| `run_full_analysis()` | Orchestrator: runs all 4 pipelines |
| `DEMO_RESUME` | Built-in sample resume text |
| `DEMO_JD` | Built-in sample job description |

### `ui_components.py` — UI Layer
| Function | Purpose |
|---|---|
| `inject_css()` | Dark theme stylesheet injection |
| `render_donut()` | Inline SVG score ring |
| `render_progress()` | Labelled gradient progress bar |
| `render_skills()` | Colour-coded skill pill cloud |
| `render_metric_card()` | Single KPI card |
| `render_hero()` | Animated landing banner |
| `render_profile_card()` | Candidate identity block |
| `render_edu_card()` | Education + certifications |
| `render_experience()` | Work experience card list |
| `render_tab_dashboard()` | Full Tab 1 content |
| `render_tab_skills()` | Full Tab 2 content |
| `render_tab_suggestions()` | Full Tab 3 content |
| `render_tab_jobs()` | Full Tab 4 content |
| `render_sidebar_brand()` | Sidebar logo/brand block |
| `render_sidebar_how_it_works()` | Sidebar explainer box |
| `render_empty_state()` | Pre-analysis placeholder |

### `app.py` — Entry Point
Pure orchestration — no logic, no HTML strings.
1. `set_page_config()` + `inject_css()`
2. Sidebar: file upload, JD input, analyze button
3. Hero banner
4. Demo toggle
5. Run pipeline (calls `core.py` functions with spinners)
6. Render results across 4 tabs (calls `ui_components.py` renderers)

---

## 🚀 Setup & Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set API key
export ANTHROPIC_API_KEY="sk-ant-..."   # Linux/macOS
# $env:ANTHROPIC_API_KEY="sk-ant-..."  # Windows PowerShell

# 3. Run
streamlit run app.py
# Opens at http://localhost:8501
```

---

## ✨ Features

- **NLP Resume Parsing** — structured extraction from PDF / DOCX / TXT
- **Skill Gap Analysis** — matched ✅ / missing ❌ / bonus ⭐ skills vs JD
- **5-Dimension Scoring** — skills, experience, keywords, format, education
- **ATS Compatibility Score** — keyword density & format check
- **8 AI Suggestions** — Claude coaching tailored to the specific JD
- **6 Job Matches** — ranked roles with salary ranges & match %
- **Demo Mode** — instant showcase without uploading any file
