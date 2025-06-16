## develop your flask app here ##
from flask import Flask, render_template, url_for, request, redirect, session, jsonify
from typing import Dict, List
from dotenv import load_dotenv
import os, json, requests, random
from groq import Groq
from user_data.user_profile import UserProfile, UsersData
<<<<<<< HEAD
=======
import random
import requests
>>>>>>> Feruza

load_dotenv()

app = Flask(
    __name__,
    template_folder="../frontend/templates"
    )
app.secret_key = "VerySupersecretKey"  # A secret key for the sessions.
spoonacular_api_key = os.getenv("API_KEY") # create an account in spoonacular.com, get api key, put in .env, and run "pip install python-dotenv"
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
users_data = UsersData() # Initializes the UsersData object where all the user profiles will be stored in a json file.

# Consent form page
@app.route('/')
def show_consent():
    """
    Checks if the consent form is shown when the user has not given consent yet.
    Redirects to the authentication page if the user has already given consent.
    """
    if not session.get('consent_given'):
        return render_template('consentform.html')
    return redirect(url_for("auth_page"))


@app.route('/consentform', methods=['POST'])
def handle_consent():
    """
    This page shows a consentform. Once accepted it will redirect to the authentication page. 
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
    Shows the authentication page where users can log in or choose to register if consent has been given, otherwise redirects to the consent form.
    If the user is logged in already, they will be redirected to the home page.
    If the user has not ben logged in yet, they will be redirected to the /auth/register page.
    """
    if session.get('consent_given') and not session.get('logged_in'):
        return render_template("auth.html")
    
    if not session.get('consent_given'):
        return redirect(url_for("handle_consent"))
    
    if session.get('logged_in'):
        return redirect(url_for("home"))

