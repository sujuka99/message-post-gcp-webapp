from flask import Flask, request, jsonify
from flask_cors import CORS
from models.post import PostModel
from models.comment import CommentModel
import firebase_admin
from firebase_admin import credentials, auth

# Initialize once
if not firebase_admin._apps:
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred)

app = Flask(__name__)
CORS(app)

@app.route("/posts", methods=["POST"])
def create_post():
    data = request.json or {}
    author = data.get("author")
    subject = data.get("subject")
    body = data.get("body")
    if not (author and subject and body):
        return jsonify({"error": "Missing fields"}), 400

    post = PostModel(author, subject, body)
    post_dict = post.create()  # returns dict with 'id' included
    return jsonify({"id": post_dict["id"]}), 201

@app.route("/posts", methods=["GET"])
def get_posts():
    posts = PostModel.get_all()  # list of dicts with 'id'
    # Format each post with to_dict for consistent output & iso timestamps
    formatted_posts = [PostModel.to_dict(post) for post in posts]
    return jsonify(formatted_posts), 200

@app.route('/posts/<post_id>', methods=['GET'])
def get_post(post_id):
    post = PostModel.get(post_id)
    if not post:
        return jsonify({'error': 'Post not found'}), 404
    return jsonify(PostModel.to_dict(post)), 200

@app.route('/posts/<post_id>', methods=['PUT'])
def update_post(post_id):
    data = request.json or {}
    user_email = data.get('author')
    subject = data.get('subject')
    body = data.get('body')
    if not (user_email and subject and body):
        return jsonify({"error": "Missing fields"}), 400

    updated_post, error = PostModel.update(post_id, user_email, subject, body)
    if error:
        status_code = 403 if error == 'Unauthorized' else 404
        return jsonify({'error': error}), status_code

    return jsonify({'message': 'Post updated successfully', 'post': PostModel.to_dict(updated_post)}), 200

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
def get_comments(post_id):
    comments = CommentModel.get_for_post(post_id)
    return jsonify(comments), 200

if __name__ == "__main__":
    app.run(debug=True)
