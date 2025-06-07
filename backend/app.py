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

SavingList: Dict[int, List[int]] = {} # key = user id, value = list of recipe id's

app = Flask(__name__)

@app.route('/savings/<user_idx>/<recipe_idx>', methods = ['POST'])
def add(user_idx, recipe_idx):
    user_id = int(user_idx)
    recipe_id = int(recipe_idx)
    if user_id not in SavingList:
        SavingList[user_id] = []
        
    if recipe_id in SavingList[user_id]:
        return "already exist"
    
    SavingList[user_id].append(recipe_id)
    return "OK"

@app.route('/savings/<user_idx>/<recipe_idx>', methods = ['DELETE'])
def remove(user_idx, recipe_idx):
    user_id = int(user_idx)
    recipe_id = int(recipe_idx)
    if user_id not in SavingList:
        SavingList[user_id] = []
    
    if recipe_id not in SavingList[user_id]:
        return "not exist"
    
    if recipe_id in SavingList[user_id]:
        SavingList[user_id].remove(recipe_id)
    
    return "OK" 

@app.route('/savings/<user_idx>', methods = ['GET'])
def recipe_list(user_idx):
    user_id = int(user_idx)
    if user_id not in SavingList:
        SavingList[user_id] = []
    
    SavedRecipes = []
    for recipe_id in SavingList[user_id]:
        recipe = RecipeList[recipe_id]
        SavedRecipes.append(recipe.toJSON())

    return jsonify(SavedRecipes)

if __name__ == "__main__":
    app.run(debug=True)