
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


comment_user_table = db.Table(
    "comment_user",
    db.Model.metadata,
    db.Column("comment_id", db.Integer, db.ForeignKey("comment.id")),
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"))
)
comment_journal_table = db.Table(
    "comment_journal",
    db.Model.metadata,
    db.Column("comment_id", db.Integer, db.ForeignKey("comment.id")),
    db.Column("journal_id", db.Integer, db.ForeignKey("journal.id"))
)

class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key = True)
    date = db.Column(db.String, nullable = False)
    comment = db.Column(db.String, nullable = False)
    user = db.relationship("User", secondary = comment_user_table, back_populates = "comments")
    journal = db.relationship("Journal", secondary = comment_journal_table, back_populates = "comments")

    def __init__(self, **kwargs):
        self.date = kwargs.get("date")
        self.comment = kwargs.get("comment")

    def serialize(self):
        return {
            "id": self.id,
            "date": self.date,
            "text": self.comment,
            "user": [u.sub_serialize() for u in self.user],
            "journal": [j.sub_serialize() for j in self.journal]
        }
    def sub_serialize(self):
        return {
            "id": self.id,
            "date": self.date,
            "text": self.comment
        }



class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String, nullable = False)
    anon_name = db.Column(db.String, nullable = False)
    journals = db.relationship("Journal", cascade = "delete")
    comments = db.relationship("Comment", secondary = comment_user_table, back_populates = "user")

    def __init__(self, **kwargs):
        self.username = kwargs.get("username")
        self.anon_name = kwargs.get("anon_name")

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "anonymous_name": self.anon_name,
            "comments": [c.sub_serialize() for c in self.comments],
            "journals": [j.sub_serialize() for j in self.journals]
        }

    def sub_serialize(self):
        return {
            "id": self.id,
            "anonymous name": self.anon_name
        }


class Journal(db.Model):
    __tablename__ = 'journal'
    id = db.Column(db.Integer, primary_key = True)
    date = db.Column(db.String, nullable = False)
    title = db.Column(db.String, nullable = False)
    entry = db.Column(db.String, nullable = False)
    public = db.Column(db.Boolean, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comments = db.relationship("Comment", secondary = comment_journal_table, back_populates = "journal")

    def __init__(self, **kwargs):
        self.user_id = kwargs.get("user_id")
        self.date = kwargs.get("date")
        self.title = kwargs.get("title")
        self.entry = kwargs.get("entry")
        self.public = kwargs.get("public")

    def serialize(self):
        return {
            "id": self.id,
            "date": self.date,
            "title": self.title,
            "entry": self.entry,
            "public": self.public,
            "comments": [c.sub_serialize() for c in self.comments]
        }
    def sub_serialize(self):
        return {
            "id": self.id,
            "date": self.date,
            "title": self.title,
            "entry": self.entry,
            "public": self.public
        }
