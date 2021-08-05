#create and set up a connection for a sqlite db 
#import the sqlite3 package
import sqlite3
from sqlite3 import Error

#defining the connection to the db 
def create_connection(database):
    try:
        #defining db connection params 
        conn = sqlite3.connect(
        database, isolation_level=None, check_same_thread=False)
        conn.row_factory = lambda c, r: dict(
        zip([col[0] for col in c.description], r))
        return conn
    #return error if connection cannot be made    
    except Error as e:
        print(e)

#create a new table in the db
def create_table(c, sql):
    c.execute(sql)

#creating a page in the db
def create_pages(c, data):
    print(data)
    sql = ''' INSERT INTO pages(name,session,first_visited)
        VALUES (?,?,?) '''
    c.execute(sql, data)

#updateing exisitng record
def update_pages(c, pageId):
    print(pageId)
    sql = ''' UPDATE pages
            SET visits = visits+1 
            WHERE id = ?'''
    c.execute(sql, [pageId])

#checking function to see what needs to be used: Update - Create
def update_or_create_page(c, data):
    sql = "SELECT * FROM pages where name=? and session=?"
    c.execute(sql, data[:-1])
    result = c.fetchone()
    #if result of checking name and session returns NONE use Create func
    if result == None:
         create_pages(c, data)
    else:
    #else update the page    
        print(result)
        update_pages(c, result['id'])

#function which inputs user session data into table once a new connection has been created
def create_session(c, data):
    sql = ''' INSERT INTO sessions(ip, continent, country, city, os, browser, session, created_at)
            VALUES (?,?,?,?,?,?,?,?) '''
    c.execute(sql, data)

#select all sessions from the table
def select_all_sessions(c):
    sql = "SELECT * FROM sessions"
    c.execute(sql)
    rows = c.fetchall()
    return rows

#select all the pages from the table
def select_all_pages(c):
    sql = "SELECT * FROM pages"
    c.execute(sql)
    rows = c.fetchall()
    return rows

#select all user visits from table 
def select_all_user_visits(c, session_id):
    sql = "SELECT * FROM pages where session =?"
    c.execute(sql, [session_id])
    rows = c.fetchall()
    return rows

#init the main function of the program
def main():
    #init the db
    database = "./pythonsqlite.db"
    #defining column params for each input 
   #connection data
    sql_create_pages = """ 
        CREATE TABLE IF NOT EXISTS pages (
        id integer PRIMARY KEY,
        name varchar(225) NOT NULL,
        session varchar(255) NOT NULL,
        first_visited datetime NOT NULL,
        visits integer NOT NULL Default 1
        ); 
        """
        #session data
    sql_create_session = """ 
        CREATE TABLE IF NOT EXISTS sessions (
        id integer PRIMARY KEY,
        ip varchar(225) NOT NULL,
        continent varchar(225) NOT NULL, 
        country varchar(225) NOT NULL,
        city varchar(225) NOT NULL, 
        os varchar(225) NOT NULL, 
        browser varchar(225) NOT NULL, 
        session varchar(225) NOT NULL,
        created_at datetime NOT NULL
        ); 
        """

    # create a database connection within the main fuction
    conn = create_connection(database)
    if conn is not None:
     # create tables
        create_table(conn, sql_create_pages)
        create_table(conn, sql_create_session)
        print("Connection established!")
    else:
        print("Could not establish connection")
if __name__ == '__main__':
    main()
