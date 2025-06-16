from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Recipe(db.model):
    recipe_id = db.Column(db.Integer, primary_key=True)
    recipe_name = db.Column(db.String(255))
    recipe_description = db.Column(db.String(255))
