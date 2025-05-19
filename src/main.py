import firebase_admin
from firebase_admin import credentials
from flask import Flask, g, jsonify, request
from flask_cors import CORS

from models.comment import CommentModel
from models.post import PostModel
from tools.auth import firebase_auth_required

if not firebase_admin._apps:
    try:
        # Try local development credentials
        cred = credentials.Certificate(
            "/secrets/message-post-gcp-webapp-cea4b-firebase-adminsdk-fbsvc-fb07dbd631.json"
        )
        firebase_admin.initialize_app(cred)
    except Exception:
        # Fall back to default creds (App Engine)
        firebase_admin.initialize_app()

app = Flask(__name__)
CORS(app)


@app.route("/posts", methods=["POST"])
@firebase_auth_required
def create_post():
    user = g.user
    author_email = user.get("email")

    data = request.json or {}
    author = data.get("author")
    subject = data.get("subject")
    body = data.get("body")
    if not (author and subject and body):
        return jsonify({"error": "Missing fields"}), 400

    post = PostModel(author_email, subject, body)
    post_dict = post.create()  # returns dict with 'id' included
    return jsonify({"id": post_dict["id"]}), 201


@app.route("/posts", methods=["GET"])
def get_posts():
    posts = PostModel.get_all()  # list of dicts with 'id'
    # Format each post with to_dict for consistent output & iso timestamps
    formatted_posts = [PostModel.to_dict(post) for post in posts]
    return jsonify(formatted_posts), 200


@app.route("/posts/<post_id>", methods=["GET"])
def get_post(post_id):
    post = PostModel.get(post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404
    return jsonify(PostModel.to_dict(post)), 200


@app.route("/posts/<post_id>", methods=["PUT"])
@firebase_auth_required
def update_post(post_id):
    user = g.user
    user_email = user.get("email")

    data = request.json or {}
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
    data = request.json or {}
    author = data.get("author")
    body = data.get("body")
    if not author or not body:
        return jsonify({"error": "Missing author or body"}), 400

    comment = CommentModel(author, body)
    comment_id = comment.add_to_post(post_id)
    return jsonify({"comment_id": comment_id}), 201


@app.route("/posts/<post_id>/comments", methods=["GET"])
@firebase_auth_required
def get_comments(post_id):
    comments = CommentModel.get_for_post(post_id)
    return jsonify(comments), 200


if __name__ == "__main__":
    app.run(debug=True)
