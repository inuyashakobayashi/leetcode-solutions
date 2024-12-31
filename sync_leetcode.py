import os
import requests
import json
from datetime import datetime

def fetch_leetcode_submissions(username):
    print(f"Fetching submissions for {username}")
    
    # LeetCode API endpoint für Recent Submissions
    url = f"https://leetcode.com/api/submissions/{username}/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            return response.json().get('submissions_dump', [])
        return []
    except Exception as e:
        print(f"Error fetching submissions: {e}")
        return []

def save_submission(submission, base_dir):
    # Erstelle Ordner für die Programmiersprache
    lang_dir = os.path.join(base_dir, submission['lang'].lower())
    os.makedirs(lang_dir, exist_ok=True)
    
    # Bereite Dateinamen vor
    problem_title = submission['title'].replace(' ', '_').lower()
    file_extension = {
        'python': '.py',
        'python3': '.py',
        'java': '.java',
        'cpp': '.cpp',
        'javascript': '.js',
        'typescript': '.ts'
    }.get(submission['lang'].lower(), '.txt')
    
    filename = f"{problem_title}{file_extension}"
    filepath = os.path.join(lang_dir, filename)
    
    # Bereite Inhalt vor
    content = f"""# {submission['title']}
# Difficulty: {submission.get('difficulty', 'Unknown')}
# Status: {submission.get('status_display', 'Unknown')}
# Submission Date: {datetime.fromtimestamp(submission['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}

{submission['code']}
"""
    
    # Speichere die Lösung
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return filepath

def main():
    username = os.environ.get('LEETCODE_USERNAME')
    if not username:
        print("Error: LEETCODE_USERNAME not set")
        return
    
    print("Starting LeetCode sync...")
    
    # Erstelle Basis-Verzeichnis für Lösungen
    base_dir = 'leetcode_solutions'
    os.makedirs(base_dir, exist_ok=True)
    
    # Hole Submissions
    submissions = fetch_leetcode_submissions(username)
    
    if not submissions:
        print("No submissions found")
        return
    
    print(f"Found {len(submissions)} submissions")
    
    # Speichere nur erfolgreiche Submissions
    saved_count = 0
    for submission in submissions:
        if submission.get('status_display') == 'Accepted':
            filepath = save_submission(submission, base_dir)
            print(f"Saved: {filepath}")
            saved_count += 1
    
    print(f"Successfully saved {saved_count} submissions")

if __name__ == "__main__":
    main()