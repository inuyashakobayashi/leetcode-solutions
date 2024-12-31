import os
import requests
from datetime import datetime

def fetch_leetcode_solutions(username):
    # LeetCode GraphQL API endpoint
    url = "https://leetcode.com/graphql"
    
    # GraphQL Query für die neuesten Submissions
    query = """
    query recentSubmissions($username: String!) {
        recentSubmissions(username: $username) {
            title
            timestamp
            statusDisplay
            lang
            code
        }
    }
    """
    
    # API Request
    response = requests.post(url, json={
        'query': query,
        'variables': {'username': username}
    })
    
    if response.status_code == 200:
        return response.json()
    return None

def save_solution(solution, base_path):
    # Dateierweiterung basierend auf der Programmiersprache
    extensions = {
        'python': '.py',
        'python3': '.py',
        'java': '.java',
        'cpp': '.cpp',
        'javascript': '.js'
    }
    
    # Bereinige den Titel für den Dateinamen
    title = solution['title'].replace(' ', '_').lower()
    ext = extensions.get(solution['lang'].lower(), '.txt')
    filename = f"{title}{ext}"
    filepath = os.path.join(base_path, filename)
    
    # Füge Metadaten als Kommentar hinzu
    content = f"""# {solution['title']}
# Submission Date: {datetime.fromtimestamp(solution['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}
# Status: {solution['statusDisplay']}
# Language: {solution['lang']}

{solution['code']}
"""
    
    # Speichere die Lösung
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return filename

def main():
    username = os.environ.get('LEETCODE_USERNAME')
    if not username:
        print("Error: LEETCODE_USERNAME not set")
        return
    
    # Hole die Lösungen
    solutions = fetch_leetcode_solutions(username)
    if not solutions:
        print("Error: Could not fetch LeetCode solutions")
        return
    
    # Speichere jede Lösung
    for solution in solutions['data']['recentSubmissions']:
        if solution['statusDisplay'] == 'Accepted':
            filename = save_solution(solution, '.')
            print(f"Saved solution: {filename}")

if __name__ == "__main__":
    main()
