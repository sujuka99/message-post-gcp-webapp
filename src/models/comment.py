from datetime import UTC, datetime

from services.firestore_client import get_firestore_client

db = get_firestore_client()


class CommentModel:
    def __init__(self, author, body):
        self.author = author
        self.body = body
        self.creation_date = datetime.now(UTC)

    def add_to_post(self, post_id):
        post_ref = db.collection("posts").document(post_id)
        comment_data = {
            "author": self.author,
            "body": self.body,
            "creation_date": self.creation_date,
        }
        comment_ref = post_ref.collection("comments").document()
        comment_ref.set(comment_data)
        return comment_ref.id

    @staticmethod
    def get_for_post(post_id):
        post_ref = db.collection("posts").document(post_id)
        comments = post_ref.collection("comments").order_by("creation_date").stream()
        return [{"id": comment.id, **comment.to_dict()} for comment in comments]
