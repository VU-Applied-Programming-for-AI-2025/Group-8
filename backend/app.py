## develop your flask app here ##

from typing import Dict, List
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from user_data.user_profile import UserProfile, UsersData
import requests
import os
import json

app = Flask(
    __name__,
    template_folder="../frontend/templates", 
)
app.secret_key = "VerySupersecretKey"  # A secret key for the sessions.
spoonacular_api_key = os.getenv("API_KEY") # create an account in spoonacular.com, get api key, put in .env, and run "pip install python-dotenv"

users_data = UsersData() # Initializes the UsersData object where all the user profiles will be stored.

# Consent form page
@app.route('/')
def show_consent():
    """
    Checks if the consent form should be given (when the user has not given consent yet). Redirects to the consent form page.
    Redirects to the authentication page if the user has already given consent.
    """
    if not session.get('consent_given'):
        return render_template('consentform.html')
    return redirect(url_for("auth_page"))


@app.route('/consentform', methods=['POST'])
def handle_consent():
    """
    Checks if the user has given consent to redirect to auth page.
    """
    accepted = request.form.get("accept", "false")

    if accepted.lower() == "true":
        session['consent_given'] = True
        return redirect(url_for("auth_page"))
    else:
        session['consent_given'] = False


# Authentication page
@app.route("/auth", methods=['GET', 'POST'])
def auth_page():
    """
    Makes sure that the authentication page is only accassible if consent has been given, otherwise redirects to the consent form.
    If the user is logged in already, they will be redirected to the home page.
    If the user has not ben logged in yet, it will be redirected to the /auth/register page.
    """
    if session.get('consent_given') and not session.get('logged_in'):
        return render_template("auth.html")
    
    if not session.get('consent_given'):
        return redirect(url_for("show_consent"))
    
    if session.get('logged_in'):
        return redirect(url_for("home"))

@app.route("/auth/register", methods=["GET", "POST"])
def register():
    """
    Handles the registration for a new user profile. 
    If the user is already logged in, redirects to the home page.
    Processes the registration form and adds a new user profile.
    If the registration is successful, redirects to the home page. 
    If the registration fails because of an existing username, it shows an error message on the registration page.
    """
    if session.get('logged_in'):
        return redirect(url_for("home"))
    
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        name = request.form.get("name")
        age = request.form.get("age")
        sex = request.form.get("sex")
        hight = request.form.get("hight")
        weight = request.form.get("weight")
        skin_color = request.form.get("skin_color")
        country = request.form.get("country")
        medication = request.form.get("medication", "").split(",")
        diet = request.form.get("diet", "").split(",")
        existing_conditions = request.form.get("existing_conditions", "").split(",")
        allergies = request.form.get("allergies", "").split(",")
        
        try: 
            user_profile = UserProfile(username, password, name, age, sex, hight, weight, skin_color, country, medication, diet, existing_conditions, allergies)
            users_data.add_user(user_profile)
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for("home"))
        except ValueError as e:
            return render_template("auth.html", error=str(e))
    
    return render_template("registration.html")

@app.route("/auth/login", methods=["POST"])
def login():
    """
    Handles the login form submission.
    If the username and password is authenticated, then the user will be redirected to the homepage.
    If the authentication fails, it will show an error message (that the username is not found in the database)
    """
    if request.method == "POST":
        username = request.form.get("name")
        password = request.form.get("password")
        authenticated, message = users_data.user_authentication(username, password)
        if authenticated:
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for("home"))
        else:
            return render_template("auth.html", error=message)


@app.route("/home")
def home():
    if not session.get('logged_in'):
        return redirect(url_for("auth_page"))
    user = users_data.get_user(session['username'])
    d = {}
    d['diet'] = ",".join(user.diet)
    d['allergies'] = ",".join(user.allergies)
    d['fullname'] = user.name
    print(d)
    return render_template("index.html", response=d)

@app.route("/recommendations")
def recommendations():
    """
    Handles the recommendations request.
    If the user is logged in, then returns foods and recipes matching the user's conditions.
    If the user is not logged in, then it will show an error message (that the username is not found in database)
    """
    if session['logged_in']:
        logged_in_user = users_data.get_user(session['username'])
        diet = ",".join(logged_in_user.diet)
        intolerance = ",".join(logged_in_user.allergies)
        response = requests.get("https://api.spoonacular.com/recipes/complexSearch?diet=" + diet \
                    + "&excludeIngredients=" + intolerance \
                    + "&apiKey=" + spoonacular_api_key)
        recipes_matching_diet = json.loads(response.text)
        print(recipes_matching_diet['results'])
        return render_template("recipes.html", response=recipes_matching_diet['results']) if recipes_matching_diet != [] \
            else render_template("recipes.html", response="")
    else:
        return redirect(url_for("/auth/login"))
    
    
@app.route('/save_favorite/<recipe_id>', methods = ['POST'])
def save_favorite(recipe_id):
    if not session.get('logged_in'):
        return redirect(url_for("auth_page"))
    
    user = users_data.get_user(session['username'])
    recipe_id = int(recipe_id)
    
    if recipe_id in user.saved_recipes:
        return "already exist"
    
    user.saved_recipes.append(recipe_id)
    return "OK"
    
@app.route('/remove_favorite/<recipe_id>', methods = ['DELETE'])
def remove_favorite(recipe_id):
    if not session.get('logged_in'):
        return redirect(url_for("auth_page"))
    
    user = users_data.get_user(session['username'])
    recipe_id = int(recipe_id)
    if recipe_id not in user.saved_recipes:
        return "not exist"
    
    if recipe_id in user.saved_recipes:
        user.saved_recipes.remove(recipe_id)
    
    return "OK" 

@app.route('/show_favorites', methods = ['GET'])
def show_favorites():
    if not session.get('logged_in'):
        return redirect(url_for("auth_page"))
    
    user = users_data.get_user(session['username'])
    return jsonify(user.saved_recipes)

@app.route('/save_results', methods=['POST'])
def save_results():
    if not session.get('logged_in'):
        return redirect(url_for("auth_page"))
    
    user = users_data.get_user(session['username'])
    
    CurrentResults = request.get_json(silent=True)
    if not CurrentResults:
        return "No result"
    user.analysis_results = CurrentResults
    
    return "OK"

if __name__ == "__main__":
    app.run(debug=True)