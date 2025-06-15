from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exists 
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

db = SQLAlchemy()

class FavoriteRecipe(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.String, db.ForeignKey('user_id'), nullable = False)