@app.route("/auth/register", methods=["GET", "POST"])
def register():
    """
    Handles the registration for a new user profile. 
    Processes the registration form and adds a new user profile.
    If the registration is successful, redirects to the home page. 
    If the registration fails because of an existing username, it shows an error message on the registration page.
    """
    if session.get('logged_in'):
        return redirect(url_for("home"))
    
    # Collecting user data from the registration form
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
        diet = request.form.get("diet")
        existing_conditions = request.form.get("existing_conditions", "").split(",")
        allergies = request.form.get("allergies", "").split(",")
        
        # Makes a user profile object and adds it to the users_data object
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
    If the authentication fails, it will show the corresponding error message on the authentication page.
    """
    # Retrieves the username and password from the login form
    if request.method == "POST":
        username = request.form.get("name")
        password = request.form.get("password")
        # Checks if the username and password corresponds to a user profile in the users_data object
        authenticated, message = users_data.user_authentication(username, password)
        if authenticated:
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for("home"))
        else:
            return render_template("auth.html", error=message)


@app.route("/home", methods = ["GET", "POST"])
def home():
    """
    This function displays the homepage.
    Users can generate a mealplan, submit their symtoms for a more custom mealplan and analyze their symptoms.
    """
    # Checks if user is logged in, if not redirects to the authentication page.
    user = userAuthHelper()
    if not user:
        return redirect(url_for("auth_page"))
    
    d = {}
    d['diet'] = user.diet
    d['allergies'] = ",".join(user.allergies)
    d['fullname'] = user.name
    print(d)

    if request.method == "POST":
        symptoms = request.form.get("symptoms").strip()
        if symptoms:
            return redirect(url_for("display_results", symptoms = symptoms))
        return redirect(url_for("home_page"))
    
    return render_template("homepage.html", response=d)

#function to analyze symptoms 
def analyze_symptoms():
    """
    This function sends the inputted symptoms to the groq api to analyze(, then returns it as text on the /results page.)
    """
    symptoms = request.args.get("symptoms")
    
    ai_prompt = f"""
        user symptoms: {symptoms}

        required analysis:
        1. top 3 likely vitamin/mineral deficiencies for each symptom
        2. for each deficiency:
        - biological explanation (short but detailed, easy to grasp. don't use the word "deficiency", in stead use something like "lack of")
        - foods to eat to fix the issue (comma-seperated list, no extra information, list each food on its own)
        - 1 lifestyle tip
        3. flag any urgent medical concerns

        return the analysis only in this format:
        [deficiency name]:
        - Why: [explanation]
        - Foods: [comma-separated list]
        - Tip: [actionable advice]

        [Urgency Note]: (if applicable)
        """
    
    # llm should incorporate the pesonal details of the user like allergies, pregnancy, etc 
    
    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "user",
                "content": ai_prompt,
            }
        ],
        temperature=0.7,
        max_completion_tokens=1024,
        top_p=1,
        stop=None
    )
    analysis_results = response.choices[0].message.content 
    return analysis_results

#results page to display analysis results
@app.route("/results")
def display_results():
    """
    This function displays the groq llm analysis on the webpage.
    """
    analysis = analyze_symptoms()
    symptoms = request.args.get("symptoms")

    return render_template("results.html", symptoms = symptoms, analysis = analysis)

#helper to function extract foods from the groq response
def extract_food_recs():
    """
    This function extracts the food recommendations from the llm response and stores it in a list for backend use.

    Call this function to extract a list with foods to eat from the groq llm response.
    """
    groq_response = analyze_symptoms()
    list_foods = []

    for line in groq_response.split("\n"):
        line = line.strip()
        if line.startswith('- Foods:'):
            all_foods = line[8:].split(',')
            foods = [food.strip() for food in all_foods]
            list_foods.extend(foods)

    seen_foods = set() #to check duplicates
    food_recs = [] #new list w/o duplicates
    for food in list_foods:
        if not (food in seen_foods or seen_foods.add(food)):
            food_recs.append(food)
    
    return food_recs

@app.route("/recommendations")
def recommendations():
    """
    Provides categorized recipe recommendations for breakfast, lunch, and dinner.
    Falls back to random recipes if no results are found.
    """
    # Checks if user is logged in, if not redirects to the authentication page.
    logged_in_user = userAuthHelper()
    if not logged_in_user:
        return redirect(url_for("auth_page"))
    
    diet = ",".join(logged_in_user.diet)
    intolerance = ",".join(logged_in_user.allergies)
    print(f"api key: {spoonacular_api_key}")

    print("Diet:", diet)
    print("Allergies:", intolerance)

    recommended_foods = extract_food_recs()
    print("Recommended foods: ", recommended_foods)

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
            
            params={
                    "diet": diet,
                    "excludeIngredients": intolerance,
                    "type": t,
                    "number": 3,
                    "apiKey": spoonacular_api_key
                }
            if recommended_foods:
                params["includeIngredients"] = ",".join(recommended_foods)

            response = requests.get(
                "https://api.spoonacular.com/recipes/complexSearch", params = params
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

#display recipe details
@app.route("/recipe/<recipe_id>")
def recipe_details(recipe_id):
    response = requests.get(
        f"https://api.spoonacular.com/recipes/{recipe_id}/information",
        params = {
            "apiKey": spoonacular_api_key,
            "includeNutrition": True    
            }
        )
    recipe_info = response.json()
    return render_template("recipe_details.html", recipe = recipe_info)

# Meal planner creation page
@app.route("/recommendations/mealplanner/select", methods=["GET", "POST"])
def choose_meal_planner():
    if request.method == "POST":
        selected = request.form.get("type")
        if selected == "auto":
            return redirect(url_for("spoonacular_builtin_mealplanner"))
        elif selected == "custom":
            return redirect(url_for("meal_planner"))
    return render_template("select_meal_plan_type.html")


@app.route("/recommendations/mealplanner/spoonacular", methods=["GET", "POST"])
def spoonacular_builtin_mealplanner():
<<<<<<< HEAD
    # Checks if user is logged in, if not redirects to the authentication page.
=======
>>>>>>> Feruza
    user = userAuthHelper()
    if not user:
        return redirect(url_for("auth_page"))

    if request.method == "POST":
        time_frame = request.form.get("timeFrame", "day")
        calories = request.form.get("calories")

        params = {
            "apiKey": spoonacular_api_key,
            "timeFrame": time_frame,
            "diet": user.diet,
            "exclude": ",".join(user.allergies)
        }
        if calories:
            params["targetCalories"] = calories

        response = requests.get("https://api.spoonacular.com/mealplanner/generate", params=params)
        if response.status_code == 200:
            user.mealplan = response.json()
            print("spoonacular response mealplan")
            print(user.mealplan)
            users_data.save_to_file()
            return redirect(url_for("edit_meal_planner"))
        else:
            return render_template("builtin_meal_planner.html", error="Failed to fetch meal plan.")

    return render_template("builtin_meal_planner.html")

def get_meal_plan(api_key, diet=None, exclude=None, calories=None, time_frame="day"):
    url = "https://api.spoonacular.com/mealplanner/generate"
    params = {
        "apiKey": api_key,
        "timeFrame": time_frame,
    }
    if diet:
        params["diet"] = diet
    if exclude:
        params["exclude"] = exclude
    if calories:
        params["targetCalories"] = calories

    response = requests.get(url, params=params)
    return response.json()


@app.route("/recommendations/mealplanner/create", methods=["GET", "POST"])
def meal_planner():
    if request.method == "POST":
        time_frame = request.form.get("timeFrame", "day")  # "day" or "week"
        calories = request.form.get("calories")

        user = userAuthHelper()
        if not user:
            return redirect(url_for("auth_page"))

        meal_plan = {}
        meal_plan['meals'] = []
        meal_plan['nutrients'] = {
            'calories': 0,
            'protein': 0,
            'fat': 0,
            'carbohydrates': 0
        }
        nutrients_to_check = set(['calories', 'protein', 'fat'])
        selected_meals = request.form.getlist("meals")
        print("selected_meals")
        print(selected_meals)
        for id in selected_meals:
            print(f"id = {id}")
            response = requests.get(
                f"https://api.spoonacular.com/recipes/{id}/information",
                    params = {
                        "apiKey": spoonacular_api_key,
                        "includeNutrition": True
                    }
                )
            recipe_info = response.json()
            print('recipe_info')
            print(recipe_info)
            meal_plan['meals'].append(recipe_info)

            for n in recipe_info['nutrition']['nutrients']:
                if n['name'].lower() in nutrients_to_check:
                    meal_plan['nutrients'][n['name'].lower()] += n['amount']

        user.mealplan = meal_plan
        users_data.save_to_file()
<<<<<<< HEAD
        return redirect(url_for("recommendations/mealplanner/view"))
=======
        return redirect(url_for("edit_meal_planner"))

>>>>>>> Feruza
    return render_template("create_meal_planner.html")


@app.route("/recommendations/mealplanner/view", methods=["GET"])
def edit_meal_planner():
    """
    Shows the meal plan for the user, where the user can edit.
    """
    # Checks if user is logged in, if not redirects to the authentication page.
    user = userAuthHelper()
    if not user:
        return redirect(url_for("auth_page"))

    mealplan = user.mealplan
    if not mealplan:
        return render_template("mealplanner.html", message="No meal plan found. Please create one.")

    # Determine if it's a daily or weekly plan
    if "meals" in mealplan:
        # Day plan
<<<<<<< HEAD
        return render_template("edit_mealplanner.html", day_plan=mealplan)
=======
        return render_template("mealplanner.html", day_plan=mealplan)
    elif "week" in mealplan:
        # Week plan
        return render_template("mealplanner.html", week_plan=mealplan["week"])
>>>>>>> Feruza
    else:
        return render_template("mealplanner.html", message="Unexpected meal plan format.")


def generate_mealplan(days: int, meals: List[str], user: UserProfile) -> Dict[str, List[Dict]]:
    """
    Provides a mealplan with categorized recipe recommendations for breakfast, lunch, and / or dinner.
    Falls back to random recipes if no results are found.
    :param days (int): The number of days for the meal plan.
    :param meals (List[str]): A list of meals to include in the meal plan (breakfast, lunch, dinner).
    :param user (UserProfile): The UserProfile object containing user information.
    :return (Dict[str, List[Dict]]): A dictionary with meal plan details.
    """
    if not user:
        return redirect(url_for("auth_page"))
    mealplan = {}
    for day in range(1, days + 1):
        mealplan[day] = {}
        for meal in meals:
            recipe = generate_recipe(meal)
            mealplan[day][meal] = recipe
    return mealplan

def generate_recipe(meal:str, exclude_ingredients: List[str] = []) -> Dict:
    """
    Generates a recipe based on the user's preferences and dietary restrictions.
    :param meal (str): The type of meal to generate a recipe for (e.g., breakfast, lunch, dinner).
    :param exclude_ingredients (List[str]): A optional list of ingredients to exclude from the recipe.
    :return (Dict): A dictionary containing the generated recipe details.
    """
    user = userAuthHelper()
    diet = user.diet
    intolerance = ",".join(user.allergies).join(exclude_ingredients)
    
    category_to_types = {
        "breakfast": ["breakfast"],
        "lunch": ["main course", "salad", "soup"],
        "dinner": ["main course", "side dish", "appetizer"]
    }
    
    types = category_to_types.get(meal, [meal])
    selected_type = random.choice(types)

    params = {
        "diet": diet,
        "excludeIngredients": intolerance,
        "type": selected_type,
        "number": 1,
        "apiKey": spoonacular_api_key
    }
    response = requests.get(
        "https://api.spoonacular.com/recipes/random", params=params
    )
    if response.status_code == 200:
        data = response.json()
        recipe = data.get("recipes", [])[0]
        return jsonify(recipe)
    else:
        return jsonify({"error": "Failed to fetch recipe"}), 500    


@app.route('/save_favorite/<recipe_id>', methods = ['POST'])
def save_favorite(recipe_id):
    # Checks if user is logged in, if not redirects to the authentication page.
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
    # Checks if user is logged in, if not redirects to the authentication page.
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
    # Checks if user is logged in, if not redirects to the authentication page.
    user = userAuthHelper()
    if not user:
        return redirect(url_for("auth_page"))
    return jsonify(user.saved_recipes)

@app.route('/save_results', methods=['POST'])
def save_results():
    # Checks if user is logged in, if not redirects to the authentication page.
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
    # Checks if user is logged in, if not redirects to the authentication page.
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
    """
    Helper function to check whether the user is logged in or not and returns the user profile.
    """
    if not session.get('logged_in'):
        return False
    logged_in_user = users_data.get_user(session['username'])
    if not logged_in_user:
        session['logged_in'] = False
        session['username'] = ""
        return False
    return logged_in_user

@app.route('/profile', methods=["GET", "POST"])
def profile():
    """
    Displays the user profile page with the information from the user profile.
    Users can update their profile information and save it.
    """
    # Checks if user is logged in, if not redirects to the authentication page.
    user = userAuthHelper()
    if not user:
        return redirect(url_for("auth_page"))
    
    # Retrieves the form data from the profile page and updates the user profile.
    if request.method == "POST":
        user.password = request.form.get("password")
        user.name = request.form.get("name")
        user.age = request.form.get("age")
        user.sex = request.form.get("sex")
        user.hight = request.form.get("hight")
        user.weight = request.form.get("weight")
        user.skin_color = request.form.get("skin_color")
        user.country = request.form.get("country")
        user.medication = request.form.get("medication", "").split(",")
        user.diet = request.form.get("diet")
        user.existing_conditions = request.form.get("existing_conditions", "").split(",")
        user.allergies = request.form.get("allergies", "").split(",")
        users_data.save_to_file()
        message = "Profile updated!"
        return render_template("profile.html", user=user, message=message)
    return render_template("profile.html", user=user)

@app.route('/logout')
def logout():
    """
    Will logout the user by clearing the session and redirects to the authentication page.
    """
    session.clear()
    return redirect(url_for("auth_page"))

if __name__ == "__main__":
    app.run(debug=True)
