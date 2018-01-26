# Imports

from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import psycopg2






class SQLHandle(object):
    '''
    Singleton class for handling SQL db connections.
    '''

    
    # Define a database name (we're using a dataset on births, so we'll call it birth_db)
    # Set your postgres username/password, and connection specifics
    username = 'postgres'
    password = 'password'     # change this
    host     = 'localhost'
    port     = '5432'            # default port that postgres listens on
    db_name  = 'book_info'


    con = None
    cursor = None



    def execute_postgresql_select(command):
        '''
        Executes a select command to the SQL database and returns the results.
        '''

        if SQLHandle.con == None:
            SQLHandle.connect_to_database()

        SQLHandle.cursor.execute(command)
        results = SQLHandle.cursor.fetchall()

        if len(results) == 0:
            results = None

        return results

    def connect_to_database():
        '''
        Lazy connect to database; only connect if asked to
        '''

        # Create the engine
        SQLHandle.engine = create_engine( 'postgresql://{}:{}@{}:{}/{}'.format(SQLHandle.username,\
         SQLHandle.password, SQLHandle.host, SQLHandle.port, SQLHandle.db_name) )

        # Create connection and cursor object to insert info into db
        SQLHandle.con = psycopg2.connect(database = SQLHandle.db_name,\
         user = SQLHandle.username, password = SQLHandle.password, host = SQLHandle.host)
        SQLHandle.cursor = SQLHandle.con.cursor()
