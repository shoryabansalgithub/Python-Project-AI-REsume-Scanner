# AI-Powered Resume Scanner and Career Assistant

## Overview

This project is an AI-powered resume scanner and career assistant built using Streamlit. It helps users optimize their resumes, identify skill gaps, explore career roadmaps, get job recommendations, and prepare for interviews. The application provides a comprehensive suite of tools for career development, from resume creation to interview preparation.

## Features

### 1. Resume Parsing

- Extracts key information from PDF resumes, including name, email, phone, skills, education, and years of experience.
- Utilizes `PyMuPDF` for efficient text extraction and regular expressions for structured data parsing.

### 2. Resume Analysis & Skill Gap Identification

- Analyzes extracted skills against a predefined database of required skills for various job roles.
- Identifies skills the user possesses and highlights missing skills for a target role.
- Provides a match percentage indicating how well the user's skills align with the target role.

### 3. Career Roadmap Generation

- Generates a personalized career roadmap based on a target job role.
- Outlines typical career progression, including milestones, estimated years of experience, and key skills required at each stage.

### 4. ATS (Applicant Tracking System) Scoring

- Calculates an ATS compatibility score for resumes based on several factors:
    - **Keyword Matching**: Scores against required skills for a target role.
    - **Section Presence**: Checks for essential resume sections (e.g., Summary, Experience, Education, Skills).
    - **Resume Length**: Optimal length for ATS readability.
    - **Action Verbs**: Presence of strong action verbs.
    - **Formatting**: Detects and penalizes problematic formatting (tables, images, multiple columns).
- Provides a detailed breakdown of the score, suggested fixes, and identified issues.

### 5. Job Recommendation

- Recommends relevant job roles based on the user's extracted skills.
- Identifies missing skills for recommended jobs to guide further learning.

### 6. Learning Path Suggestion

- Generates a customized learning path to acquire missing skills.
- Suggests resources (e.g., Coursera, YouTube) and estimates learning hours.

### 7. STAR Interview Question Generator

- Provides STAR (Situation, Task, Action, Result) interview questions tailored to specific roles and skills.
- Helps users practice and prepare structured answers for common interview scenarios.

### 8. Resume PDF Generation

- Allows users to generate a clean, ATS-friendly PDF resume based on their profile information.
- Utilizes `fpdf2` to create professional-looking resumes.

## Technologies Used

- **Streamlit**: For building the interactive web application.
- **PyMuPDF (fitz)**: For efficient PDF text extraction.
- **Matplotlib**: For generating various charts and visualizations (skill gap, career roadmap, ATS score).
- **NumPy**: For numerical operations.
- **fpdf2**: For generating PDF resumes.
- **SQLite**: For user authentication, profile management, and storing resume data.

## Installation

To set up the project locally, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/shoryabansalgithub/Python-Project-AI-REsume-Scanner.git
    cd Python-Project-AI-REsume-Scanner
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Run the Streamlit application:**
    ```bash
    streamlit run app.py
    ```

2.  **Access the application:**
    Open your web browser and navigate to the URL provided by Streamlit (usually `http://localhost:8501`).

3.  **Register or Log In:**
    Create a new account or log in to access the features.

4.  **Upload Resume:**
    Upload your resume in PDF format to get started with parsing and analysis.

5.  **Explore Features:**
    Navigate through the sidebar to utilize different functionalities like Skill Gap Analysis, Career Roadmap, ATS Scorer, Job Recommender, Learning Path, and STAR Interview Prep.

## Project Structure

```
Python-Project-AI-REsume-Scanner/
├── app.py                      # Main Streamlit application file
├── auth.py                     # User authentication and profile management
├── charts.py                   # Matplotlib charts and visualizations
├── database.py                 # SQLite database schema and operations
├── job_recommender.py          # Logic for job recommendations
├── learning_path.py            # Generates learning paths for missing skills
├── resume_analyzer.py          # Core resume analysis, skill gap, and career roadmap logic
├── resume_maker.py             # Generates PDF resumes using fpdf2
├── resume_parser.py            # Extracts text and parses structured data from PDFs
├── resume_scorer.py            # Calculates ATS compatibility score
├── star_generator.py           # Generates STAR interview questions
├── requirements.txt            # Python dependencies
├── users.db                    # SQLite database file (generated on first run)
└── data/                       # Data-related modules
    ├── __init__.py
    ├── learning_db.py          # Database of learning resources
    ├── skills_db.py            # Database of required skills for various roles
    └── star_bank.py            # Database of STAR interview questions
```

## Data Models

### `skills_db.py`

This module defines a central database of skills required for various job roles. It maps job titles (e.g., "software engineer", "data scientist") to a list of essential skills. This database is crucial for features like skill gap analysis and ATS scoring.

### `database.py`

Handles the SQLite database operations. It sets up the `users.db` file and defines tables for:

-   `users`: Stores user registration details (name, email, password, job title, education).
-   `resumes`: Stores metadata about uploaded resumes (user email, file path, score, upload timestamp).
-   `user_skills`: Links user emails to specific skills found in their resumes.
-   `career_path`: Stores user's career progression details (current level, target level, timeline).

## Contributing

Contributions are welcome! Please feel free to fork the repository, create a new branch, and submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License - see the LICENSE file for details. (Note: A LICENSE file is not currently present in the repository, but it is good practice to include one.)

---

*Generated by Manus AI*
