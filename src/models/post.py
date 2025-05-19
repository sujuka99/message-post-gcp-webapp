from datetime import datetime, timezone
from services.firestore_client import get_firestore_client

db = get_firestore_client()


class PostModel:
    collection_name = "posts"

    def __init__(self, author, subject, body):
        self.author = author
        self.subject = subject
        self.body = body
        self.creation_date = datetime.now(timezone.utc)
        self.change_date = self.creation_date

    def create(self):
        doc_ref = db.collection(PostModel.collection_name).document()
        data = {
            "change_date": self.change_date,
            "creation_date": self.creation_date,
            "author": self.author,
            "subject": self.subject,
            "body": self.body,
        }
        doc_ref.set(data)
        return doc_ref.get().to_dict() | {"id": doc_ref.id}

    @staticmethod
    def get(post_id):
        doc_ref = db.collection(PostModel.collection_name).document(post_id)
        doc = doc_ref.get()
        if not doc.exists:
            return None
        post = doc.to_dict()
        post["id"] = post_id
        return post

    @staticmethod
    def get_all():
        docs = db.collection(PostModel.collection_name).stream()
        return [{"id": doc.id, **doc.to_dict()} for doc in docs]

    @staticmethod
    def update(post_id, user_email, subject, body):
        doc_ref = db.collection(PostModel.collection_name).document(post_id)
        doc = doc_ref.get()
        if not doc.exists:
            return None, "Post not found"
        post = doc.to_dict()
        if post["author"] != user_email:
            return None, "Unauthorized"
        updated_data = {
            "subject": subject,
            "body": body,
            "change_date": datetime.now(timezone.utc),
        }
        doc_ref.update(updated_data)
        updated_post = doc_ref.get().to_dict()
        return updated_post | {"id": post_id}, None

    @staticmethod
    def to_dict(post_dict):
        # post_dict should be dict with keys including 'id', 'author', 'subject', 'body', 'creation_date', 'change_date'
        return {
            "id": post_dict.get("id"),
            "author": post_dict.get("author"),
            "subject": post_dict.get("subject"),
            "body": post_dict.get("body"),
            "created_at": post_dict.get("creation_date").isoformat(),
            "updated_at": post_dict.get("change_date").isoformat(),
        }
