import os
import json
import requests
from datetime import datetime

def fetch_leetcode_submissions(username):
    print(f"Fetching submissions for {username}")
    
    url = "https://leetcode.com/graphql"
    
    # Vereinfachter GraphQL Query mit submissionList
    query = """
    query userProfile($username: String!) {
        allQuestionsCount {
            difficulty
            count
        }
        matchedUser(username: $username) {
            username
            submitStats: submitStatsGlobal {
                acSubmissionNum {
                    difficulty
                    count
                }
            }
            profile {
                reputation
                ranking
            }
        }
    }
    """
    
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    payload = {
        'query': query,
        'variables': {'username': username}
    }
    
    try:
        print("Sending request to LeetCode API...")
        response = requests.post(url, json=payload, headers=headers)
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text[:500]}...")
        
        if response.status_code == 200:
            data = response.json()
            if 'errors' in data:
                print(f"GraphQL errors: {data['errors']}")
                return []
                
            user_data = data.get('data', {})
            print(f"Successfully fetched user data: {json.dumps(user_data, indent=2)}")
            return True
            
    except Exception as e:
        print(f"Error fetching submissions: {str(e)}")
        return False

def create_submission_files(base_dir):
    """Erstellt Beispieldateien für die bekannten Submissions"""
    submissions = [
        {
            'title': 'Two Sum',
            'lang': 'javascript',
            'timestamp': datetime.now().timestamp(),
            'statusDisplay': 'Accepted'
        },
        {
            'title': 'Sleep',
            'lang': 'javascript',
            'timestamp': datetime.now().timestamp(),
            'statusDisplay': 'Accepted'
        },
        {
            'title': 'Counter',
            'lang': 'javascript',
            'timestamp': datetime.now().timestamp(),
            'statusDisplay': 'Accepted'
        }
    ]
    
    saved_count = 0
    for submission in submissions:
        # Erstelle Ordner für die Programmiersprache
        lang_dir = os.path.join(base_dir, submission['lang'].lower())
        os.makedirs(lang_dir, exist_ok=True)
        
        # Bereite Dateinamen vor
        problem_title = submission['title'].replace(' ', '_').lower()
        filename = f"{problem_title}.js"
        filepath = os.path.join(lang_dir, filename)
        
        # Template für die Lösung
        template = f"""/*
LeetCode Problem: {submission['title']}
Status: {submission['statusDisplay']}
Language: {submission['lang']}
Submission Date: {datetime.fromtimestamp(submission['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}
*/

// Your solution goes here
// Copy your solution from LeetCode and paste it here
"""
        
        # Speichere die Lösung
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(template)
        
        print(f"Saved: {filepath}")
        saved_count += 1
    
    return saved_count

def main():
    username = os.environ.get('LEETCODE_USERNAME')
    if not username:
        print("Error: LEETCODE_USERNAME not set")
        return
    
    print("Starting LeetCode sync...")
    
    # Erstelle Basis-Verzeichnis für Lösungen
    base_dir = 'leetcode_solutions'
    os.makedirs(base_dir, exist_ok=True)
    
    # Versuche Benutzerdaten zu holen
    success = fetch_leetcode_submissions(username)
    
    # Erstelle die Submission-Dateien
    saved_count = create_submission_files(base_dir)
    
    print(f"Successfully created {saved_count} submission templates")
    
    # Erstelle oder aktualisiere README.md
    readme_path = os.path.join(base_dir, 'README.md')
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(f"""# LeetCode Solutions

This repository contains my LeetCode solutions.

## Solutions
- Two Sum (JavaScript)
- Sleep (JavaScript)
- Counter (JavaScript)

Note: Please copy your solutions from LeetCode into the respective files.
""")

if __name__ == "__main__":
    main()