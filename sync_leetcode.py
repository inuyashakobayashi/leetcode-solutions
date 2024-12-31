import os
import json
import requests
from datetime import datetime

def fetch_solution(title_slug):
    """Holt die Lösung für ein spezifisches Problem"""
    url = "https://leetcode.com/graphql"
    
    query = """
    query questionData($titleSlug: String!) {
        question(titleSlug: $titleSlug) {
            questionId
            questionFrontendId
            codeSnippets {
                lang
                code
            }
            submissionList {
                statusDisplay
                lang
                code
            }
        }
    }
    """
    
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0',
        'Referer': f'https://leetcode.com/problems/{title_slug}',
        'Cookie': os.environ.get('LEETCODE_COOKIE', '')  # Benötigt für Authentifizierung
    }
    
    payload = {
        'query': query,
        'variables': {'titleSlug': title_slug}
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Solution fetch response: {response.status_code}")
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error fetching solution: {str(e)}")
    return None

def fetch_recent_submissions(username):
    """Holt die letzten Submissions eines Benutzers"""
    url = "https://leetcode.com/graphql"
    
    query = """
    query recentSubmissions($username: String!) {
        recentSubmissionList(username: $username) {
            id
            title
            titleSlug
            timestamp
            statusDisplay
            lang
            code
            runtime
            memory
        }
    }
    """
    
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0',
        'Cookie': os.environ.get('LEETCODE_COOKIE', '')  # Benötigt für Authentifizierung
    }
    
    payload = {
        'query': query,
        'variables': {'username': username}
    }
    
    try:
        print("Fetching recent submissions...")
        response = requests.post(url, json=payload, headers=headers)
        print(f"Submissions response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'errors' in data:
                print(f"GraphQL errors: {data['errors']}")
                return []
            return data.get('data', {}).get('recentSubmissionList', [])
    except Exception as e:
        print(f"Error: {str(e)}")
    return []

def save_submission(submission, base_dir):
    """Speichert eine Submission in einer Datei"""
    lang_dir = os.path.join(base_dir, submission['lang'].lower())
    os.makedirs(lang_dir, exist_ok=True)
    
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
    
    content = f"""/*
LeetCode Problem: {submission['title']}
Status: {submission['statusDisplay']}
Language: {submission['lang']}
Runtime: {submission.get('runtime', 'N/A')}
Memory: {submission.get('memory', 'N/A')}
Submission Date: {datetime.fromtimestamp(submission['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}
*/

{submission.get('code', '// Code nicht verfügbar - Bitte manuell aus LeetCode kopieren')}
"""
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return filepath

def main():
    username = os.environ.get('LEETCODE_USERNAME')
    if not username:
        print("Error: LEETCODE_USERNAME not set")
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
    
    # Speichere jede Submission
    saved_count = 0
    for submission in submissions:
        if submission['statusDisplay'] == 'Accepted':
            filepath = save_submission(submission, base_dir)
            print(f"Saved: {filepath}")
            saved_count += 1
    
    print(f"Successfully saved {saved_count} submissions")
    
    # Update README
    with open(os.path.join(base_dir, 'README.md'), 'w', encoding='utf-8') as f:
        f.write("""# LeetCode Solutions

This repository contains my LeetCode solutions.

## Recent Accepted Submissions
""")
        for submission in submissions:
            if submission['statusDisplay'] == 'Accepted':
                date = datetime.fromtimestamp(submission['timestamp']).strftime('%Y-%m-%d')
                f.write(f"\n- {submission['title']} ({submission['lang']}) - {date}")

if __name__ == "__main__":
    main()