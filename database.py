import sqlite3
import json


def create_table(cur):
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            userId TEXT NOT NULL PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            task_list TEXT,
            isActive BOOLEAN
                                            )
        ''')

def database(command, userId=None, username=None, password=None, updateTaskList=None, isActive=None):
    # Connect to database
    dataFile = "tasks.db"
    conn = sqlite3.connect(dataFile)
    cur = conn.cursor()
    # create table
    if command == "create":
        # create "users" table if not exist
        create_table(cur)
        # task_list(string): ["eat","bed","play"]
        task_list_json = json.dumps(updateTaskList)
        # insert initial values
        cur.execute('INSERT INTO users (userId, username, password, task_list, isActive) VALUES (?, ?, ?, ?, ?)',
                    (userId, username, password, task_list_json, isActive))
    # read table
    elif command == "read":
        # create "users" table if not exist
        create_table(cur)
        cur.execute("SELECT * from users WHERE userId = ?", (userId,))
        userData = cur.fetchall()
        if len(userData) < 1:  # userId not exist
            return False
        # userId, username, password, task_list, status = userData
        return userData[0]
    # update table
    elif command == "update":
        # create "users" table if not exist
        create_table(cur)
        if username != None:
            cur.execute(
                "UPDATE users SET username = ? WHERE userId = ?", (username, userId))
        if password != None:
            cur.execute(
                "UPDATE users SET password = ? WHERE userId = ?", (password, userId))
        if updateTaskList != None:
            updateTaskList = json.dumps(updateTaskList)
            cur.execute(
                "UPDATE users SET task_list = ? WHERE userId = ?", (updateTaskList, userId))
        if isActive != None:
            cur.execute(
                "UPDATE users SET isActive = ? WHERE userId = ?", (isActive, userId))
    # delte table
    elif command == "delete":
        # create "users" table if not exist
        create_table(cur)
        if userId != None:
            cur.execute("DELETE FROM users WHERE userId = ?", (userId,))
        else:
            cur.execute("DROP TABLE IF EXISTS users")

    # Save changes and close the connection
    conn.commit()
    conn.close()
