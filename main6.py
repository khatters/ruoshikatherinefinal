from datetime import datetime
import requests
import time
import sqlite3
import matplotlib.pyplot as plt


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
    


def create_pie_chart():
    # Connect to SQLite database
    conn = sqlite3.connect('spacexprojects2.db')
    cursor = conn.cursor()

    # Query data from the spacex_articles table
    cursor.execute("SELECT searching_year, COUNT(*) FROM spacex_articles GROUP BY searching_year")
    data = cursor.fetchall()

    # Close the cursor and connection
    cursor.close()
    conn.close()

    # Process the data for the pie chart
    labels, sizes = zip(*data)

    # Create a pie chart
    plt.figure(figsize=(8, 8))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title('Distribution of Articles Over Time')
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    # Save the pie chart to a file (e.g., PNG)
    plt.savefig('article_pie_chart.png')

    # Display the pie chart
    plt.show()


def create_bar_chart():
    # Connect to SQLite database
    conn = sqlite3.connect('spacexprojects2.db')
    cursor = conn.cursor()

    # Query data from the spacex_articles table
    cursor.execute("SELECT searching_year, COUNT(*) FROM spacex_articles GROUP BY searching_year")
    data = cursor.fetchall()

    # Close the cursor and connection
    cursor.close()
    conn.close()

    # Process the data for the bar chart
    labels, sizes = zip(*data)

    # Create a bar chart
    plt.figure(figsize=(10, 6))
    plt.bar(labels, sizes, color='green')
    plt.xlabel('Year')
    plt.ylabel('Number of Articles')
    plt.title('Number of Articles Over Time')
    plt.grid(axis='y')

    # Save the bar chart to a file (e.g., PNG)
    plt.savefig('article_bar_chart.png')

    # Display the bar chart
    plt.show()


def create_line_chart():
    # Connect to SQLite database
    conn = sqlite3.connect('spacexprojects2.db')
    cursor = conn.cursor()

    # Query data from the spacex_articles table
    cursor.execute("SELECT searching_year, COUNT(*) FROM spacex_articles GROUP BY searching_year")
    data = cursor.fetchall()

    # Close the cursor and connection
    cursor.close()
    conn.close()

    # Process the data for the line chart
    labels, sizes = zip(*data)

    # Create a line chart
    plt.figure(figsize=(10, 6))
    plt.plot(labels, sizes, marker='o', linestyle='-', color='green')
    plt.xlabel('Year')
    plt.ylabel('Number of Articles')
    plt.title('Number of Articles Over Time')
    plt.grid(axis='y')

    # Save the line chart to a file (e.g., PNG)
    plt.savefig('article_line_chart.png')

    # Display the line chart
    plt.show()


def corr_line_graph():
    # Connect to the database
    conn = sqlite3.connect('spacexprojects2.db')
    cursor = conn.cursor()

    # Execute the join query
    cursor.execute('''
        SELECT
            projects.projectId,
            projects.title,
            projects.startdate,
            spacex_articles.*
        FROM
            projects
        LEFT JOIN spacex_articles ON projects.startdate = spacex_articles.formatted_date
    ''')

    # Fetch the results
    results = cursor.fetchall()

    # Display or process the results as needed
    for row in results:
        print(row)

    # Close the connection
    conn.close()

    # Filter out rows where formatted_date is None
    filtered_results = [result for result in results if result[5] is not None]

    # Count the number of rows for each searching_year
    counting_dict = {}
    for result in filtered_results:
        searching_year = result[5]
        counting_dict[searching_year] = counting_dict.get(searching_year, 0) + 1

    sorted_counting_dict = dict(sorted(counting_dict.items()))

    # Process the data for the line chart
    searching_years = list(sorted_counting_dict.keys())
    row_counts = list(sorted_counting_dict.values())

    # Create a line chart
    plt.plot(searching_years, row_counts, marker='o')
    plt.title('Distribution of Articles Over SpaceX Projects')
    plt.xlabel('Year')
    plt.ylabel('Number of intersection between Articles and Projects')

    plt.savefig('corr_line_chart.png')

    # Show the line chart
    #plt.show()


def corr_pie_chart():
    # Connect to the database
    conn = sqlite3.connect('spacexprojects2.db')
    cursor = conn.cursor()

    # Execute the join query
    cursor.execute('''
        SELECT
            projects.projectId,
            projects.title,
            projects.startdate,
            spacex_articles.*
        FROM
            projects
        LEFT JOIN spacex_articles ON projects.startdate = spacex_articles.formatted_date
    ''')

    # Fetch the results
    results = cursor.fetchall()

    # Close the connection
    conn.close()

    # Filter out rows where formatted_date is None
    filtered_results = [result for result in results if result[5] is not None]

    # Count the number of rows for each searching_year
    counting_dict = {}
    for result in filtered_results:
        searching_year = result[5]
        counting_dict[searching_year] = counting_dict.get(searching_year, 0) + 1

    # Process the data for the pie chart
    labels = list(counting_dict.keys())
    sizes = list(counting_dict.values())

    # Create a pie chart
    plt.figure(figsize=(8, 8))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title('Distribution of Articles Over SpaceX Projects')
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    plt.savefig('corr_pie_chart.png')

    # Show the pie chart
    #plt.show()


def corr_calculation():
    # Connect to the database
    conn = sqlite3.connect('spacexprojects2.db')
    cursor = conn.cursor()

    # Execute the join query
    cursor.execute('''
        SELECT
            projects.projectId,
            projects.title,
            projects.startdate,
            spacex_articles.*
        FROM
            projects
        LEFT JOIN spacex_articles ON projects.startdate = spacex_articles.formatted_date
    ''')

    # Fetch the results
    results = cursor.fetchall()

    # Display or process the results as needed
    for row in results:
        print(row)

    # Close the connection
    conn.close()

    # Filter out rows where formatted_date is None
    filtered_results = [result for result in results if result[5] is not None]


    # Count the number of rows for each searching_year
    counting_dict = {}
    for result in filtered_results:
        searching_year = result[5]
        counting_dict[searching_year] = counting_dict.get(searching_year, 0) + 1

    sorted_counting_dict = dict(sorted(counting_dict.items()))

    # Process the data for the line chart
    searching_years = list(sorted_counting_dict.keys())
    row_counts = list(sorted_counting_dict.values())

    # Calculate the distribution
    total_rows = sum(row_counts)
    distribution = {year: count / total_rows for year, count in zip(searching_years, row_counts)}

    # Write the calculated data to a file
    with open('corr_distribution_data.txt', 'w') as file:
        for year, percentage in distribution.items():
            file.write(f'{year}: {percentage * 100:.2f}%\n')



if __name__ == "__main__":
    '''
    api_key = "PEiUddLbM3CtpMyTG6SgGeCjecE2A27D"  # Replace with your actual New York Times API key
    conn = sqlite3.connect('spacexprojects2.db')  # Change the database name if needed

    fetch_spacex_articles(api_key, conn)

    conn.close()

    create_pie_chart()

    #create_bar_chart()  

    create_line_chart()

    '''
    #corr_pie_chart()

    #corr_line_graph()

    corr_calculation()


