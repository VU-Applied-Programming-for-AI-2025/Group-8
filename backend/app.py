## develop your flask app here ##
from typing import Dict, List
from flask import Flask, jsonify

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