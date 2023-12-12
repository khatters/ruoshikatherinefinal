import sqlite3
import json
import os
import requests
import matplotlib.pyplot as plt
import sys
from datetime import datetime
#FLEX CODED VERSION

# Function to create a connection and cursor to the SQLite database
def create_connection(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + "/" + db_name)
    cur = conn.cursor()
    return conn, cur

# Function to retrieve all project IDs from the database
def get_project_ids(cur):
    cur.execute('SELECT projectId FROM projects')
    project_ids = cur.fetchall()
    return [str(project_id[0]) for project_id in project_ids]

# Function to close the connection to the SQLite database
def close_connection(conn):
    conn.close()


def get_startdate_data(cur, conn, api_token, project_ids, limit=25): 
    all_data = []
    for project_id in project_ids:
        

        api_url = "https://techport.nasa.gov/api/projects/" + str(project_id)
        params = {
            "projectId": project_id,
            "limit": limit, 
            
        }

        headers = {
            "Authorization": f"Bearer {api_token}"
        }

        try:
            response = requests.get(api_url, params=params, headers=headers)
            response.raise_for_status()

            data = response.json() 
            all_data.append(data)

        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None

    return all_data

def orgainize_data(all_data):
    project_list = []
    for data in all_data:
        projects = data.get('project', [])
        #print("This is projects:", projects)
        if projects:
            project_id = projects.get('projectId')
            #print("This is project id:", project_id)
            start_date = projects.get("startDateString")
            print(type(start_date))
            #print(f"Project ID: {project_id}, Start Date: {start_date}")
            project_list.append((project_id, start_date))
        
    print(project_list)
    return project_list


# def insert_project_data(project_list, cur, conn):
#     for project_data in project_list:
#         print("This is the initial value:", project_data)
#         project_id, startdate = project_data
#         print(f"Original Start Date ({project_id}): {startdate}")

#         try:
#             startdate = datetime.strptime(startdate, "%b %Y").strftime("%Y-%m-d%") #make it only year and month
#             print(f"Parsed Start Date ({project_id}): {startdate}")
#         except ValueError:
#             print(f"Error parsing startdate: {startdate}")
#             startdate = None

#         if startdate is not None:
#             cur.execute('''
#                 INSERT OR IGNORE INTO projects (projectId, title, startdate)
#                 VALUES (?, NULL, NULL)
#                 ''', (project_id,))

#             cur.execute('''
#                 UPDATE projects
#                 SET startdate = ?
#                 WHERE projectId = ?
#                 ''', (startdate, project_id))
#             print(f"Inserted/Updated project: {project_id}, {startdate}")
#         else:
#             print(f"Skipping project: {project_id} due to parsing error.")

   
        

#     conn.commit()
def insert_project_data(project_list, cur, conn):
    for project_data in project_list:
        print("This is the initial value:", project_data)
        project_id, startdate = project_data
        print(f"Original Start Date ({project_id}): {startdate}")

        try:
            startdate = datetime.strptime(startdate, "%b %Y").strftime("%Y-%m-%d")
            print(f"Parsed Start Date ({project_id}): {startdate}")
        except ValueError:
            print(f"Error parsing startdate: {startdate}")
            startdate = None

        if startdate is not None:
            cur.execute('''
                INSERT OR IGNORE INTO projects (projectId, title, startdate)
                VALUES (?, NULL, NULL)
                ''', (project_id,))

            cur.execute('''
                UPDATE projects
                SET startdate = ?
                WHERE projectId = ?
                ''', (startdate, project_id))
            print(f"Inserted/Updated project: {project_id}, {startdate}")
        else:
            print(f"Skipping project: {project_id} due to parsing error.")

        # cur.execute('''
        #     INSERT OR IGNORE INTO projects (projectId, title, startdate)
        #     VALUES (?, NULL, NULL)
        #     ''', (project_id, startdate))

        # cur.execute('''
        #     UPDATE projects
        #     SET startdate = COALESCE(?, startdate)
        #     WHERE projectId = ?
        #     ''', (startdate, project_id))
        

    conn.commit()


#MATPLOTLIB EQUATIONS
def extract_year(startdate):
    try:
        date_obj = datetime.strptime(startdate, "%b %Y")
        #print("Parsed startdate:", date_obj)
        return date_obj.year
    except ValueError:
        print("Error parsing startdate:", startdate) #see if this stupid thing isn't parsing my dates bc of the weird format
        return None


