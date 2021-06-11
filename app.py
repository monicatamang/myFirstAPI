import dbconnect
import mariadb
from flask import Flask, request, Response
import json
import traceback

def close_db_and_cursor(conn, cursor):
    closing_cursor = dbconnect.close_cursor(cursor)
    closing_db = dbconnect.close_db_connection(conn)
    if(closing_cursor == False or closing_db == False):
        print("\nFailed to close cursor and database connection.")

def check_db_connection_and_cursor(conn, cursor):
    if(conn == None or cursor == None):
        print("An error has occured in the database.")
        dbconnect.close_cursor(cursor)
        dbconnect.close_db_connection(conn)
        return

app = Flask(__name__)

@app.get("/animals")
def get_animals_list():
    conn = dbconnect.open_db_connection()
    cursor = dbconnect.create_db_cursor(conn)
    animals_list = None

    check_db_connection_and_cursor(conn, cursor)

    try:
        cursor.execute("SELECT name, class, location, id FROM animal")
        animals_list = cursor.fetchall()
    except mariadb.OperationalError:
        print(f"\nOperational errors occured when retrieving the animals list from the database.\n")
        traceback.print_exc()
    except mariadb.ProgrammingError:
        print("\nInvalid SQL syntax.\n")
        traceback.print_exc()
    except mariadb.DatabaseError:
        print("\nError detected in the database and resulted in a connection failure.\n")
        traceback.print_exc()
    except:
        print("An error has occured.")
        traceback.print_exc()

    close_db_and_cursor(conn, cursor)

    if(animals_list != None):
        animals_list_json = json.dumps(animals_list, default=str)
        return Response(animals_list_json, mimetype="application/json", status=200)
    else:
        return Response("Failed to retrieve animals from database.", mimetype="text/plain", status=500)

@app.post("/animals")
def create_animal():
    try:
        animal_name = request.json['name']
        animal_class = request.json['class']
        animal_location = request.json['location']
    except TypeError:
        print("\nInvalid data being passed to the database.\n")
        traceback.print_exc()
    except ValueError:
        print("\nInvalid data being passed to the database.\n")
        traceback.print_exc()
    except:
        print("An error has occured.")
        traceback.print_exc()
        return Response("Invalid data was passed to the database.", mimetype="text/plain", status=400)

    conn = dbconnect.open_db_connection()
    cursor = dbconnect.create_db_cursor(conn)
    row_count = 0
    new_id = None

    check_db_connection_and_cursor(conn, cursor)

    try:
        cursor.execute("INSERT INTO animal(name, class, location) VALUES(?, ?, ?)", [animal_name, animal_class, animal_location])
        conn.commit()
        row_count = cursor.rowcount
        new_id = cursor.lastrowid
    except mariadb.IntegrityError:
        print(f"\nAnimal name is already taken. Please enter another username.\n")
        traceback.print_exc()
    except mariadb.OperationalError:
        print(f"\nAn operational error has occured when creating {animal_name} and storing {animal_name} in the database.\n")
        traceback.print_exc()
    except mariadb.ProgrammingError:
        print(f"\nInvalid SQL syntax.\n")
        traceback.print_exc()
    except mariadb.DatabaseError:
        print(f"\nAn error in the database has occured. Failed to create {animal_name} and store {animal_name} in the database.\n")
        traceback.print_exc()
    except:
        print("An error has occured.")
        traceback.print_exc()

    close_db_and_cursor(conn, cursor)

    if(row_count == 1 and new_id != None):
        new_animal = {
            'id': new_id,
            'name': animal_name,
            'class': animal_class,
            'location': animal_location
        }
        new_animal_json = json.dumps(new_animal, default=str)
        return Response(new_animal_json, mimetype="application/json", status=201)
    else:
        return Response("Failed to create a new animal.", mimetype="text/plain", status=500)


@app.patch("/animals")
def edit_animal():
    try:
        animal_id = request.json['id']
        animal_name = request.json['name']
    except TypeError:
        print("\nInvalid data being passed to the database.\n")
        traceback.print_exc()
    except ValueError:
        print("\nInvalid data being passed to the database.\n")
        traceback.print_exc()
    except:
        print("An error has occured.")
        traceback.print_exc()
        return Response("Invalid data was passed to the database.", mimetype="text/plain", status=400)

    conn = dbconnect.open_db_connection()
    cursor = dbconnect.create_db_cursor(conn)
    row_count = 0
    edit_animal = None

    check_db_connection_and_cursor(conn, cursor)

    try:
        cursor.execute("UPDATE animal SET name = ? WHERE id = ?", [animal_name, animal_id])
        conn.commit()
        row_count = cursor.rowcount
        
        cursor.execute("SELECT name, class, location, id FROM animal WHERE id = ?", [animal_id,])
        edit_animal = cursor.fetchall()
    except mariadb.IntegrityError:
        print(f"\nAnimal name is already taken. Please enter another username.\n")
        traceback.print_exc()
    except mariadb.OperationalError:
        print(f"\nAn operational error has occured when creating {animal_name} and storing {animal_name} in the database.\n")
        traceback.print_exc()
    except mariadb.ProgrammingError:
        print(f"\nInvalid SQL syntax.\n")
        traceback.print_exc()
    except mariadb.DatabaseError:
        print(f"\nAn error in the database has occured. Failed to create {animal_name} and store {animal_name} in the database.\n")
        traceback.print_exc()
    except:
        print("An error has occured.")
        traceback.print_exc()

    close_db_and_cursor(conn, cursor)

    if(row_count == 1 and edit_animal != None):
        edit_animal_json = json.dumps(edit_animal, default=str)
        return Response(edit_animal_json, mimetype="application/json", status=201)
    else:
        return Response("Failed to edit animal.", mimetype="text/plain", status=500)

@app.delete("/animals")
def delete_animal():
    try:
        animal_id = request.json['id']
    except TypeError:
        print("\nInvalid data being passed to the database.\n")
        traceback.print_exc()
    except ValueError:
        print("\nInvalid data being passed to the database.\n")
        traceback.print_exc()
    except:
        print("An error has occured.")
        traceback.print_exc()
        return Response("Invalid data was passed to the database.", mimetype="text/plain", status=400)

    conn = dbconnect.open_db_connection()
    cursor = dbconnect.create_db_cursor(conn)
    row_count = 0

    check_db_connection_and_cursor(conn, cursor)

    try:
        cursor.execute("DELETE FROM animal WHERE id = ?", [animal_id,])
        conn.commit()
        row_count = cursor.rowcount
    except mariadb.OperationalError:
        print(f"\nAn operational error has occured. Failed to delete animal in the database.\n")
        traceback.print_exc()
    except mariadb.ProgrammingError:
        print(f"\nInvalid SQL syntax.\n")
        traceback.print_exc()
    except mariadb.DatabaseError:
        print(f"\nAn error in the database has occured. Failed to delete animal in the database.\n")
        traceback.print_exc()
    except:
        print("An error has occured.")
        traceback.print_exc()

    close_db_and_cursor(conn, cursor)

    if(row_count == 1):
        return Response(f"Animal {animal_id} has been successfully deleted.", mimetype="application/json", status=200)
    else:
        return Response("Failed to delete animal.", mimetype="text/plain", status=500)

app.run(debug=True)