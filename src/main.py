from flask import Flask, jsonify, request
from flask_cors import CORS

from models.comment import CommentModel
from models.post import PostModel

app = Flask(__name__)
CORS(app)


@app.route("/posts", methods=["POST"])
def create_post():
    """Create post.

    :return: Result in json format and a status code
    """
    data = request.json or {}
    author = data.get("author_email")
    subject = data.get("subject")
    body = data.get("body")
    if not (author and subject and body):
        return jsonify({"error": "Missing fields"}), 400

    post = PostModel(author, subject, body)
    post_dict = post.create()  # returns dict with 'id' included
    return jsonify({"id": post_dict["id"]}), 201


@app.route("/posts", methods=["GET"])
def get_posts():
    """Get all posts.

    :return: Posts as json and status code.
    """
    posts = PostModel.get_all()  # list of dicts with 'id'
    # Format each post with to_dict for consistent output & iso timestamps
    formatted_posts = [PostModel.to_dict(post) for post in posts]
    return jsonify(formatted_posts), 200


@app.route("/posts/<post_id>", methods=["GET"])
def get_post(post_id):
    """Get specific post.

    :param post_id: ID of the desired post.
    :return: Post as json and status code.
    """
    post = PostModel.get(post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404
    return jsonify(PostModel.to_dict(post)), 200


@app.route("/posts/<post_id>", methods=["PUT"])
def update_post(post_id):
    """Update specified post.

    :param post_id: ID of the post to be modified.
    :return: Result in json form and status code.
    """
    data = request.json or {}
    user_email = data.get("author_email")
    subject = data.get("subject")
    body = data.get("body")
    if not (user_email and subject and body):
        return jsonify({"error": "Missing fields"}), 400

    updated_post, error = PostModel.update(post_id, user_email, subject, body)
    if error:
        status_code = 403 if error == "Unauthorized" else 404
        return jsonify({"error": error}), status_code

    return jsonify(
        {
            "message": "Post updated successfully",
            "post": PostModel.to_dict(updated_post),
        }
    ), 200


@app.route("/posts/<post_id>/comments", methods=["POST"])
def add_comment(post_id):
    """Upload a comment to a post.

    :param post_id: ID of the post to comment on.
    :return: ID of the comment and status code.
    """
    data = request.json or {}
    author = data.get("author_email")
    body = data.get("body")
    if not author or not body:
        return jsonify({"error": "Missing author or body"}), 400

    comment = CommentModel(author, body)
    comment_id = comment.add_to_post(post_id)
    return jsonify({"comment_id": comment_id}), 201


@app.route("/posts/<post_id>/comments", methods=["GET"])
def get_comments(post_id):
    """Retrieve all comments for a specified post.

    :param post_id: Post to get the coments from.
    :return: List of all comments in json format and a status code.
    """
    comments = CommentModel.get_for_post(post_id)
    return jsonify(comments), 200


if __name__ == "__main__":
    app.run(debug=True)
