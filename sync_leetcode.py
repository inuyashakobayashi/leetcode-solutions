import os
import json
import requests
from datetime import datetime

def fetch_leetcode_solutions(username):
    print(f"Versuche Lösungen für Benutzer {username} abzurufen...")
    
    url = "https://leetcode.com/graphql"
    
    # GraphQL Query für die letzten Submissions
    query = """
    {
      matchedUser(username: "%s") {
        submitStats {
          acSubmissionNum {
            difficulty
            count
            submissions
          }
        }
        submissionCalendar
        submitStatsGlobal {
          submissions
        }
      }
    }
    """ % username
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    
    try:
        print("Sende API Request zu LeetCode...")
        response = requests.post(
            url, 
            json={'query': query},
            headers=headers
        )
        
        print(f"API Response Status: {response.status_code}")
        print(f"API Response Content: {response.text[:200]}...")  # Erste 200 Zeichen
        
        if response.status_code == 200:
            data = response.json()
            if data.get('errors'):
                print(f"GraphQL Fehler: {data['errors']}")
                return None
            return data
        else:
            print(f"Fehler beim API-Aufruf: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Exception beim API-Aufruf: {str(e)}")
        return None

def save_solution(data, base_path):
    try:
        print(f"Speichere Daten in: {base_path}")
        
        # Erstelle einen Ordner für die Statistiken
        stats_path = os.path.join(base_path, 'stats')
        os.makedirs(stats_path, exist_ok=True)
        
        # Speichere die rohen API-Daten für Debug-Zwecke
        with open(os.path.join(stats_path, 'leetcode_data.json'), 'w') as f:
            json.dump(data, f, indent=2)
            
        print("Daten erfolgreich gespeichert!")
        return True
        
    except Exception as e:
        print(f"Fehler beim Speichern der Daten: {str(e)}")
        return False

def main():
    print("Start des LeetCode Sync Scripts...")
    
    # Hole Username aus Umgebungsvariablen
    username = os.environ.get('LEETCODE_USERNAME')
    if not username:
        print("Fehler: LEETCODE_USERNAME nicht gesetzt!")
        return
    
    print(f"Arbeitsverzeichnis: {os.getcwd()}")
    print(f"Verzeichnisinhalt: {os.listdir('.')}")
    
    # Hole die Lösungen
    solutions = fetch_leetcode_solutions(username)
    if not solutions:
        print("Fehler: Konnte keine LeetCode-Lösungen abrufen")
        return
    
    # Speichere die Lösungen
    success = save_solution(solutions, '.')
    if success:
        print("Sync erfolgreich abgeschlossen!")
    else:
        print("Fehler beim Speichern der Lösungen")

if __name__ == "__main__":
    main()