import unittest
import sqlite3
import json
import os
import requests
import matplotlib.pyplot as plt

#HARD CODED VERSION
def create_database(db_name): 
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+"/"+db_name)
    cur = conn.cursor()

    cur.execute('''
            CREATE TABLE IF NOT EXISTS projdate (
                projectId INTEGER PRIMARY KEY,
                startdate TEXT,
                acronym TEXT,
                website TEXT
            )
        ''')

    conn.commit()
    return cur, conn

def get_startdate_data(cur, conn, api_token, project_Id, limit=25): 
    all_data = []
    for project in project_Id: 
        print(project)
        # Get the count of records in the database
        cur.execute('SELECT COUNT(*) FROM projdate')
        count = cur.fetchone()[0]

        api_url = "https://techport.nasa.gov/api/projects/"+ str(project)
        params = {
            "projectId": project,
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
            all_data.append(data)

            # print(type(data))
            #print(data)
        
            #insert_project_data(cur, conn, data) #should I be inserting it here? 

            

        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None
    print(all_data)
    return all_data

def orgainize_data(all_data):
    project_list = []
    for data in all_data:
        projects = data.get('project', [])
        #print("This is projects:", projects)
        if projects:
            project_id = projects.get('projectId')
            print("This is project id:", project_id)
            start_date = projects.get("startDateString")
            project_list.append((project_id, start_date))
        
    print(project_list)
    return project_list


def insert_project_data(project_list, cur, conn):
    cur.execute('SELECT COUNT(*) as row_count FROM projdate')
    row_count = cur.fetchone()[0]
    print("This is row_count:", row_count)
   
    # start_index = (row_count // 25) * 25
    # end_index = start_index+25
    to_insert = project_list
    print("This is the to insert:", to_insert)
    print("this is the length:", len(to_insert))
  
    for project_data in to_insert:
        print(project_data)
        projectId = project_data[0]
        startdate = project_data[1]
        #projectId, startdate = project_data
        cur.execute('''
            INSERT OR IGNORE INTO projdate (projectId, startdate)
            VALUES (?, ?)
            ''', (projectId, startdate))
    print(f"Inserted project: {projectId}, {startdate}")

    conn.commit()

#ending function stuff: 
cur, conn = create_database('projectdates.db')


api_key = "A7tjXzHzLQYWzLz3cguCfLqhKCGuXe4XRa98a84O" #nasa general API token
#nasa techport api token
api_token = "eyJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJUZWNoUG9ydCIsImV4cCI6MTcwMTg5OTQ5NiwibmJmIjoxNzAxODEzMDk2LCJTRVNTSU9OX0lEIjoidTIwbHhKNmxNMzJqdTRFMXRWVDdaeW5EY0VTbEw0WUpJRzVpIiwiRklOR0VSUFJJTlRfSEFTSCI6IkU3NzNBNzRGQUYyQkY0N0Q0MDA2QkJCQUJCNkMzRkE4RDlGMTRFRUE5MTI0MjlBRkU1NThFNjc3NjVBRjE1NTUifQ.g3aSUWPbPm66f-d6l5Z7Bcq3DRKHUa3tUTrEDVa9x2Q"
project_Id= ['146530', '6451', '7308']


result = get_startdate_data(cur, conn, api_token, project_Id, limit=25)

if result: 
    for project_data in result:
        formatted_data = orgainize_data(result)
        insert_project_data(formatted_data, cur, conn)

conn.close()


