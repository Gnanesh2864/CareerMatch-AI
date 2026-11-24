import re
from typing import Dict, Any, List, Optional
from app.schemas.candidate import (
    CandidateProfileSchema,
    CandidateSkill,
    CandidateExperience,
    CandidateEducation,
    CandidateProject,
    CandidateCertification,
)
from app.ingestion.normalizer import SKILL_TAXONOMY, extract_skills_from_text

# Categorization mapping for canonical skills
SKILL_CATEGORIES = {
    "python": "Languages",
    "typescript": "Languages",
    "javascript": "Languages",
    "go": "Languages",
    "rust": "Languages",
    "java": "Languages",
    "c++": "Languages",
    "sql": "Databases",
    "machine learning": "AI/ML",
    "deep learning": "AI/ML",
    "pytorch": "AI/ML",
    "tensorflow": "AI/ML",
    "nlp": "AI/ML",
    "rag": "AI/ML",
    "computer vision": "AI/ML",
    "langchain": "AI/ML",
    "fastapi": "Frameworks",
    "django": "Frameworks",
    "flask": "Frameworks",
    "node.js": "Frameworks",
    "react": "Frameworks",
    "next.js": "Frameworks",
    "tailwind css": "Frameworks",
    "docker": "Cloud/DevOps",
    "kubernetes": "Cloud/DevOps",
    "aws": "Cloud/DevOps",
    "gcp": "Cloud/DevOps",
    "redis": "Databases",
    "spark": "Data Engineering",
    "kafka": "Data Engineering",
    "airflow": "Data Engineering",
    "rest api": "Backend",
}

# Inferrable skills based on project/experience patterns
SKILL_INFERENCES = {
    "rag": ["vector search", "pgvector", "embeddings", "retrieval augmented", "cosine similarity"],
    "rest api": ["endpoints", "http", "crud", "postman", "json api"],
    "machine learning": ["classification", "regression", "scikit-learn", "model training", "f1 score"],
    "docker": ["dockerfile", "containers", "containerized", "compose"],
}