# def create_pie_chart(year_distribution):
#     labels = list(year_distribution.keys())
#     sizes = list(year_distribution.values())
#     print("Labels:", labels)
#     print("Sizes:", sizes)


#     plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
#     plt.axis('equal')  # draw pie in circle 
#     plt.title('Distribution of Years in Projects')
#     plt.show()

# #new stuff
# def create_bar_chart(year_distribution):
#     years = list(year_distribution.keys())
#     projects_count = list(year_distribution.values())

#     plt.bar(years, projects_count, color='blue')
#     plt.xlabel('Year')
#     plt.ylabel('Number of Projects')
#     plt.title('Distribution of Projects Across Years')
#     plt.show()

def create_charts(year_distribution):
    # pie chart
    labels = list(year_distribution.keys())
    sizes = list(year_distribution.values())

    plt.figure(figsize=(12, 6))

    plt.subplot(1, 2, 1)
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')  # draw pie in circle 
    plt.title('Distribution of Years in Projects')

    #  bar chart
    plt.subplot(1, 2, 2)
    years = list(year_distribution.keys())
    projects_count = list(year_distribution.values())

    plt.bar(years, projects_count, color='blue')
    plt.xlabel('Year')
    plt.ylabel('Number of Projects')
    plt.title('Distribution of Projects Across Years')

    plt.tight_layout()  # Ensures proper spacing between subplots
    plt.show()
#END MATPLOTLIB EQUATIONS

# Function to run the functions in nasadates.py with retrieved project IDs
def run_nasadates_script(project_ids):

    conn, cur = create_connection('spacexprojects3.db')

    # NASA API token
    api_token = "eyJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJUZWNoUG9ydCIsImV4cCI6MTcwMTg5OTQ5NiwibmJmIjoxNzAxODEzMDk2LCJTRVNTSU9OX0lEIjoidTIwbHhKNmxNMzJqdTRFMXRWVDdaeW5EY0VTbEw0WUpJRzVpIiwiRklOR0VSUFJJTlRfSEFTSCI6IkU3NzNBNzRGQUYyQkY0N0Q0MDA2QkJCQUJCNkMzRkE4RDlGMTRFRUE5MTI0MjlBRkU1NThFNjc3NjVBRjE1NTUifQ.g3aSUWPbPm66f-d6l5Z7Bcq3DRKHUa3tUTrEDVa9x2Q"
    result = get_startdate_data(cur, conn, api_token, project_ids, limit=25)
    
    if result:
        formatted_data = orgainize_data(result)

        # Call the insert_project_data function
        insert_project_data(formatted_data, cur, conn)

        year_distribution = {}
        for project_id, start_date in formatted_data:
            year = extract_year(start_date)
            if year:
                year_distribution[year] = year_distribution.get(year, 0) + 1

        # Create and show the pie chart
        #create_pie_chart(year_distribution)
        create_charts(year_distribution)

    

    conn.commit()
    close_connection(conn)

if __name__ == "__main__":
    # Retrieve project IDs from the database
    conn, cur = create_connection('spacexprojects3.db') #GSI -- THIS IS HARDCODED
    project_ids = get_project_ids(cur)
    close_connection(conn)


    run_nasadates_script(project_ids)

api_key = "A7tjXzHzLQYWzLz3cguCfLqhKCGuXe4XRa98a84O" #nasa general API token
#nasa techport api token
api_token = "eyJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJUZWNoUG9ydCIsImV4cCI6MTcwMTg5OTQ5NiwibmJmIjoxNzAxODEzMDk2LCJTRVNTSU9OX0lEIjoidTIwbHhKNmxNMzJqdTRFMXRWVDdaeW5EY0VTbEw0WUpJRzVpIiwiRklOR0VSUFJJTlRfSEFTSCI6IkU3NzNBNzRGQUYyQkY0N0Q0MDA2QkJCQUJCNkMzRkE4RDlGMTRFRUE5MTI0MjlBRkU1NThFNjc3NjVBRjE1NTUifQ.g3aSUWPbPm66f-d6l5Z7Bcq3DRKHUa3tUTrEDVa9x2Q"



