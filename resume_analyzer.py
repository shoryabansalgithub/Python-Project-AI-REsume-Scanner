# Comprehensive skills database
skills_db = [
    # Programming Languages
    "python", "java", "c++", "c#", "javascript", "typescript", "go", "rust", "kotlin", "swift",
    # Data & ML
    "machine learning", "data analysis", "deep learning", "nlp", "computer vision", "tensorflow", "pytorch",
    # Databases
    "sql", "nosql", "mongodb", "postgresql", "mysql", "redis", "elasticsearch",
    # Web Technologies
    "html", "css", "react", "vue", "angular", "node", "express", "django", "flask",
    # Cloud & DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "ci/cd", "jenkins",
    # Soft Skills
    "communication", "leadership", "problem solving", "teamwork", "project management",
    "agile", "scrum", "git", "api", "rest", "microservices"
]

def analyze_resume(text):
    """
    Analyze resume text and extract skills
    Returns tuple of (score, found_skills)
    """
    text = text.lower()
    found_skills = []

    for skill in skills_db:
        if skill in text:
            found_skills.append(skill)
    
    # Calculate score based on found skills (max 100)
    base_score = min(len(found_skills) * 8, 80)
    
    # Bonus points for specific combinations
    if any(lang in found_skills for lang in ["python", "java", "c++"]):
        base_score = min(base_score + 5, 100)
    
    if any(ml in found_skills for ml in ["machine learning", "deep learning", "tensorflow"]):
        base_score = min(base_score + 5, 100)
    
    if any(soft in found_skills for soft in ["communication", "leadership", "teamwork"]):
        base_score = min(base_score + 5, 100)
    
    score = min(base_score, 100)

    return score, found_skills


def get_required_skills(job_title="software engineer"):
    """
    Get required skills based on job title
    """
    job_skills = {
        "software engineer": ["python", "java", "c++", "sql", "git", "api", "problem solving"],
        "data scientist": ["python", "machine learning", "sql", "data analysis", "tensorflow"],
        "web developer": ["javascript", "react", "html", "css", "node", "api"],
        "devops engineer": ["docker", "kubernetes", "aws", "ci/cd", "git"],
    }
    
    return job_skills.get(job_title.lower(), skills_db[:10])