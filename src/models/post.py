from datetime import UTC, datetime

from services.firestore_client import get_firestore_client

db = get_firestore_client()

type Post = dict[str, str]


class PostModel:
    """Model of a post.

    Works with Firestore.

    :param author_email: Unique email address to be used as authentication for the author email.
    :param subject: The subject of the post.
    :param body: The body (text) of the post.
    """

    collection_name = "posts"

    def __init__(self, author_email: str, subject: str, body: str) -> None:
        self.author_email = author_email
        self.subject = subject
        self.body = body
        self.creation_date = datetime.now(UTC)
        self.change_date = self.creation_date

    def create(self) -> Post:
        """Create a post.

        ID generation is left to firestore.

        :return: A mapping containing all details relevant to the object.
        """
        doc_ref = db.collection(PostModel.collection_name).document()
        data = {
            "change_date": self.change_date,
            "creation_date": self.creation_date,
            "author_email": self.author_email,
            "subject": self.subject,
            "body": self.body,
        }
        doc_ref.set(data)
        return doc_ref.get().to_dict() | {"id": doc_ref.id}

    @staticmethod
    def get(post_id: str) -> Post | None:
        """Get a single post.

        :param post_id: ID of the post in firebase.
        :return: The requested post as a mapping.
        """
        doc_ref = db.collection(PostModel.collection_name).document(post_id)
        doc = doc_ref.get()
        if not doc.exists:
            return None
        post = doc.to_dict()
        post["id"] = post_id
        return post

    @staticmethod
    def get_all() -> list[Post]:
        """Retrieve all posts.

        :return: List of all existing posts.
        """
        docs = db.collection(PostModel.collection_name).stream()
        return [{"id": doc.id, **doc.to_dict()} for doc in docs]

    # TODO(Ivan Yordanov): Improve the returns and the function signature.
    @staticmethod
    def update(
        post_id: str, user_email: str, subject: str, body: str
    ) -> tuple[Post | None, str | None]:
        """Update a single post.

        :param post_id: ID of the post.
        :param user_email: User trying to edit the post.
        :param subject: New post subject.
        :param body: New post body.
        :return: The updated post if successful, else None.
        """
        doc_ref = db.collection(PostModel.collection_name).document(post_id)
        doc = doc_ref.get()
        if not doc.exists:
            return None, "Post not found"
        post = doc.to_dict()
        if post["author_email"] != user_email:
            return None, "Unauthorized"
        updated_data = {
            "subject": subject,
            "body": body,
            "change_date": datetime.now(UTC),
        }
        doc_ref.update(updated_data)
        updated_post = doc_ref.get().to_dict()
        return updated_post | {"id": post_id}, None

    # TODO(Ivan Yordanov): Is this needed at all? Test without it.
    @staticmethod
    def to_dict(post_dict):
        return {
            "id": post_dict.get("id"),
            "author_email": post_dict.get("author_email"),
            "subject": post_dict.get("subject"),
            "body": post_dict.get("body"),
            "created_at": post_dict.get("creation_date").isoformat(),
            "updated_at": post_dict.get("change_date").isoformat(),
        }
