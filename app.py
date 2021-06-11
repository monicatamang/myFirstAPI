import dbconnect
import mariadb
from flask import Flask, request, Response
import json
import re
import traceback

# Creating a function that searches for invalid characters in the animal's name
def check_invalid_chars(user_input):
    # Using the python's regular expression compile and search methods to find whether the user's data contains invalid characters for the animal name
    valid_chars = re.compile(r'[a-zA-Z]').search(user_input)
    # If the animal name contains only lowercase and uppercase letters, store it in the database
    if(valid_chars):
        return True
    # if the animal name is contains invalid characters such as numbers or special characters, don't store it in the database
    else:
        return False

# Creating a function that closes the database connection and the cursor
def close_db_connection_and_cursor(conn, cursor):
    # Closing the cursor and database connection
    closing_cursor = dbconnect.close_cursor(cursor)
    closing_db = dbconnect.close_db_connection(conn)
    # If the cursor or database connection failed to close, print an error message
    if(closing_cursor == False or closing_db == False):
        print("Failed to close cursor and database connection.")

# Checking to see if the database connection is opened and the cursor is created
def check_db_connection_and_cursor(conn, cursor):
    # If the connection was successful but the cursor was failed to be created, print an error message and attempt to close the cursor and database connection again
    if(conn == None or cursor == None):
        print("An error has occured in the database.")
        dbconnect.close_cursor(cursor)
        dbconnect.close_db_connection(conn)
        return

# Initializing the flask server
app = Flask(__name__)

# Creating a GET request to the "animals" endpoint to get the list of animals
@app.get("/animals")
def get_animals_list():
    # Opening the database and creating a cursor
    conn = dbconnect.open_db_connection()
    cursor = dbconnect.create_db_cursor(conn)

    # Initalizing the list of animals as a variable and assigning it a value of "None" so that it can still be referenced after the try-except block
    animals_list = None

    # Checking to see if the database connection is opened and whether the cursor is created
    check_db_connection_and_cursor(conn, cursor)

    # Creating a try-except block to catch errors when getting the list of animals from the database
    try:
        # Getting the all the animals from the database
        cursor.execute("SELECT name, id FROM animal")
        animals_list = cursor.fetchall()
    # Raising the OperationalError exception for things that are not in control of the programmer, printing an error message and the traceback
    except mariadb.OperationalError:
        print(f"An operational error has occured when retrieving the all the animals from the database.")
        traceback.print_exc()
    # Raising the ProgrammingError exception for errors made by the programmer, printing an error message and the traceback
    except mariadb.ProgrammingError:
        print("Invalid SQL syntax.")
        traceback.print_exc()
    # Raising the DatabaseError exception for errors related to the database, printing an error message and the traceback
    except mariadb.DatabaseError:
        print("Error detected in the database and resulted in a connection failure.")
        traceback.print_exc()
    # Raising a general exception to catch all other errors, printing a general error message and the traceback
    except:
        print("An error has occured.")
        traceback.print_exc()

    # Closing the cursor and database connection
    close_db_connection_and_cursor(conn, cursor)

    # If the list of animals was successfully retrieved from the database, convert the list of animals into JSON format and send a client success response
    if(animals_list != None):
        animals_list_json = json.dumps(animals_list, default=str)
        return Response(animals_list_json, mimetype="application/json", status=200)
    # If the list of animals was not retrieved from the database, send the user a server error response
    else:
        return Response("Failed to retrieve animals from database.", mimetype="text/plain", status=500)

