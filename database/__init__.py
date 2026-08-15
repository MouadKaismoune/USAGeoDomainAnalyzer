from database.db_manager import DatabaseManager

db = DatabaseManager()

def init_database():
    db.create_tables()
    db.migrate()
    return db
