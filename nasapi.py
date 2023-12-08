import unittest
import sqlite3
import json
import os
import requests
import matplotlib.pyplot as plt

#NO DROP TABLE
def create_database(db_name): #don't mention db_name anywhere else..
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+"/"+db_name)
    cur = conn.cursor()

    cur.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                projectId INTEGER PRIMARY KEY,
                title TEXT,
                acronym TEXT,
                website TEXT,
                startdate DATE
            )
        ''')

    conn.commit()
    return cur, conn

def get_techport_data(cur, conn, api_token, search_term, limit=25): 
    # Get the count of records in the database
    cur.execute('SELECT COUNT(*) FROM projects')
    count = cur.fetchone()[0]

    api_url = "https://techport.nasa.gov/api/projects/search"
    params = {
        "searchQuery": search_term,
        "limit": limit, 
        "offset":count
    }

    headers = {
        "Authorization": f"Bearer {api_token}"
    }

    try:
        response = requests.get(api_url, params=params, headers=headers)
        response.raise_for_status()  # HTTPError for bad responses (4xx or 5xx)

        data = response.json() 

        # print(type(data))
        # print(data)
    
        #insert_project_data(cur, conn, data) #should I be inserting it here? 

        return data

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None


def orgainize_data(data):
    project_list = []
    projects = data.get('projects', [])
    #print("This is projects:", projects)
    #project_info_list = [(projects.get('projectId'), projects.get('title')) for project in projects]
    #print(project_info_list)
    #return project_info_list
    for project in projects: 
        project_ID = project.get('projectId')
        project_title = project.get('title')
        project_list.append((project_ID, project_title))
    
    return project_list


def insert_project_data(project_list, cur, conn):
    cur.execute('SELECT COUNT(*) as row_count FROM projects')
    row_count = cur.fetchone()[0]
    print("This is row_count:", row_count)
   
    # start_index = (row_count // 25) * 25
    # end_index = start_index+25
    to_insert = project_list[row_count:row_count+25]
    print("This is the to insert:", to_insert)
    print("this is the length:", len(to_insert))
  
    for project_data in to_insert:
        projectId, title = project_data
        
        cur.execute('''
            INSERT INTO projects (projectId, title)
            VALUES (?, ?)
            ''', (projectId, title))
    print(f"Inserted project: {projectId}, {title}")

    conn.commit()

#ending function stuff: 
cur, conn = create_database('spacexprojects2.db')


api_key = "A7tjXzHzLQYWzLz3cguCfLqhKCGuXe4XRa98a84O" #nasa general API token
#nasa techport api token
api_token = "eyJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJUZWNoUG9ydCIsImV4cCI6MTcwMTg5OTQ5NiwibmJmIjoxNzAxODEzMDk2LCJTRVNTSU9OX0lEIjoidTIwbHhKNmxNMzJqdTRFMXRWVDdaeW5EY0VTbEw0WUpJRzVpIiwiRklOR0VSUFJJTlRfSEFTSCI6IkU3NzNBNzRGQUYyQkY0N0Q0MDA2QkJCQUJCNkMzRkE4RDlGMTRFRUE5MTI0MjlBRkU1NThFNjc3NjVBRjE1NTUifQ.g3aSUWPbPm66f-d6l5Z7Bcq3DRKHUa3tUTrEDVa9x2Q"
search_term = 'SpaceX'


result = get_techport_data(cur, conn, api_token, search_term, limit=25)

if result: 
    formatted_data = orgainize_data(result)
    insert_project_data(formatted_data, cur, conn)

conn.close()


