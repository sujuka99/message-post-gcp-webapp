from google.cloud import firestore

DATABASE_ID = "second-try"  # TODO: Move to env file


def get_firestore_client():
    """Return a properly configured firestore client."""
    return firestore.Client(database=DATABASE_ID)
