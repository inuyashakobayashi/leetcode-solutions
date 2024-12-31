import os
import json
import requests
from datetime import datetime

def fetch_leetcode_submissions(username):
    print(f"Fetching submissions for {username}")
    
    # GraphQL API endpoint
    url = "https://leetcode.com/graphql"
    
    # GraphQL query für die neuesten Submissions
    query = """
    query recentSubmissionList($username: String!) {
        recentSubmissionList(username: $username) {
            title
            timestamp
            statusDisplay
            lang
            code
            runtime
            memory
            id
            notes
            topicTags {
                name
            }
        }
    }
    """
    
    # Headers mit mehr Browser-ähnlichen Informationen
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Origin': 'https://leetcode.com',
        'Referer': 'https://leetcode.com/',
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
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            if 'errors' in data:
                print(f"GraphQL errors: {data['errors']}")
                return []
            submissions = data.get('data', {}).get('recentSubmissionList', [])
            print(f"Found {len(submissions)} submissions")
            return submissions
        else:
            print(f"Response content: {response.text[:200]}...")  # Erste 200 Zeichen
            return []
            
    except Exception as e:
        print(f"Error fetching submissions: {str(e)}")
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
    content = f"""/*
Problem: {submission['title']}
Status: {submission['statusDisplay']}
Runtime: {submission.get('runtime', 'N/A')}
Memory: {submission.get('memory', 'N/A')}
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
    
    # Speichere nur erfolgreiche Submissions
    saved_count = 0
    for submission in submissions:
        if submission.get('statusDisplay') == 'Accepted':
            filepath = save_submission(submission, base_dir)
            print(f"Saved: {filepath}")
            saved_count += 1
    
    print(f"Successfully saved {saved_count} submissions")

if __name__ == "__main__":
    main()