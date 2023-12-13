from datetime import datetime
import requests
import time
import sqlite3
import matplotlib.pyplot as plt
   

def fetch_spacex_articles(api_key, conn):
    base_url = "https://api.nytimes.com/svc/search/v2/articlesearch.json"

    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS spacex_articles (
            headline TEXT PRIMARY KEY,
            formatted_date DATE,
            searching_year INTEGER 
        )
    ''')

    for pub_year in range(2010, 2024):
    
        for print_page in range(0, 30):
            
            params = {
                "q": "spacex stock increase",
                "fq": f'pub_year:({int(pub_year)})',
                "page": print_page,
                "api-key": api_key
            }

            response = requests.get(base_url, params=params)

            
            if response.status_code == 200:
                data = response.json()
                articles = data.get("response", {}).get("docs", [])

                if not articles:
                        
                        time.sleep(12)
                        break

                
                for article in articles:
                    headline = article.get("headline", {}).get("main", "")
                    print(headline)

                    pubdate = article.get("pub_date", "")
                    parsed_date = datetime.strptime(pubdate, "%Y-%m-%dT%H:%M:%S%z")
                    formatted_date = parsed_date.strftime("%Y-%m-01")
                    print(pubdate)

                    try:
                        
                        cursor.execute("INSERT OR IGNORE INTO spacex_articles (headline, formatted_date, searching_year) VALUES (?, ?, ?)",
                                        (headline, formatted_date, pub_year))
                        
                        conn.commit()

                    except Exception as e:
                        print(f"Error inserting data into database: {e}")

                time.sleep(12)

            else:
                print(f"Error: {response.status_code}, {response.text}")

        
        # cursor.close()

def create_pie_chart():
    
    conn = sqlite3.connect('spacexprojects2.db')
    cursor = conn.cursor()

    
    cursor.execute("SELECT searching_year, COUNT(*) FROM spacex_articles GROUP BY searching_year")
    data = cursor.fetchall()

   
    cursor.close()
    conn.close()

   
    labels, sizes = zip(*data)

   
    plt.figure(figsize=(8, 8))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title('Distribution of Articles Over Time')
    plt.axis('equal') 

   
    plt.savefig('article_pie_chart.png')

    
    plt.show()


def create_bar_chart():
    
    conn = sqlite3.connect('spacexprojects2.db')
    cursor = conn.cursor()

   
    cursor.execute("SELECT searching_year, COUNT(*) FROM spacex_articles GROUP BY searching_year")
    data = cursor.fetchall()

    
    cursor.close()
    conn.close()

    
    labels, sizes = zip(*data)

    
    plt.figure(figsize=(10, 6))
    plt.bar(labels, sizes, color='green')
    plt.xlabel('Year')
    plt.ylabel('Number of Articles')
    plt.title('Number of Articles Over Time')
    plt.grid(axis='y')

    
    plt.savefig('article_bar_chart.png')

    
    plt.show()


'''
def create_line_chart():
   
    conn = sqlite3.connect('spacexprojects2.db')
    cursor = conn.cursor()

    
    cursor.execute("SELECT searching_year, COUNT(*) FROM spacex_articles GROUP BY searching_year")
    data = cursor.fetchall()

    
    cursor.close()
    conn.close()

    
    labels, sizes = zip(*data)

    
    plt.figure(figsize=(10, 6))
    plt.plot(labels, sizes, marker='o', linestyle='-', color='green')
    plt.xlabel('Year')
    plt.ylabel('Number of Articles')
    plt.title('Number of Articles Over Time')
    plt.grid(axis='y')

    
    plt.savefig('article_line_chart.png')

    
    plt.show()
'''


def corr_line_graph():
   
    conn = sqlite3.connect('spacexprojects2.db')
    cursor = conn.cursor()

    
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

    
    results = cursor.fetchall()

    
    for row in results:
        print(row)

    
    conn.close()

    
    filtered_results = [result for result in results if result[5] is not None]

    counting_dict = {}
    for result in filtered_results:
        searching_year = result[5]
        counting_dict[searching_year] = counting_dict.get(searching_year, 0) + 1

    sorted_counting_dict = dict(sorted(counting_dict.items()))

    
    searching_years = list(sorted_counting_dict.keys())
    row_counts = list(sorted_counting_dict.values())

    
    plt.plot(searching_years, row_counts, marker='o')
    plt.title('Distribution of Articles Over SpaceX Projects')
    plt.xlabel('Year')
    plt.ylabel('Number of intersection between Articles and Projects')

    plt.savefig('corr_line_chart.png')

    #plt.show()


def corr_pie_chart():
    
    conn = sqlite3.connect('spacexprojects2.db')
    cursor = conn.cursor()

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

    results = cursor.fetchall()

    conn.close()

    filtered_results = [result for result in results if result[5] is not None]

    counting_dict = {}
    for result in filtered_results:
        searching_year = result[5]
        counting_dict[searching_year] = counting_dict.get(searching_year, 0) + 1

    labels = list(counting_dict.keys())
    sizes = list(counting_dict.values())

    plt.figure(figsize=(8, 8))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title('Distribution of Articles Over SpaceX Projects')
    plt.axis('equal')  

    plt.savefig('corr_pie_chart.png')

    #plt.show()

def corr_calculation():
    
    conn = sqlite3.connect('spacexprojects2.db')
    cursor = conn.cursor()

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

    results = cursor.fetchall()

    for row in results:
        print(row)

    conn.close()

    filtered_results = [result for result in results if result[5] is not None]

    counting_dict = {}
    for result in filtered_results:
        searching_year = result[5]
        counting_dict[searching_year] = counting_dict.get(searching_year, 0) + 1

    sorted_counting_dict = dict(sorted(counting_dict.items()))

    searching_years = list(sorted_counting_dict.keys())
    row_counts = list(sorted_counting_dict.values())

    total_rows = sum(row_counts)
    distribution = {year: count / total_rows for year, count in zip(searching_years, row_counts)}

    with open('corr_distribution_data.txt', 'w') as file:
        file.write('Year, Distribution\n')

        for year, percentage in distribution.items():
            file.write(f'{year}: {percentage * 100:.2f}%\n')



if __name__ == "__main__":
    
    # create table
    api_key = "PEiUddLbM3CtpMyTG6SgGeCjecE2A27D"  
    conn = sqlite3.connect('spacexprojects2.db') 

    fetch_spacex_articles(api_key, conn)

    conn.close()

    # draw chart
    create_pie_chart()

    create_bar_chart()  

    #create_line_chart()

    corr_pie_chart()

    corr_line_graph()

    # calculate correlation
    corr_calculation()


