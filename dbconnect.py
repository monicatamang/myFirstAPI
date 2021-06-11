import dbcreds
import mariadb
import traceback

def open_db_connection():
    try:
        return mariadb.connect(user=dbcreds.user, password=dbcreds.password, host=dbcreds.host, port=dbcreds.port, database=dbcreds.database)
    except mariadb.OperationalError:
        print("\nOperational errors detected in the database connection.\n")
        traceback.print_exc()
    except mariadb.DatabaseError:
        print("\nError detected in the database and resulted in a connection failure.\n")
        traceback.print_exc()
    except:
        print("\nAn error has occured. Failed to connect to the database.\n")
        traceback.print_exc()
        return None

def create_db_cursor(conn):
    try:
        return conn.cursor()
    except mariadb.InternalError:
        print("\nInternal errors detected in the database. Failed to create a cursor.\n")
        traceback.print_exc()
    except mariadb.OperationalError:
        print("\nOperational errors detected in the database connection. Failed to create a cursor.\n")
        traceback.print_exc()
    except mariadb.DatabaseError:
        print("\nErrors detected in database. Failed to create a cursor.\n")
        traceback.print_exc()
    except:
        print("\nAn error has occured. Failed to create a cursor.\n")
        traceback.print_exc()
        return None

def close_cursor(cursor):
    if(cursor == None):
        return True
    try:
        cursor.close()
        return True
    except mariadb.InternalError:
        print("\nInternal errors detected in the database. Failed to create a cursor.\n")
        traceback.print_exc()
    except mariadb.OperationalError:
        print("\nOperational errors detected in the database connection. Failed to create a cursor.\n")
        traceback.print_exc()
    except mariadb.DatabaseError:
        print("\nErrors detected with the current connection. Failed to close cursor.\n")
        traceback.print_exc()
    except:
        print("An error has occured. Failed to close cursor.")
        traceback.print_exc()
        return False

def close_db_connection(conn):
    if(conn == None):
        return True
    try:
        conn.close()
        return True
    except mariadb.OperationalError:
        print("\nOptional errors detected in the database. Failed to close the connection.\n")
        traceback.print_exc()
    except mariadb.DatabaseError:
        print("Errored detected in the database. Failed to close the connection.")
        traceback.print_exc()
    except:
        print("An error has occured. Failed to close database connection.")
        traceback.print_exc()
        return False