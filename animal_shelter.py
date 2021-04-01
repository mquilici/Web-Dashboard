# Python module that implements CRUD operations in MongoDB.

from pymongo import cursor
from pymongo import MongoClient
from bson.json_util import dumps


class AnimalShelter(object):
    """ CRUD operations for Animal collection in MongoDB """

    # Initialize AnimalShelter object
    def __init__(self, userval: str, passval: str) -> None:
        # Initializing the MongoClient. This helps to
        # access the MongoDB databases and collections.
        # Note, the authentication code provided to students does not work:
        # self.client = MongoClient('mongodb://%s:%s@localhost:27017' % (userval, passval))
        # Instead, use the following to authenticate:
        self.client = MongoClient('mongodb://localhost:27017', username=userval, password=passval)
        # Use the AAC database
        self.database = self.client['AAC']

    # Complete this create method to implement the C in CRUD.
    # Input -> key/value pairs in the data type acceptable to the MongoDB driver insert API call.
    # Return -> “True” if successful insert, else “False.”
    # Note in order to return False, an except block is needed to catch exceptions and return false,
    # otherwise the program will end without returning.
    def create(self, data: dict) -> bool:
        """ Insert a document into the AAC database """
        if data is not None and type(data) is dict:   # data should be dictionary
            try:
                self.database.animals.insert(data)                       # call insert method
                return True                                              # if successful, return true
            except Exception as e:                                       # catch exceptions
                print("An exception occurred ::", e)                     # print exception
                return False                                             # if unsuccessful, return false
        else:
            raise Exception("Nothing to save, because data parameter is empty")   # Raise exception with improper input

    # Create method to implement the R in CRUD.
    # Input -> key/value lookup pair to use with the MongoDB driver find API call.
    # Return -> result in cursor if successful, else MongoDB returned error message.
    def read(self, query: dict) -> cursor.Cursor:
        """ Query a result from the AAC database """
        if query is not None and type(query) is dict:                    # data should be dictionary
            return self.database.animals.find(query, {'_id': 0})         # call find method and return results, omit id
        else:
            raise Exception("Read error: invalid query parameter")       # Raise exception with improper input

    # Update method to implement the U in CRUD.
    # Input -> key/value lookup pair to find and key/value pairs to insert.
    # Return -> result in JSON format if successful, else MongoDB returned error message.
    def update(self, query: dict, changes: dict) -> str:
        """ Update a document in the AAC database """
        if (query is not None and type(query) is dict) and (changes is not None and type(changes) is dict):
            updated = self.database.animals.update_many(query, changes)  # call update_many method
            return dumps(updated.raw_result)                             # return raw_result in JSON format
        else:
            raise Exception("Update error: invalid update parameters")   # Raise exception with improper input

    # Delete method to implement the D in CRUD.
    # Input -> key/value lookup pair to delete
    # Return -> result in JSON format if successful, else MongoDB returned error message.
    def delete(self, remove: dict) -> str:
        """ Delete a document from the AAC database """
        if remove is not None and type(remove) is dict:                  # data should be dictionary
            deleted = self.database.animals.delete_many(remove)          # call delete_many method
            return dumps(deleted.raw_result)                             # return raw_result in JSON format
        else:
            raise Exception("Delete error: invalid delete parameter")    # Raise exception with improper input