# Creating a POST request to the "animals" endpoint to create an animal
@app.post("/animals")
def create_animal():
    # Creating a try-except block to catch errors when receiving the user's input
    try:
        # Converting the user's data as a string
        animal_name = str(request.json['name'])
        # Checking the validity of the animal name
        is_animal_name_valid = check_invalid_chars(animal_name)
        # If the user sent an invalid animal name, send the user a client error response
        if(is_animal_name_valid == False):
            return Response("Invalid animal name being passed to the database.", mimetype="text/plain", status=400) 
    # Raising the error exception if the regular expression library is unable to compile the data being passed to it
    except re.error:
        print("An error occured with processing the regular expression.")
        traceback.print_exc()
    # Raising the ValueError exception if the user sends an animal name that has a data type other than a string, printing an error message and the traceback
    except ValueError:
        print("Invalid animal name being passed to the database.")
        traceback.print_exc()
    # Raising a general exception to catch all other errors, printing a general error message and the traceback
    except:
        print("An error has occured.")
        traceback.print_exc()
        # Sending the user a client error response and stopping the function from running the next lines of code that interacts with the database
        return Response("Invalid animal name was passed to the database.", mimetype="text/plain", status=400)

    # If the user sends valid data, open the database connection and create a cursor
    conn = dbconnect.open_db_connection()
    cursor = dbconnect.create_db_cursor(conn)

    # Initializing the row count and id and assigning it a value so that it can still be referenced after the try-except block
    row_count = 0
    new_id = None

    # Checking to see if the database connection is opened and whether the cursor is created
    check_db_connection_and_cursor(conn, cursor)

    # Creating a try-except block to catch errors when inserting the user's data into the database
    try:
        # Inserting the user's data into the database and commiting the changes
        cursor.execute("INSERT INTO animal(name) VALUES(?)", [animal_name,])
        conn.commit()
        # Checking to see if the user's data was stored in the database and getting the id of new animal
        row_count = cursor.rowcount
        new_id = cursor.lastrowid
    # Raising an IntegrityError exception if the user sends an animal that already exists in the database, printing an error message and the traceback
    except mariadb.IntegrityError:
        print(f"Unique key constraint failure. The animal already exists in the database.")
        traceback.print_exc()
    # Raising the OperationalError exception for things that are not in control of the programmer, printing an error message and the traceback
    except mariadb.OperationalError:
        print(f"An operational error has occured when creating a new animal.")
        traceback.print_exc()
    # Raising the ProgrammingError exception for errors made by the programmer, printing an error message and the traceback
    except mariadb.ProgrammingError:
        print(f"Invalid SQL syntax.")
        traceback.print_exc()
    # Raising the DatabaseError exception for errors related to the database, printing an error message and the traceback
    except mariadb.DatabaseError:
        print(f"An error in the database has occured. Failed to create a new animal.")
        traceback.print_exc()
    # Raising a general exception to catch all other errors, printing a general error message and the traceback
    except:
        print("An error has occured.")
        traceback.print_exc()

    # Closing the cursor and database connection
    close_db_connection_and_cursor(conn, cursor)

    # If the user's data was stored in the database and an id was created for the new animal, send the user the new animal created in JSON format and a client success response
    if(row_count == 1 and new_id != None):
        new_animal = {
            'id': new_id,
            'name': animal_name
        }
        new_animal_json = json.dumps(new_animal, default=str)
        return Response(new_animal_json, mimetype="application/json", status=201)
    # If the database failed to store the user's animal, send the user a server error response
    else:
        return Response("Failed to create a new animal.", mimetype="text/plain", status=500)

# Creating a PATCH request to the "animals" endpoint to edit an animal
@app.patch("/animals")
def edit_animal():
    # Creating a try-except block to catch errors when receiving the user's data
    try:
        # Converting the id into an integer data type and converting the name into a string data type
        animal_id = int(request.json['id'])
        animal_name = str(request.json['name'])
        # Checking the validity of the animal name
        is_animal_name_valid = check_invalid_chars(animal_name)
        # If the user sent an invalid animal name, send the user a client error response
        if(is_animal_name_valid == False):
            return Response("Invalid animal name being passed to the database.", mimetype="text/plain", status=400)
    # Raising the error exception if the regular expression library is unable to compile the data being passed to it
    except re.error:
        print("An error occured with processing the regular expression.")
        traceback.print_exc()
    # Raising the ValueError exception if the user sends an invalid data type for the id and name, printing an error message and the traceback
    except ValueError:
        print("Invalid data was being passed to the database.")
        traceback.print_exc()
    # Raising a general exception to catch all other errors, printing a general error message and the traceback
    except:
        print("An error has occured.")
        traceback.print_exc()
        # Sending the user a client error response and stopping the function for running the next lines of code that interacts with the database
        return Response("Invalid data was being passed to the database.", mimetype="text/plain", status=400)

    # If the user sends valid data, open the database connection and create a cursor 
    conn = dbconnect.open_db_connection()
    cursor = dbconnect.create_db_cursor(conn)

    # Initializing the row count and assigning it a value so that it can still be referenced after the try-except block
    row_count = 0

    # Checking to see if the database connection is opened and whether the cursor is created
    check_db_connection_and_cursor(conn, cursor)

    # Creating a try-except block to catch errors when updating the data in the database
    try:
        # Editing the old animal with the new animal and committing the changes
        cursor.execute("UPDATE animal SET name = ? WHERE id = ?", [animal_name, animal_id])
        conn.commit()
        # Checking to see if the user's data was stored in the database
        row_count = cursor.rowcount
    # Raising the OperationalError exception for things that are not in control of the programmer, printing an error message and the traceback
    except mariadb.OperationalError:
        print(f"An operational error has occured when storing the edited animal in the database.")
        traceback.print_exc()
    # Raising the ProgrammingError exception for errors made by the programmer, printing an error message and the traceback
    except mariadb.ProgrammingError:
        print(f"Invalid SQL syntax.")
        traceback.print_exc()
    # Raising the DatabaseError exception for errors related to the database, printing an error message and the traceback
    except mariadb.DatabaseError:
        print(f"An error in the database has occured. Failed to stored edited animal in the database.")
        traceback.print_exc()
    # Raising a general exception to catch all other errors, printing a general error message and the traceback
    except:
        print("An error has occured.")
        traceback.print_exc()

    # Closing the cursor and database connection
    close_db_connection_and_cursor(conn, cursor)

    # If the edited animal was successfully stored into the database, send the user the edited animal in JSON format and a client success response
    if(row_count == 1):
        edit_animal = {
            'id': animal_id,
            'name': animal_name
        }
        edit_animal_json = json.dumps(edit_animal, default=str)
        return Response(edit_animal_json, mimetype="application/json", status=200)
    # If the database failed to store the edited animal, send the user a server error response
    else:
        return Response("Failed to edit animal.", mimetype="text/plain", status=500)

