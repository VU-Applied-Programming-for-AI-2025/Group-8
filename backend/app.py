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
    user = userAuthHelper()
    if not user:
        return redirect(url_for("auth_page"))
    d = {}
    d['diet'] = ",".join(user.diet)
    d['allergies'] = ",".join(user.allergies)
    d['fullname'] = user.name
    print(d)
    return render_template("index.html", response=d)

@app.route("/recommendations")
def recommendations():
    """
    Provides categorized recipe recommendations for breakfast, lunch, and dinner.
    Falls back to random recipes if no results are found.
    """
    logged_in_user = userAuthHelper()
    if not logged_in_user:
        return redirect(url_for("auth_page"))
    diet = ",".join(logged_in_user.diet)
    intolerance = ",".join(logged_in_user.allergies)
    print(f"api key: {spoonacular_api_key}")

    print("Diet:", diet)
    print("Allergies:", intolerance)

    category_to_types = {
        "breakfast": ["breakfast"],
        "lunch": ["main course", "salad", "soup"],
        "dinner": ["main course", "side dish", "appetizer"]
    }

    meal_recipes = {}

    for category, types in category_to_types.items():
        collected_recipes = []

        for t in types:
            print(f"Fetching recipes for {category} ({t})...")
            response = requests.get(
                "https://api.spoonacular.com/recipes/complexSearch",
                params={
                    "diet": diet,
                    "excludeIngredients": intolerance,
                    "type": t,
                    "number": 3,
                    "apiKey": spoonacular_api_key
                }
            )
            print("URL:", response.url)
            print("Status:", response.status_code)
            print("Response:", response.text[:200])  # just preview the text

            try:
                data = response.json()
                collected_recipes.extend(data.get("results", []))
            except Exception as e:
                print(f"Error parsing {category} ({t}):", e)

        # fallback if no recipes found for this category
        if not collected_recipes:
            print(f"No recipes found for {category} with filters. Trying fallback.")
            fallback_response = requests.get(
                "https://api.spoonacular.com/recipes/random",
                params={
                    "number": 3,
                    "apiKey": spoonacular_api_key
                }
            )
            try:
                fallback_data = fallback_response.json()
                collected_recipes = fallback_data.get("recipes", [])
            except Exception as e:
                print(f"Fallback error for {category}:", e)
                collected_recipes = []

        # remove duplicates by ID
        unique = {r['id']: r for r in collected_recipes}
        meal_recipes[category] = list(unique.values())

    print(meal_recipes)

    return render_template("recipes.html", recipes_by_meal=meal_recipes)


    
    
@app.route('/save_favorite/<recipe_id>', methods = ['POST'])
def save_favorite(recipe_id):
    user = userAuthHelper()
    if not user:
        return redirect(url_for("auth_page"))
    recipe_id = int(recipe_id)
    
    if recipe_id in user.saved_recipes:
        return "already exist"
    
    user.saved_recipes.append(recipe_id)
    return "OK"
    
@app.route('/remove_favorite/<recipe_id>', methods = ['DELETE'])
def remove_favorite(recipe_id):
    user = userAuthHelper()
    if not user:
        return redirect(url_for("auth_page"))
    recipe_id = int(recipe_id)
    if recipe_id not in user.saved_recipes:
        return "not exist"
    
    if recipe_id in user.saved_recipes:
        user.saved_recipes.remove(recipe_id)
    
    return "OK" 

@app.route('/show_favorites', methods = ['GET'])
def show_favorites():
    user = userAuthHelper()
    if not user:
        return redirect(url_for("auth_page"))
    return jsonify(user.saved_recipes)

@app.route('/save_results', methods=['POST'])
def save_results():
    user = userAuthHelper()
    if not user:
        return redirect(url_for("auth_page"))
    
    CurrentResults = request.get_json(silent=True)
    if not CurrentResults:
        return "No result"
    user.analysis_results = CurrentResults
    
    return "OK"

@app.route('/result_visualization', methods=['POST'])
def result_visualization():
    user = userAuthHelper()
    if not user:
        return redirect(url_for("auth_page"))
    
    result = {}
    CurrentResult = user.analysis_results 
    
    for vitamin in CurrentResult:
        if CurrentResult[vitamin] < 40:
            result[vitamin] = "Low"
        elif CurrentResult[vitamin] < 70:
            result[vitamin] = "Medium"
        else:
            result[vitamin] = "High"
    
    return jsonify(result)

def userAuthHelper():
    if not session.get('logged_in'):
        return False
    logged_in_user = users_data.get_user(session['username'])
    if not logged_in_user:
        session['logged_in'] = False
        session['username'] = ""
        return False
    return logged_in_user

if __name__ == "__main__":
    app.run(debug=True)
