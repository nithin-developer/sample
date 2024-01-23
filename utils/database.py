import sqlite3

class DatabaseManager:
    def __init__(self, db_file='app_database.db'):
        self.db_file = db_file
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()

    def create_tables(self):
        # Create necessary tables if they don't exist
        create_logs_table_query = '''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            token TEXT,
            tenant_id TEXT,
            secretToken TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        '''
        self.cursor.execute(create_logs_table_query)
        self.connection.commit()

    def insert_userdata(self, username, token, tenant_id, secretToken):
        insert_log_query = "INSERT INTO users (username, token, tenant_id, secretToken) VALUES (?, ?, ?, ?)"
        self.cursor.execute(insert_log_query, (username, token, tenant_id, secretToken))
        self.connection.commit()
        
    def get_userdata(self):
        get_log_query = "SELECT * FROM users"
        self.cursor.execute(get_log_query)
        return self.cursor.fetchall()
        
    def close_connection(self):
        # Close the database connection
        self.connection.close()
