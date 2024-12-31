import os
import json
import requests
from datetime import datetime

def fetch_leetcode_submissions(username):
    print(f"Fetching submissions for {username}")
    
    url = "https://leetcode.com/graphql"
    
    # Korrigierter GraphQL Query
    query = """
    query submissions($username: String!) {
        recentAcSubmissions(username: $username) {
            submissionId
            title
            titleSlug
            timestamp
            statusDisplay
            lang
        }
    }
    """
    
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }
    
    # Request Body
    payload = {
        'query': query,
        'variables': {'username': username}
    }
    
    try:
        print("Sending request to LeetCode API...")
        response = requests.post(url, json=payload, headers=headers)
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text[:200]}...")
        
        if response.status_code == 200:
            data = response.json()
            if 'errors' in data:
                print(f"GraphQL errors: {data['errors']}")
                return []
            submissions = data.get('data', {}).get('recentAcSubmissions', [])
            print(f"Found {len(submissions)} submissions")
            
            # Hole zusätzliche Details für jede Submission
            detailed_submissions = []
            for sub in submissions:
                details = fetch_submission_detail(sub['titleSlug'], sub['submissionId'])
                if details:
                    detailed_submissions.append({**sub, **details})
            
            return detailed_submissions
            
    except Exception as e:
        print(f"Error fetching submissions: {str(e)}")
        return []

def fetch_submission_detail(titleSlug, submissionId):
    """Hole zusätzliche Details für eine spezifische Submission"""
    url = "https://leetcode.com/graphql"
    
    query = """
    query submissionDetails($titleSlug: String!) {
        question(titleSlug: $titleSlug) {
            questionId
            difficulty
            content
            stats
            codeDefinition
        }
    }
    """
    
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }
    
    payload = {
        'query': query,
        'variables': {'titleSlug': titleSlug}
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json().get('data', {}).get('question', {})
    except Exception as e:
        print(f"Error fetching submission details: {str(e)}")
    return {}

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
    
    # Template für die Lösung
    template = f"""/*
Problem: {submission['title']}
Difficulty: {submission.get('difficulty', 'Unknown')}
Status: {submission['statusDisplay']}
Submission Date: {datetime.fromtimestamp(submission['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}
*/

// Your submission was:
"""
    
    # Speichere die Lösung
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(template)
    
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
        print("No submissions found or error occurred")
        return
    
    # Speichere die Submissions
    saved_count = 0
    for submission in submissions:
        filepath = save_submission(submission, base_dir)
        print(f"Saved: {filepath}")
        saved_count += 1
    
    print(f"Successfully saved {saved_count} submissions")

if __name__ == "__main__":
    main()