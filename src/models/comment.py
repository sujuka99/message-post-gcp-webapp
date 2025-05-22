from datetime import UTC, datetime

from models.post import PostModel
from services.firestore_client import get_firestore_client

db = get_firestore_client()

type Comment = dict[str, str]


class CommentModel:
    """Model of a comment to be used in Firestore.

    "param author_email: Author of the comment
    """

    collection_name = "comments"

    def __init__(self, author_email: str, body: str) -> None:
        self.author = author_email
        self.body = body
        self.creation_date = datetime.now(UTC)

    def add_to_post(self, post_id) -> str:
        """Create comment and assign to post.

        :param post_id: ID of the post to comment on.
        :return: ID of the created comment.
        """
        post_ref = db.collection(PostModel.collection_name).document(post_id)
        comment_data = {
            "author_email": self.author,
            "body": self.body,
            "creation_date": self.creation_date,
        }
        comment_ref = post_ref.collection(CommentModel.collection_name).document()
        comment_ref.set(comment_data)
        return comment_ref.id

    @staticmethod
    def get_for_post(post_id) -> list[Comment]:
        """Retrieve all comments for a specific post.

        :param post_id: ID of the post.
        :return: List containing all requested comments.
        """
        post_ref = db.collection(PostModel.collection_name).document(post_id)
        comments = (
            post_ref.collection(CommentModel.collection_name)
            .order_by("creation_date")
            .stream()
        )
        return [{"id": comment.id, **comment.to_dict()} for comment in comments]