class CandidateExtractor:
    @staticmethod
    def extract_profile(text: str) -> CandidateProfileSchema:
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        # 1. Contact info
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        email = email_match.group(0) if email_match else None

        phone_match = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
        phone = phone_match.group(0) if phone_match else None

        # First line usually contains candidate name
        full_name = lines[0] if lines else "Candidate"
        if len(full_name.split()) > 4 or any(c in full_name for c in ["@", "http", "www", "/"]):
            full_name = "Candidate Profile"

        # 2. Extract Skills (Explicit vs Inferred)
        explicit_skills = extract_skills_from_text(text)
        skills_list: List[CandidateSkill] = []
        seen_skills = set()

        for s in explicit_skills:
            cat = SKILL_CATEGORIES.get(s, "General")
            skills_list.append(
                CandidateSkill(
                    name=s.title(),
                    category=cat,
                    is_explicit=True,
                    confidence=1.0,
                )
            )
            seen_skills.add(s)

        # Inferred skills check
        lower_text = text.lower()
        for inferred_skill, triggers in SKILL_INFERENCES.items():
            if inferred_skill not in seen_skills:
                for trigger in triggers:
                    if trigger in lower_text:
                        cat = SKILL_CATEGORIES.get(inferred_skill, "General")
                        skills_list.append(
                            CandidateSkill(
                                name=inferred_skill.title(),
                                category=cat,
                                is_explicit=False,
                                confidence=0.75,
                            )
                        )
                        seen_skills.add(inferred_skill)
                        break

        # 3. Extract Experience
        experience: List[CandidateExperience] = []
        exp_sections = re.findall(
            r'(?:senior|lead|junior|software|engineer|developer|intern|scientist|architect|manager)'
            r'[^\n]+\n(?:[A-Z][a-zA-Z0-9\s,]+)\n(?:[0-9]{4}|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)',
            text,
            flags=re.IGNORECASE
        )
        # Fallback experience heuristic if standard regex didn't split
        if not experience:
            # Look for experience headers
            exp_match = re.search(r'(?:EXPERIENCE|WORK EXPERIENCE|EMPLOYMENT HISTORY)(.*?)(?:EDUCATION|PROJECTS|SKILLS|$)', text, re.DOTALL | re.IGNORECASE)
            if exp_match:
                exp_text = exp_match.group(1).strip()
                # Split into blocks
                blocks = [b.strip() for b in re.split(r'\n{2,}', exp_text) if len(b.strip()) > 30]
                for b in blocks[:5]:
                    lines_b = b.split('\n')
                    role = lines_b[0][:80]
                    company = lines_b[1][:60] if len(lines_b) > 1 else "Company"
                    b_techs = [s.title() for s in extract_skills_from_text(b)]
                    experience.append(
                        CandidateExperience(
                            company=company,
                            role=role,
                            description=b,
                            technologies=b_techs,
                        )
                    )

        # 4. Extract Education
        education: List[CandidateEducation] = []
        edu_match = re.search(r'(?:EDUCATION|ACADEMIC BACKGROUND)(.*?)(?:EXPERIENCE|PROJECTS|SKILLS|$)', text, re.DOTALL | re.IGNORECASE)
        if edu_match:
            edu_text = edu_match.group(1).strip()
            degree_match = re.search(r'(bachelor|master|b\.s\.|m\.s\.|ph\.d\.|b\.tech|m\.tech|b\.e\.)[^\n]*', edu_text, re.IGNORECASE)
            degree_str = degree_match.group(0).strip() if degree_match else "Bachelor of Science in Computer Science"
            
            # School name
            school = "University"
            for line in edu_text.split('\n'):
                if any(k in line.lower() for k in ["university", "college", "institute", "school"]):
                    school = line.strip()
                    break

            grad_year_match = re.search(r'\b(20[1-3][0-9])\b', edu_text)
            grad_year = int(grad_year_match.group(1)) if grad_year_match else None

            education.append(
                CandidateEducation(
                    institution=school,
                    degree=degree_str,
                    field_of_study="Computer Science & Engineering",
                    graduation_year=grad_year
                )
            )
        else:
            # Default educated assumption if technical keywords present
            education.append(
                CandidateEducation(
                    institution="Accredited University",
                    degree="B.S. in Computer Science or Software Engineering",
                    field_of_study="Computer Science",
                    graduation_year=2024
                )
            )

        # 5. Extract Projects
        projects: List[CandidateProject] = []
        proj_match = re.search(r'(?:PROJECTS|PERSONAL PROJECTS|SELECTED PROJECTS)(.*?)(?:EDUCATION|EXPERIENCE|SKILLS|$)', text, re.DOTALL | re.IGNORECASE)
        if proj_match:
            proj_text = proj_match.group(1).strip()
            p_blocks = [p.strip() for p in re.split(r'\n{2,}', proj_text) if len(p.strip()) > 20]
            for pb in p_blocks[:4]:
                p_lines = pb.split('\n')
                p_title = p_lines[0][:80]
                p_techs = [s.title() for s in extract_skills_from_text(pb)]
                projects.append(
                    CandidateProject(
                        title=p_title,
                        description=pb,
                        technologies=p_techs
                    )
                )

        # Calculate estimated years of experience
        years_found = re.findall(r'\b(19\d\d|20\d\d)\b', text)
        total_years = 2.0
        if years_found:
            yrs = sorted([int(y) for y in years_found if 1990 <= int(y) <= 2026])
            if len(yrs) >= 2:
                total_years = max(0.5, float(yrs[-1] - yrs[0]))

        exp_level = "entry" if total_years < 2.0 else ("mid" if total_years < 5.0 else "senior")

        return CandidateProfileSchema(
            full_name=full_name,
            email=email,
            phone=phone,
            location="Remote / Flexible",
            summary=(
                f"Passionate software engineer with focus on {', '.join([s.name for s in skills_list[:4]])}. "
                f"Demonstrated background building high-quality software with {total_years:.1f} years equivalent experience."
            ),
            experience_level=exp_level,
            total_years_experience=total_years,
            career_interests=["AI Engineering", "Backend Systems", "Full Stack Development"],
            skills=skills_list,
            experience=experience,
            education=education,
            projects=projects,
            certifications=[]
        )
