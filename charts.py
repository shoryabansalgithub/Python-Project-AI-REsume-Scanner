import matplotlib.pyplot as plt
import numpy as np

def skill_chart(user_skills, required_skills):
    """
    Create a bar chart showing user skills vs required skills
    """
    values = []
    labels = []

    for skill in required_skills:
        labels.append(skill.title())
        values.append(1 if skill in user_skills else 0)

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ['#667eea' if v == 1 else '#e0e0e0' for v in values]
    ax.bar(labels, values, color=colors, edgecolor='black', linewidth=1.5)
    ax.set_ylabel('Skill Level', fontsize=12, fontweight='bold')
    ax.set_title('Your Skills Assessment', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 1.2)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    return fig


def skill_gap_chart(user_skills, required_skills):
    """
    Create a radar/bar chart showing skill gaps
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    labels = [s.title() for s in required_skills]
    user_vals = [1 if s in user_skills else 0 for s in required_skills]
    required_vals = [1 for _ in required_skills]
    
    x = np.arange(len(labels))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, user_vals, width, label='Your Skills', color='#667eea', alpha=0.8)
    bars2 = ax.bar(x + width/2, required_vals, width, label='Required Skills', color='#f5576c', alpha=0.8)
    
    ax.set_xlabel('Skills', fontsize=12, fontweight='bold')
    ax.set_ylabel('Proficiency', fontsize=12, fontweight='bold')
    ax.set_title('Skill Gap Analysis', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.legend()
    ax.set_ylim(0, 1.3)
    
    plt.tight_layout()
    return fig


def career_roadmap_chart(user_skills):
    """
    Create a career progression chart
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    levels = ['Junior\nEngineer', 'Mid-Level\nEngineer', 'Senior\nEngineer', 'Tech\nLead']
    experience = [0, 2, 5, 8]
    salary_range = [40, 80, 120, 160]  # in thousands
    
    colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c']
    
    ax.plot(levels, salary_range, marker='o', linewidth=3, markersize=12, color='#667eea', label='Expected Salary Range')
    ax.fill_between(range(len(levels)), salary_range, alpha=0.3, color='#667eea')
    
    ax.set_ylabel('Expected Salary (in thousands USD)', fontsize=12, fontweight='bold')
    ax.set_title('Your Career Progression Path', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    
    for i, (level, salary) in enumerate(zip(levels, salary_range)):
        ax.text(i, salary + 5, f'${salary}K', ha='center', fontweight='bold')
    
    plt.tight_layout()
    return fig