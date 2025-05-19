from google.cloud import firestore

DATABASE_ID = "second-try"  # TODO: Move to env file

def get_firestore_client():
    return firestore.Client(database=DATABASE_ID)
