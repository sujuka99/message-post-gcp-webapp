# Simple App Engine App

## Random troubleshooting

- Login: `gcloud auth login`
- Select project: `gcloud config set project message-post-gcp-webapp`
- Create a Firestore (native mode) database in the project. CHOOSE THE REGION WISELY
- App runs locally with `flask --app src.main run`
- Create app engine `gcloud app create --project=message-post-gcp-webapp`. CHOOSE SAME REGION AS FIRESTORE
- Perhaps App Engine account doesn't have the right permissions. Go to https://console.cloud.google.com/iam-admin/iam?project=message-post-gcp-webapp and make `message-post-gcp-webapp@appspot.gserviceaccount.com` a `Storage Admin`
- deploy with `gcloud app deploy src/app.yaml`
- see logs with `gcloud app logs tail -s default`


## Test backend

#### Start app

`PYTHONPATH=$(pwd)/src flask --app src.main run`

#### Create sample post

```
curl -X POST "http://127.0.0.1:5000/posts" \
  -H "Content-Type: application/json" \
  -d '{
        "author_email": "testuser@example.com",
        "subject": "Hello World",
        "body": "This is a test post."
      }'
```

#### Get all posts

```
curl -X GET "http://127.0.0.1:5000/posts"
```

#### Update post

```
curl -X PUT "http://127.0.0.1:5000/posts/<post_id>" \
  -H "Content-Type: application/json" \
  -d '{
        "author_email": "testuser@example.com",
        "subject": "Updated Subject",
        "body": "This is an updated test post."
      }'
```

#### Add coment

```
curl -X POST "http://127.0.0.1:5000/posts/<post_id>/comments" \
  -H "Content-Type: application/json" \
  -d '{
        "author_email": "commenter@example.com",
        "body": "This is a test comment."
      }'
```

#### Get comments

```
curl -X GET "http://127.0.0.1:5000/posts/<post_id>/comments"
```