# Creating a DELETE request to the "animals" endpoint to delete an exisiting animal
@app.delete("/animals")
def delete_animal():
    # Creating a try-except block to catch error when receiving data from the user
    try:
        # Converting the id into an integer data type
        animal_id = int(request.json['id'])
    # Raising the ValueError exception if the user sends an id that has a data type other than an integer, printing an error message and the traceback
    except ValueError:
        print("\nInvalid data being passed to the database.\n")
        traceback.print_exc()
    # Raising a general exception to catch all other errors, printing a general error message and the traceback
    except:
        print("An error has occured.")
        traceback.print_exc()
        # Sending the user a client error response and stopping the function for running the next lines of code that interacts with the database
        return Response("Invalid data was passed to the database.", mimetype="text/plain", status=400)

    # If the user sends a valid id, open the database connection and create a cursor
    conn = dbconnect.open_db_connection()
    cursor = dbconnect.create_db_cursor(conn)

    # Initializing the row count and assigning it a value so that it can still be referenced after the try-except block
    row_count = 0

    # Checking to see if the database connection is opened and whether the cursor is created
    check_db_connection_and_cursor(conn, cursor)

    # Creating a try-except block to catch errors when deleting an animal from the database
    try:
        # Deleting an animal from the database and committing the changes
        cursor.execute("DELETE FROM animal WHERE id = ?", [animal_id,])
        conn.commit()
        # Checking to see if the user's data was stored in the database
        row_count = cursor.rowcount
    # Raising the OperationalError exception for things that are not in control of the programmer, printing an error message and the traceback
    except mariadb.OperationalError:
        print(f"\nAn operational error has occured. Failed to delete animal in the database.\n")
        traceback.print_exc()
    # Raising the ProgrammingError exception for errors made by the programmer, printing an error message and the traceback
    except mariadb.ProgrammingError:
        print(f"\nInvalid SQL syntax.\n")
        traceback.print_exc()
    # Raising the DatabaseError exception for errors related to the database, printing an error message and the traceback
    except mariadb.DatabaseError:
        print(f"\nAn error in the database has occured. Failed to delete animal in the database.\n")
        traceback.print_exc()
    # Raising a general exception to catch all other errors, printing a general error message and the traceback
    except:
        print("An error has occured.")
        traceback.print_exc()

    # Closing the cursor and database connection
    close_db_connection_and_cursor(conn, cursor)

    # If the database successfully deleted the animal, send a client success response
    if(row_count == 1):
        return Response(f"Animal {animal_id} was successfully deleted.", mimetype="application/json", status=200)
    # If the database failed to delete the animal, send a server error response
    else:
        return Response("Failed to delete animal.", mimetype="text/plain", status=500)

# Running the flask server with debug mode turned on
app.run(debug=True)