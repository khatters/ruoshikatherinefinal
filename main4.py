from datetime import datetime
import requests
import time
import sqlite3


def get_row_count(cursor):
    # Execute a SELECT statement to count the rows
    cursor.execute("SELECT COUNT(*) FROM spacex_articles")
    row_count = cursor.fetchone()[0]
    return row_count



def fetch_spacex_articles(api_key, conn):
    base_url = "https://api.nytimes.com/svc/search/v2/articlesearch.json"

    # Connect to SQLite database (create it if not exists)
    cursor = conn.cursor()

    # Create the table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS spacex_articles (
            article_count INTEGER PRIMARY KEY,
            formatted_date DATE
        )
    ''')

    # Check the number of rows before inserting
    initial_row_count = int(get_row_count(cursor))
    print(f"Initial number of rows in the database: {initial_row_count}")

    pub_year = 2010 + initial_row_count//12

    # Iterate over print pages 1 to 100 and pub_years 2010 to 2023
    for pub_month in range(1, 13):

        article_count = 0

        for print_page in range(0, 100):
            # Specify both query and filter parameters
            params = {
                "q": "tesla stock",
                "fq": f'pub_year:({int(pub_year)}) AND pub_month:({int(pub_month)})',
                "page": print_page,
                "api-key": api_key
            }

            response = requests.get(base_url, params=params)

            # Check if the request was successful
            if response.status_code == 200:
                data = response.json()
                articles = data.get("response", {}).get("docs", [])

                '''
                
                # Extract and print article titles
                for article in articles:
                    headline = article.get("headline", {}).get("main", "")
                    print(headline)

                    pubdate = article.get("pub_date", "")
                    parsed_date = datetime.strptime(pubdate, "%Y-%m-%dT%H:%M:%S%z")
                    formatted_date = parsed_date.strftime("%Y-%m")
                    print(pubdate)
                
                '''

                if not articles:
                    # No articles on this page, break out of the inner loop
                    break


                # Count the number of articles
                article_count += len(articles)

            else:
                print(f"Error: {response.status_code}, {response.text}")
            
            # Introduce a delay between requests to avoid rate limiting
            time.sleep(15)
        
        formatted_date = datetime(pub_year, pub_month, 1).strftime("%Y-%m-%d")
        print(f"Number of articles for {formatted_date}: {article_count}")

        try:
            # Insert or ignore (if the headline already exists) into the database
            cursor.execute("INSERT OR IGNORE INTO spacex_articles (formatted_date, article_count) VALUES (?, ?)",
                        (formatted_date, article_count))
            
            conn.commit()

        except Exception as e:
            print(f"Error inserting data into database: {e}")

       


    # Close the cursor
    # cursor.close()

if __name__ == "__main__":
    api_key = "VYkwtRJvHXz83t0AsMM42OGqQSyOnKEr"  # Replace with your actual New York Times API key
    conn = sqlite3.connect('spacex_articles.db')  # Change the database name if needed

    fetch_spacex_articles(api_key, conn)

    conn.close()
