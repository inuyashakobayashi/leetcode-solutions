import os
import json
import requests
from datetime import datetime

def fetch_submission_details(titleSlug):
    """Holt Details einer spezifischen Submission"""
    url = "https://leetcode.com/graphql"
    
    query = """
    query submissionDetails($titleSlug: String!) {
        question(titleSlug: $titleSlug) {
            submissions {
                id
                code
                runtime
                memory
                statusDisplay
                lang
                timestamp
            }
        }
    }
    """
    
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0',
        'Cookie': os.environ.get('LEETCODE_COOKIE', ''),  # Wichtig für Authentifizierung
        'Referer': f'https://leetcode.com/problems/{titleSlug}/'
    }
    
    payload = {
        'query': query,
        'variables': {'titleSlug': titleSlug}
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.encoding = 'utf-8'
        print(f"Submission details response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            return data.get('data', {}).get('question', {}).get('submissions', [])
    except Exception as e:
        print(f"Error fetching submission details: {str(e)}")
    return []

def fetch_recent_submissions(username):
    """Holt die letzten Submissions eines Benutzers"""
    url = "https://leetcode.com/api/submissions/" + username
    
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Cookie': os.environ.get('LEETCODE_COOKIE', ''),  # Wichtig für Authentifizierung
    }
    
    try:
        print(f"Fetching submissions for {username}...")
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            submissions_data = response.json()
            submissions = submissions_data.get('submissions_dump', [])
            print(f"Found {len(submissions)} submissions")
            return submissions
            
    except Exception as e:
        print(f"Error: {str(e)}")
    return []

def save_submission(submission, base_dir):
    """Speichert eine Submission in einer Datei"""
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
        'javascript': '.js'
    }.get(submission['lang'].lower(), '.txt')
    
    filename = f"{problem_title}{file_extension}"
    filepath = os.path.join(lang_dir, filename)
    
    # Bereite Inhalt vor
    content = f"""/*
LeetCode Problem: {submission['title']}
Status: {submission['status_display']}
Language: {submission['lang']}
Runtime: {submission.get('runtime', 'N/A')}
Memory Usage: {submission.get('memory', 'N/A')}
Submission Date: {datetime.fromtimestamp(submission['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}
*/

{submission['code']}
"""
    
    # Speichere die Lösung
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return filepath

def main():
    username = os.environ.get('LEETCODE_USERNAME')
    leetcode_cookie = os.environ.get('LEETCODE_COOKIE')
    
    if not username or not leetcode_cookie:
        print("Error: LEETCODE_USERNAME or LEETCODE_COOKIE not set")
        return
    
    print("Starting LeetCode sync...")
    
    # Erstelle Basis-Verzeichnis
    base_dir = 'leetcode_solutions'
    os.makedirs(base_dir, exist_ok=True)
    
    # Hole Submissions
    submissions = fetch_recent_submissions(username)
    
    if not submissions:
        print("No submissions found or error occurred")
        return
    
    # Speichere nur erfolgreiche Submissions
    saved_count = 0
    for submission in submissions:
        if submission.get('status_display') == 'Accepted':
            filepath = save_submission(submission, base_dir)
            print(f"Saved: {filepath}")
            saved_count += 1
    
    print(f"Successfully saved {saved_count} submissions")
    
    # Update README
    with open(os.path.join(base_dir, 'README.md'), 'w', encoding='utf-8') as f:
        f.write("""# LeetCode Solutions

This repository contains my LeetCode solutions.

## Recent Accepted Submissions:
""")
        for submission in submissions:
            if submission.get('status_display') == 'Accepted':
                date = datetime.fromtimestamp(submission['timestamp']).strftime('%Y-%m-%d')
                f.write(f"\n- {submission['title']} ({submission['lang']})")
                f.write(f"\n  - Submitted: {date}")
                f.write(f"\n  - Runtime: {submission.get('runtime', 'N/A')}")
                f.write(f"\n  - Memory: {submission.get('memory', 'N/A')}\n")

if __name__ == "__main__":
    main()