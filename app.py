import datetime
import os
import json
from db import db
from db import User
from db import Journal
from db import Comment
from flask import Flask
from flask import request

app = Flask(__name__)
db_filename = "diary.db"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)
with app.app_context():
    db.create_all()


# your routes here
def success_response(data, code=200):
    return json.dumps(data), code


def failure_response(message, code=404):
    return json.dumps({"error": message}), code


@app.route("/")
def hello_world():
    return "Anonymous Diary"

@app.route("/api/users/", methods=["POST"])
def create_user():
    body = json.loads(request.data)
    username= body.get("username")
    anon_name = body.get("anonymous_name")
    if username is None or anon_name is None:
        return failure_response("Name/anonymous name cannot be empty!",400)
    new_user = User(username= username, anon_name = anon_name)
    db.session.add(new_user)
    db.session.commit()
    return success_response(new_user.serialize(), 201)

@app.route("/api/users/<int:user_id>/")
def get_user(user_id):
    user = User.query.filter_by(id = user_id).first()
    if user is None:
        return failure_response("User not found!")
    return success_response(user.serialize())

@app.route("/api/users/<int:user_id>/", methods=["DELETE"])
def delete_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found!")
    db.session.delete(user)
    db.session.commit()
    return success_response(user.serialize())

@app.route("/api/journals/public/")
def get_journals_public():
    return success_response(
        {"journals": [j.serialize() for j in Journal.query.all() if j.public == True]}
    )

@app.route("/api/journals/private/")
def get_journals_private():
    return success_response(
        {"journals": [j.serialize() for j in Journal.query.all() if j.public == False]}
    )

@app.route("/api/journals/public/<int:journal_id>/")
def get_journal(journal_id):
    journal = Journal.query.filter_by(id=journal_id).first()
    if journal is None:
        return failure_response("Journal not found!", 400)
    if journal.public == True:
        return success_response(journal.serialize())
    else:
        return failure_response("Journal is private!", 400)

@app.route("/api/users/<int:user_id>/journal/<int:journal_id>/", methods=["POST"])
def create_comment(user_id, journal_id):
    journal = Journal.query.filter_by(id=journal_id).first()
    if journal is None:
        return failure_response("Journal not found!", 400)
    if journal.public == False:
        return failure_response("Journal is private!", 400)
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found!")

    body = json.loads(request.data)
    comment = body.get("comment")
    if comment is None:
        return failure_response("Empty comment not allowed!", 400)
    new_comment = Comment(
        date= datetime.date.today(),
        comment=comment
    )
    new_comment.user.append(user)
    new_comment.journal.append(journal)
    db.session.add(new_comment)
    db.session.commit()
    return success_response(new_comment.serialize(), 201)

@app.route("/api/users/<int:user_id>/journal/", methods=["POST"])
def create_journal(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found!")
    body = json.loads(request.data)
    title = body.get("title")
    entry = body.get("entry")
    public = body.get("public", False)
    if title is None or entry is None or public is None:
        return failure_response("Title/entry/public cannot be none!", 400)
    new_journal = Journal(
        user_id=user_id,
        date= datetime.date.today(),
        title=title,
        entry= entry,
        public = public
    )
    db.session.add(new_journal)
    db.session.commit()
    return success_response(new_journal.serialize(),201)






if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
