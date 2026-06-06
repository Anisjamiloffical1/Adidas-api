# how to get the api response in json format using requests library in python
# import requests
# import psycopg2
# # this use for getting the api response in json format using requests library in python
# for i in range(1,101):
#     url = f'https://jsonplaceholder.typicode.com/posts/{i}'




#     response =  requests.get(url)

#     print(response.json())
import requests
import sqlite3

# Step 1: Get API data
url = "https://jsonplaceholder.typicode.com/users"
data = requests.get(url).json()

# Step 2: Connect SQLite database (auto creates file)
conn = sqlite3.connect("api_data.db")
cursor = conn.cursor()

# Step 3: Create table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT,
    phone TEXT,
    website TEXT
)
""")

# Step 4: Insert data
for user in data:
    print(data)
    cursor.execute("""
        INSERT OR REPLACE INTO users (id, name, email, phone, website)
        VALUES (?, ?, ?, ?, ?)
    """, (
        user["id"],
        user["name"],
        user["email"],
        user["phone"],
        user["website"]
    ))
    

# Step 5: Save changes
conn.commit()
conn.close()

print("Data saved successfully in SQLite!")

