## develop your flask app here ##
from typing import Dict, List
from flask import Flask, jsonify
from recipe import Recipe
from user import User

UserList: Dict[int, User] = {} # key = user id, value = user object
UserList[1] = User(1, 21, "Sevval")
UserList[2] = User(2, 44, "Feyza")
UserList[3] = User(3, 34, "Omer")
UserList[4] = User(4, 88, "Mustafa")
RecipeList: Dict[int, Recipe] = {}
RecipeList[101] = Recipe(101, "Sarma")
RecipeList[102] = Recipe(102, "Kebap")
RecipeList[103] = Recipe(103, "Corba")

app = Flask(__name__)

@app.route('/savings/<user_idx>/<recipe_idx>', methods = ['POST'])
def add(user_idx, recipe_idx):
    
    return "OK"

@app.route('/savings/<user_idx>/<recipe_idx>', methods = ['DELETE'])
def remove(user_idx, recipe_idx):
    return "OK" 

@app.route('/savings/<user_idx>', methods = ['GET'])
def recipe_list(user_idx):
    return jsonify([])

if __name__ == "__main__":
    app.run(debug=True)