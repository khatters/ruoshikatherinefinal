from datetime import datetime
import requests
import time
import sqlite3



def fetch_spacex_articles(api_key, conn):
    base_url = "https://api.nytimes.com/svc/search/v2/articlesearch.json"

    # Connect to SQLite database (create it if not exists)
    cursor = conn.cursor()

    # Create the table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS spacex_articles (
            headline TEXT PRIMARY KEY,
            formatted_date DATE,
            searching_year INTEGER 
        )
    ''')

    for pub_year in range(2010, 2024):
    
        for print_page in range(0, 30):
            # Specify both query and filter parameters
            params = {
                "q": "spacex stock increase",
                "fq": f'pub_year:({int(pub_year)})',
                "page": print_page,
                "api-key": api_key
            }

            response = requests.get(base_url, params=params)

            # Check if the request was successful
            if response.status_code == 200:
                data = response.json()
                articles = data.get("response", {}).get("docs", [])

                if not articles:
                        # No articles on this page, break out of the inner loop
                        time.sleep(12)
                        break

                # Extract and print article titles
                for article in articles:
                    headline = article.get("headline", {}).get("main", "")
                    print(headline)

                    pubdate = article.get("pub_date", "")
                    parsed_date = datetime.strptime(pubdate, "%Y-%m-%dT%H:%M:%S%z")
                    formatted_date = parsed_date.strftime("%Y-%m-01")
                    print(pubdate)

                    try:
                        # Insert or ignore (if the headline already exists) into the database
                        cursor.execute("INSERT OR IGNORE INTO spacex_articles (headline, formatted_date, searching_year) VALUES (?, ?, ?)",
                                        (headline, formatted_date, pub_year))
                        # Commit the changes
                        conn.commit()

                    except Exception as e:
                        print(f"Error inserting data into database: {e}")

                
                # Introduce a delay between requests to avoid rate limiting
                time.sleep(12)

            else:
                print(f"Error: {response.status_code}, {response.text}")

        # Close the cursor
        # cursor.close()

if __name__ == "__main__":
    api_key = "PEiUddLbM3CtpMyTG6SgGeCjecE2A27D"  # Replace with your actual New York Times API key
    conn = sqlite3.connect('spacexprojects2.db')  # Change the database name if needed

    fetch_spacex_articles(api_key, conn)

    conn.close()
