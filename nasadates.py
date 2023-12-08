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
        # cur.execute('SELECT COUNT(*) FROM projects WHERE projectId = ?', (project_id,))
        # count = cur.fetchone()[0]

        api_url = "https://techport.nasa.gov/api/projects/" + str(project_id)
        params = {
            "projectId": project_id,
            "limit": limit, 
            #"offset": count
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
            project_list.append((project_id, start_date))
        
    #print(project_list)
    return project_list


# def insert_project_data(project_list, cur, conn):
#     cur.execute('SELECT COUNT(*) as row_count FROM projdate')
#     row_count = cur.fetchone()[0]
#     #print("This is row_count:", row_count)
   
#     # start_index = (row_count // 25) * 25
#     # end_index = start_index+25
#     to_insert = project_list
#     #print("This is the to insert:", to_insert)
#     #print("this is the length:", len(to_insert))
  
#     for project_data in to_insert:
#         #print(project_data)
#         projectId = project_data[0]
#         startdate = project_data[1]

#         cur.execute('''
#             INSERT OR IGNORE INTO projdate (projectId, startdate)
#             VALUES (?, ?)
#             ''', (projectId, startdate))
#     print(f"Inserted project: {projectId}, {startdate}")

#     conn.commit()

def insert_project_data(project_list, cur, conn):
    for project_data in project_list:
        project_id, startdate = project_data

        cur.execute('''
            INSERT OR IGNORE INTO projects (projectId, title, startdate)
            VALUES (?, NULL, NULL)
            ''', (project_id,))

        cur.execute('''
            UPDATE projects
            SET startdate = COALESCE(?, startdate)
            WHERE projectId = ?
            ''', (startdate, project_id))

    conn.commit()
    print(f"Inserted/Updated project: {project_id}, {startdate}")


# def get_shared_data(projectId, title, startdate, conn, cur, ):
#     tuple_list = []
#     query = """SELECT projects.title, projdate.startdate, projdate.projectId 
#     FROM projects 
#     JOIN projdate ON projects.projectId = projdate.projectId
#     WHERE projects.title == ? AND projdate.startdate == ? AND projdate.projectId ==? """
#     #print("SQL Query:", query)
#     #print("Parameters:", (title, startdate, projectId))

#     cur.execute(query, (title, startdate, projectId))
#     result = cur.fetchall()
#     #print(result)
#     return result

#MATPLOTLIB EQUATIONS
# def extract_year(startdate):
#     try:
#         date_obj = datetime.strptime(startdate, "%b %Y")
#         return date_obj.year
#     except ValueError:
#         return None


# def create_pie_chart(year_distribution):
#     labels = list(year_distribution.keys())
#     sizes = list(year_distribution.values())
#     print("Testing Plotlib")
#     plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
#     plt.axis('equal')  # draw pie in circle 
#     plt.title('Distribution of Years in Projects')
#     plt.show(block=True)
# #END MATPLOTLIB EQUATIONS 


# Function to run the functions in nasadates.py with retrieved project IDs
def run_nasadates_script(project_ids):

    conn, cur = create_connection('spacexprojects2.db')

    # NASA API token
    api_token = "eyJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJUZWNoUG9ydCIsImV4cCI6MTcwMTg5OTQ5NiwibmJmIjoxNzAxODEzMDk2LCJTRVNTSU9OX0lEIjoidTIwbHhKNmxNMzJqdTRFMXRWVDdaeW5EY0VTbEw0WUpJRzVpIiwiRklOR0VSUFJJTlRfSEFTSCI6IkU3NzNBNzRGQUYyQkY0N0Q0MDA2QkJCQUJCNkMzRkE4RDlGMTRFRUE5MTI0MjlBRkU1NThFNjc3NjVBRjE1NTUifQ.g3aSUWPbPm66f-d6l5Z7Bcq3DRKHUa3tUTrEDVa9x2Q"


    result = get_startdate_data(cur, conn, api_token, project_ids, limit=25)

    if result: 
        #year_distribution = {} #FOR MATPLOTLIB
        for project_data in result:
            formatted_data = orgainize_data(result)
            insert_project_data(formatted_data, cur, conn)

            # shared_data = get_shared_data(project_data[0], project_data[1], project_data[2], conn, cur)
            # print("Shared Data:", shared_data)

            #matplotlib calcs: 
            # for project_id, start_date in formatted_data: 
            #     year = extract_year(start_date)
            #     if year: 
            #         year_distribution[year]=year_distribution.get(year, 0)+1

            # create_pie_chart(year_distribution)

    conn.commit()
    close_connection(conn)

if __name__ == "__main__":
    # Retrieve project IDs from the database
    conn, cur = create_connection('spacexprojects2.db') #GSI -- THIS IS HARDCODED
    project_ids = get_project_ids(cur)
    close_connection(conn)


    run_nasadates_script(project_ids)

api_key = "A7tjXzHzLQYWzLz3cguCfLqhKCGuXe4XRa98a84O" #nasa general API token
#nasa techport api token
api_token = "eyJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJUZWNoUG9ydCIsImV4cCI6MTcwMTg5OTQ5NiwibmJmIjoxNzAxODEzMDk2LCJTRVNTSU9OX0lEIjoidTIwbHhKNmxNMzJqdTRFMXRWVDdaeW5EY0VTbEw0WUpJRzVpIiwiRklOR0VSUFJJTlRfSEFTSCI6IkU3NzNBNzRGQUYyQkY0N0Q0MDA2QkJCQUJCNkMzRkE4RDlGMTRFRUE5MTI0MjlBRkU1NThFNjc3NjVBRjE1NTUifQ.g3aSUWPbPm66f-d6l5Z7Bcq3DRKHUa3tUTrEDVa9x2Q"



