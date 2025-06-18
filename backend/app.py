## develop your flask app here ##
from typing import Dict, List, Union
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    jsonify,
    Response,
)
from user_data.user_profile import UserProfile, UsersData
from dotenv import load_dotenv
from forms import SearchForm
from groq import Groq
import os, json, requests, random

load_dotenv()

app = Flask(__name__, template_folder="../frontend/templates")
app.secret_key = "VerySupersecretKey"  # A secret key for the sessions.

# Retrieves the spoonacular API key from the .env file
spoonacular_api_key: str = os.getenv("API_KEY")

client: str = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Initializes the UsersData object where all the user profiles will be stored in a json file.
users_data = UsersData()


def userAuthHelper() -> UserProfile:
    """
    Helper function to check whether the user is logged in or not and returns the user profile.
    :returns (UserProfile): The userprofile object of the corresponding user.
    """
    if not session.get("logged_in"):
        return False
    logged_in_user = users_data.get_user(session["username"])
    if not logged_in_user:
        session["logged_in"] = False
        session["username"] = ""
        return False
    return logged_in_user


@app.route("/")
def show_consent() -> Union[str, Response]:
    """
    Checks if the consent form is shown when the user has not given consent yet.
    Redirects to the authentication page if the user has already given consent.
    :returns:
        str: rendered HTML string for the consentform
        Response: Redirect response to the /auth route.
    """
    if not session.get("consent_given"):
        return render_template("consentform.html")
    return redirect(url_for("auth_page"))


@app.route("/consentform", methods=["POST"])
def handle_consent() -> Union[Response, None]:
    """
    This page shows a consentform. Once accepted it will redirect to the authentication page.
    :returns:
        None: If consent is not given.
        Response: Redirect response to the /auth route
    """
    accepted = request.form.get("accept", "false")

    if accepted.lower() == "true":
        session["consent_given"] = True
        return redirect(url_for("auth_page"))
    else:
        session["consent_given"] = False


@app.route("/auth", methods=["GET", "POST"])
def auth_page() -> Union[str, Response]:
    """
    Shows the authentication page where users can log in or choose to register if consent has been given, otherwise redirects to the consent form.
    If the user is logged in already, they will be redirected to the home page.
    If the user has not ben logged in yet, they will be redirected to the /auth/register page.
    :returns:
        str: Rendered authentication HTML page.
        Response: Redirect to consent or home page.
    """
    if session.get("consent_given") and not session.get("logged_in"):
        return render_template("auth.html")

    if not session.get("consent_given"):
        return redirect(url_for("show_consent"))

    if session.get("logged_in"):
        return redirect(url_for("home"))


@app.route("/auth/register", methods=["GET", "POST"])
def register() -> Union[str, Response]:
    """
    Handles the registration for a new user profile.
    Processes the registration form and adds a new user profile.
    If the registration is successful, redirects to the home page.
    If the registration fails because of an existing username, it shows an error message on the registration page.
    :returns:
        str: Rendered registration HTML page.
        Response: Redirect to home page on success.
    """
    if session.get("logged_in"):
        return redirect(url_for("home"))

    # Collecting user data from the registration form
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        name = request.form.get("name")
        age = int(request.form.get("age"))
        sex = request.form.get("sex")
        height = float(request.form.get("height"))
        weight = float(request.form.get("weight"))
        skin_color = request.form.get("skin_color")
        country = request.form.get("country")
        medication = request.form.get("medication", "").split(",")
        diet = request.form.get("diet")
        existing_conditions = request.form.get("existing_conditions", "").split(",")
        allergies = request.form.get("allergies", "").split(",")

        # Makes a user profile object and adds it to the users_data object
        try:
            user_profile = UserProfile(
                username,
                password,
                name,
                age,
                sex,
                height,
                weight,
                skin_color,
                country,
                medication,
                diet,
                existing_conditions,
                allergies,
            )

            # Adds the user profile object to the users_data object
            users_data.add_user(user_profile)
            session["logged_in"] = True
            session["username"] = username
            return redirect(url_for("home"))
        except ValueError as e:
            return render_template("registration.html", error=str(e))

    return render_template("registration.html")


@app.route("/auth/login", methods=["POST"])
def login() -> Union[str, Response]:
    """
    Handles the login form submission.
    If the username and password is authenticated, then the user will be redirected to the homepage.
    If the authentication fails, it will show the corresponding error message on the authentication page.

    :returns:
        str: Rendered authentication HTML page with error.
        Response: Redirect to home page on success.
    """
    # Retrieves the username and password from the login form
    if request.method == "POST":
        username = request.form.get("name")
        password = request.form.get("password")

        # Checks if the username and password corresponds to a user profile in the users_data object
        authenticated, message = users_data.user_authentication(username, password)

        # If the authentication succeeded, the user will be logged in and redirected to the homepage.
        if authenticated:
            session["logged_in"] = True
            session["username"] = username
            return redirect(url_for("home"))
        else:
            # If the authentication fails, the user will stay on the authentication page and get the corresponding error message.
            return render_template("auth.html", error=message)


@app.route("/logout")
def logout() -> Response:
    """
    Will logout the user by clearing the session and redirects to the consentform page.

    :returns:
        Response: Redirect to the consent form page.
    """
    # Clears the session
    session.clear()

    # Redirects the user to the consentform page.
    return redirect(url_for("show_consent"))


@app.route("/home", methods=["GET", "POST"])
def home():
    """
    This function displays the homepage.
    Users can generate a mealplan, submit their symtoms for a more custom mealplan and analyze their symptoms.
    """
    # Checks if user is logged in, if not redirects to the authentication page.
    form = SearchForm()
    user = userAuthHelper()
    if not user:
        return redirect(url_for("auth_page"))
    user_name = user.name

    if request.method == "POST":
        symptoms = request.form.get("symptoms").strip()
        if symptoms:
            return redirect(url_for("display_results", symptoms=symptoms))
        return redirect(url_for("home_page"))

    return render_template("homepage.html", response=user_name, form=form)


# function to analyze symptoms
def analyze_symptoms():
    """
    Sends the user's profile and symptoms to the Groq API and returns a text response.

    The result includes possible deficiencies, explanations, food suggestions, and tips.
    Other functions can parse this text to extract vitamins or recommended foods.
    """

    username = session["username"]
    user = users_data.get_user(username)

    symptoms = request.args.get("symptoms")
    session["last_symptoms"] = symptoms

    ai_prompt = f"""
        user profile:
        - name: {user.name}
        - age: {user.age}
        - sex: {user.sex}
        - height: {user.height}
        - weight: {user.weight}
        - skin tone: {user.skin_color}
        - medication: {", ".join(user.medication) if user.medication else "none"}
        - existing conditions: {", ".join(user.existing_conditions) if user.existing_conditions else "none"}
        - allergies: {", ".join(user.allergies) if user.allergies else "none"}
        - diet: {user.diet}

        user symptoms: {symptoms}

        required analysis: 
        1. top 3 likely vitamin/mineral deficiencies for each symptom based on the user's age, sex, height/weight. ONLY use these vitamin/minerals: Copper, Calcium, Choline, Cholesterol, Fluoride, SaturatedFat, VitaminA, VitaminC, VitaminD, VitaminE, VitaminK, VitaminB1, VitaminB2, VitaminB3, VitaminB5, VitaminB6, VitaminB12, Fiber, Folate, FolicAcid, Iodine, Iron, Magnesium, Manganese, Phosphorus, Potassium, Selenium, Sodium, Sugar, Zinc
        2. for each deficiency:
        - biological explanation, if the user's profile plays a role on the vitamin/nutrient like age, sex, existing conditions, include that information (short but detailed, easy to grasp. don't use the word "deficiency", in stead use something like "lack of")
        - top 3 foods to eat to fix the issue, keep in mind the user's medication, allergies and diet (comma-seperated list, no extra information, list each food on its own)
        - 1 lifestyle tip, that aligns with the user's profile
        3. flag any urgent medical concerns, including the user's medication, existing conditions and allergies

        return the analysis ONLY in this format:
        [vitamin/mineral name] (no extra stuff):
        - Why: [explanation]
        - Foods: [comma-separated list]
        - Tip: [actionable advice]

        [Urgency Note]: (optional)
        """

    # llm should incorporate the pesonal details of the user like allergies, pregnancy, etc

    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[{"role": "user", "content": ai_prompt}],
            temperature=0.7,
            max_completion_tokens=1024,
            top_p=1,
            stop=None,
        )
        return response.choices[0].message.content
    except Exception as e:
        print("Groq API failed:", e) 



def extract_deficiency_keywords(text: str):
    """
    Returns a list of nutrient or vitamin names found at the start of lines in the LLM response.

    Looks for known keys like 'vitamin d', 'iron', etc., followed by a colon.
    """
    known_keys = {
    "copper", "calcium", "choline", "cholesterol", "fluoride", "saturatedfat",
    "vitamina", "vitaminc", "vitamind", "vitamine", "vitamink", "vitaminb1",
    "vitaminb2", "vitaminb3", "vitaminb5", "vitaminb6", "vitaminb12", "fiber",
    "folate", "folicacid", "iodine", "iron", "magnesium", "manganese",
    "phosphorus", "potassium", "selenium", "sodium", "sugar", "zinc"
    }

    deficiencies = []

    for line in text.splitlines():
        if ":" in line:
            key = line.split(":")[0].strip().lower()
            if key in known_keys:
                deficiencies.append(key)

    return deficiencies

def vitamin_intake(deficiencies: List[str]) -> Dict[str, Dict[str, int]]:
    """
    """

    if not deficiencies:
        return {}
    
    prompt = f"""
    for each of the following nutrients/vitamins, suggest a minimum daily amount (in mg) to consume when mildly lacking it. the maximum amount cannot exceed 100 mg,
    in this JSON format: 
    {{
        "vitamin_a": {{ "minVitaminA": 5 }},
        "zinc": {{ "minZinc": 10 }}
    }}

    nutrients/vitamins: {", ".join(str(d) for d in deficiencies)}
    rule: only do it in the exameple format provided above.

    """
    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {"role": "system", "content": "You are a nutrition analysis API that responds strictly in JSON."},
                {"role": "user", "content": prompt}
                ],
            temperature=0.7,
            max_completion_tokens=1024,
            top_p=1,
            stop=None,
            response_format={"type": "json_object"}
        )

        uncleaned_data = json.loads(response.choices[0].message.content)

        cleaned = {
            nutrient_name: {
                min_amount_key: int(val)
                for min_amount_key, val in nutrient_data.items()
                if isinstance(val, (int, float, str)) and str(val).isdigit()
            }
            for nutrient_name, nutrient_data in uncleaned_data.items()
            if isinstance(nutrient_data, dict)
        }
        
        return cleaned

        
    except Exception as e:
        print("Groq API failed:", e)
        return {}
    

if __name__ == "__main__":
    deficiencies = ["VitaminA", "Zinc", "Calcium"]
    intake_recommendations = vitamin_intake(deficiencies)
    print("Recommended minimum intakes:")
    print(intake_recommendations)



# helper to function extract foods from the groq response
def extract_food_recs() -> List[str]:
    """
    Tries to get symptom analysis from Groq. Falls back if unavailable.
    Returns two lists: vitamins, foods
    """
    try:
        analysis_text = analyze_symptoms()
    except Exception as e:
        print("Groq API failed:", e)
        # fallback: use common vitamins and foods
        return ["vitamin c", "iron"], ["broccoli", "spinach", "orange"]

    vitamins = extract_deficiency_keywords(analysis_text)

    foods = []
    for line in analysis_text.splitlines():
        line = line.strip()
        if line.lower().startswith("- foods:"):
            parts = line[8:].split(",")
            foods.extend([x.strip() for x in parts])

    foods = list(dict.fromkeys(foods))  # remove duplicates

    return vitamins, foods


# results page to display analysis results
@app.route("/results")
def display_results():
    """
    This function displays the groq llm analysis on the webpage.
    """
    analysis = analyze_symptoms()
    symptoms = request.args.get("symptoms")

    return render_template("results.html", symptoms=symptoms, analysis=analysis)


@app.route("/recommendations")
def recommendations() -> Union[str, Response]:
    """
    Suggests personalized recipes categorized by meal type (breakfast, lunch, dinner),
    based on nutrient deficiencies extracted from user symptoms via LLM.

    If Groq or API fails, fallback logic avoids unrelated random suggestions.

    :returns:
        str: Rendered HTML template with recipe suggestions.
    """
    # Checks if user is logged in, if not redirects to the authentication page.
    logged_in_user = userAuthHelper()
    if not logged_in_user:
        return redirect(url_for("auth_page"))
    
    try:
        analysis_text = analyze_symptoms()
    except Exception as e:
        print("Error analyzing symptoms:", e)
        analysis_text = ""

    deficiencies = extract_deficiency_keywords(analysis_text)
    min_nutrients: Dict[str, Dict[str, int]] = vitamin_intake(deficiencies)

    diet = logged_in_user.diet
    intolerance = ",".join(logged_in_user.allergies)

    # Mapping meal types to Spoonacular's categories
    category_to_types = {
        "breakfast": ["breakfast", "bread", "snack"],
        "lunch": ["main course", "salad", "soup"],
        "dinner": ["main course", "side dish", "appetizer"]}

    meal_recipes = {}
    min_nutrient_params = {}

    # Flatten nutrient parameters for API request
    for nutrient_dict in min_nutrients.values():
        min_nutrient_params.update(nutrient_dict)

    # Loop through each meal category and fetch recipes
    for category, types in category_to_types.items():
        collected_recipes = []

        for t in types:
            params = {
                "diet": diet,
                "excludeIngredients": intolerance,
                "type": t,
                "number": 3,
                "apiKey": spoonacular_api_key,
            }
            params.update(min_nutrient_params)

            try:
                response = requests.get(
                    "https://api.spoonacular.com/recipes/complexSearch", params=params
                )
                data = response.json()
                collected_recipes.extend(data.get("results", []))
            except Exception as e:
                print(f"Error fetching {category} ({t}):", e)

    
        # fallback logic removed to avoid unrelated random recipes
        unique = {r["id"]: r for r in collected_recipes}
        meal_recipes[category] = list(unique.values())

    print("API params:", params)
    print("API response:", data)

    return render_template("recipes.html", recipes_by_meal=meal_recipes)


# display recipe details
@app.route("/recipe/<recipe_id>")
def recipe_details(recipe_id) -> str:
    """
    Fetches and displays detailed recipe information from the Spoonacular API.

    :param recipe_id: The ID of the recipe to display
    :return: Rendered HTML with full recipe info including nutrition
    """
    response = requests.get(
        f"https://api.spoonacular.com/recipes/{recipe_id}/information",
        params={"apiKey": spoonacular_api_key, "includeNutrition": True},
    )
    recipe_info = response.json()
    return render_template("recipe_details.html", recipe=recipe_info)


# Meal planner creation page
@app.route("/recommendations/mealplanner/spoonacular", methods=["GET", "POST"])
def spoonacular_builtin_mealplanner() -> Union[str, Response]:
    """
    Generates a built-in meal plan using the Spoonacular API based on user profile
    and calorie goals (maintain, gain, or lose weight).

    :return:
        str: Rendered HTML page with meal plan or error.
        Response: Redirect to meal planner editor on success.
    """
    # Check user login status
    user = userAuthHelper()
    if not user:
        return redirect(url_for("auth_page"))

    # Handle form submission
    if request.method == "POST":
        time_frame = request.form.get("timeFrame", "day")
        # calories = request.form.get("calories")
        type_of_diet = request.form.get("diet")

        # Base parameters
        params = {
            "apiKey": spoonacular_api_key,
            "timeFrame": time_frame,
            "diet": user.diet,
            "exclude": ",".join(user.allergies),
        }

        # Adjust calorie targets based on selected goal
        if type_of_diet == "gain":
            bmr = calculate_bmr()
            calories = bmr + 300
            params["targetCalories"] = calories
        elif type_of_diet == "loose":
            bmr = calculate_bmr()
            calories = bmr - 300
            params["targetCalories"] = calories
        elif type_of_diet == "health":
            bmr = calculate_bmr()
            calories = bmr
            params["targetCalories"] = calories

        # Make API call
        response = requests.get(
            "https://api.spoonacular.com/mealplanner/generate", params=params
        )
        if response.status_code == 200:
            # Save meal plan and redirect
            user.mealplan = response.json()
            print("spoonacular response mealplan")
            print(user.mealplan)
            users_data.save_to_file()
            return redirect(url_for("edit_meal_planner"))
        else:
            return render_template(
                "builtin_meal_planner.html", error="Failed to fetch meal plan."
            )

    # Show form on GET
    return render_template("builtin_meal_planner.html")


def get_meal_plan(api_key, diet=None, exclude=None, calories=None, time_frame="day") -> Dict:
    """
    Retrieves a meal plan from the Spoonacular API based on user preferences and calorie needs.

    :param api_key: Your Spoonacular API key
    :param diet: Diet type (e.g. vegetarian, keto)
    :param exclude: Ingredients to exclude (e.g. allergies)
    :param calories: Target calorie intake
    :param time_frame: 'day' or 'week'
    :return: Meal plan data as dictionary
    """
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


def calculate_bmr() -> float:
    """
    Calculates the basal metabolismic rate of a person based on their gender, age, height and weight.
    :return bmr: (float) bmr of the person
    """
    user = userAuthHelper()
    if not user:
        return redirect(url_for("auth_page"))

    bmr = 0

    height = user.height
    weight = user.weight
    gender = user.sex
    age = user.age
    if gender == "men":
        bmr = 88.362 + (weight * 13.397) + (height * 4.799) - (age * 5.677)
    elif gender == "female":
        bmr = 447.593 + (weight * 9.247) + (height * 3.098) - (age * 4.330)
    return bmr


@app.route("/recommendations/mealplanner/create", methods=["GET", "POST"])
def meal_planner() -> Union[str, Response]:
    """
    Creates a custom meal plan based on user-selected recipes.
    Calculates total nutrition (calories, protein, fat) from selected meals
    and saves the plan to the user's profile.

    :return:
        Response: Redirects to the meal plan view page on POST success.
        str: Renders the meal planner form page on GET.
    """
    if request.method == "POST":
        # Retrieve selected timeframe and target calories (not yet used in this version)
        time_frame = request.form.get("timeFrame", "day")  # "day" or "week"
        calories = request.form.get("calories")

        # Verify user authentication
        user = userAuthHelper()
        if not user:
            return redirect(url_for("auth_page"))

        # Initialize empty meal plan
        meal_plan = {}
        meal_plan["meals"] = []
        meal_plan["nutrients"] = {
            "calories": 0,
            "protein": 0,
            "fat": 0,
            "carbohydrates": 0,
        }
        nutrients_to_check = set(["calories", "protein", "fat"])
        selected_meals = request.form.getlist("meals")
        print("selected_meals")
        print(selected_meals)

        # Loop through selected recipe IDs and fetch their details
        for recipe_id in selected_meals:
            print(f"id = {recipe_id}")
            response = requests.get(
                f"https://api.spoonacular.com/recipes/{recipe_id}/information",
                params={"apiKey": spoonacular_api_key, "includeNutrition": True},
            )
            recipe_info = response.json()
            print("recipe_info")
            print(recipe_info)
            meal_plan["meals"].append(recipe_info)

            # Sum nutritional values for calories, protein, fat
            for nutrient in recipe_info["nutrition"]["nutrients"]:
                if nutrient["name"].lower() in nutrients_to_check:
                    meal_plan["nutrients"][nutrient["name"].lower()] += nutrient["amount"]

        # Save plan to user's profile
        user.mealplan = meal_plan
        users_data.save_to_file()

        return redirect(url_for("edit_meal_planner"))
    
    # If GET request, show the form
    return render_template("create_meal_planner.html")


@app.route("/recommendations/mealplanner/view", methods=["GET"])
def edit_meal_planner() -> str:
    """
    Displays the user's saved meal plan (either day or week plan).
    If no plan exists, shows a message prompting to create one.

    :return: Rendered meal planner HTML page.
    """
    # Checks if user is logged in, if not redirects to the authentication page.
    user = userAuthHelper()
    if not user:
        return redirect(url_for("auth_page"))

    mealplan = user.mealplan
    if not mealplan:
        return render_template(
            "mealplanner.html", message="No meal plan found. Please create one."
        )

    # Determine if it's a daily or weekly plan
    if "meals" in mealplan:
        # Day plan
        return render_template("mealplanner.html", day_plan=mealplan)
    elif "week" in mealplan:
        # Week plan
        return render_template("mealplanner.html", week_plan=mealplan["week"])
    else:
        return render_template(
            "mealplanner.html", message="Unexpected meal plan format."
        )


def generate_mealplan(
    days: int, meals: List[str], user: UserProfile
) -> Dict[str, List[Dict]]:
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

    # Generate recipes for each day and each selected meal type
    for day in range(1, days + 1):
        mealplan[day] = {}
        for meal in meals:
            recipe = generate_recipe(meal)
            mealplan[day][meal] = recipe

    return mealplan


def generate_recipe(meal: str, exclude_ingredients: List[str] = []) -> Dict:
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
        "dinner": ["main course", "side dish", "appetizer"],
    }

    types = category_to_types.get(meal, [meal])
    selected_type = random.choice(types)

    params = {
        "diet": diet,
        "excludeIngredients": intolerance,
        "type": selected_type,
        "number": 1,
        "apiKey": spoonacular_api_key,
    }
    response = requests.get("https://api.spoonacular.com/recipes/random", params=params)
    if response.status_code == 200:
        data = response.json()
        recipe = data.get("recipes", [])[0]
        return jsonify(recipe)
    else:
        return jsonify({"error": "Failed to fetch recipe"}), 500


@app.route("/save_favorite/<recipe_id>", methods=["POST"])
def save_favorite(recipe_id: str) -> Union[str, Response]:
    """
    Saves recipes to user profile when users decide to save the recipe to the favorites.
    It returns 401 if the recipe is already saved.
    :param recipe_id: ID of the recipe on the Spoonacular API
    """

    user = userAuthHelper()
    if not user:
        return redirect(url_for("auth_page"))
    recipe_id = int(recipe_id)
    
    # Check if already saved
    if recipe_id in user.saved_recipes:
        return "Already saved", 401
    else:
        # Save and persist to file
        user.saved_recipes.append(recipe_id)
        users_data.save_to_file()
        # return redirect(request.referrer or url_for("recommendations"))
        return "OK", 200


@app.route("/remove_favorite/<recipe_id>", methods=["POST"])
def remove_favorite(recipe_id: str) -> Union[str, Response]:
    """
    Removes recipes to user profile when users decide to remove the recipe from the favorites.
    It returns 401 if the recipe does not exist on the user profile.
    :param recipe_id: ID of the recipe on the Spoonacular API
    """

    user = userAuthHelper()
    if not user:
        return redirect(url_for("auth_page"))

    recipe_id = int(recipe_id)
    if recipe_id in user.saved_recipes:
        user.saved_recipes.remove(recipe_id)
        users_data.save_to_file()
        return "OK", 200
    return "Not exists", 401


@app.route("/show_favorites", methods=["GET"])
def show_favorites() -> Union[str, Response]:
    """
    Shows the recipes that were saved as a favorite before.
    
    :return: Rendered HTML page showing favorite recipes
    """
    user = userAuthHelper()
    if not user:
        return redirect(url_for("auth_page"))

    recipes = []
    # Fetch recipe details for each saved ID
    for recipe_id in user.saved_recipes:
        response = requests.get(
            f"https://api.spoonacular.com/recipes/{recipe_id}/information",
            params={"apiKey": spoonacular_api_key},
        )
        if response.ok:
            recipes.append(response.json())

    return render_template("favorites.html", recipes=recipes)


@app.route("/save_results", methods=["POST"])
def save_results() -> Union[str, Response]:
    """
    Saves analysis results to the user profile that were given by the Groq API
    It returns 401 if the there is no result.
    It returns 401 if the format of the analysis is not a json file.
    """

    user = userAuthHelper()
    if not user:
        return redirect(url_for("auth_page"))

    if not request.is_json:
        return "No result", 401

    analysis = request.get_json(silent=True)

    if not analysis:
        return "No result", 401

    symptoms = session.get("last_symptoms", "Unknown")

    user.analysis_results.append(
        {
            "symptoms": symptoms,
            "analyse": analysis,
        }
    )
    users_data.save_to_file()

    return "OK"


@app.route("/analysis_history")
def show_history() -> Union[str, Response]:
    """
    Shows the analysis history

    :return: Rendered HTML page showing saved analysis results.
    """

    user = userAuthHelper()
    if not user:
        return redirect(url_for("auth_page"))
    return render_template("analysis_history.html", results=user.analysis_results)


def get_nutrient_info() -> Dict[str, Any]:
    """
    Gets the information from nutrient_info.json file

    :return: Dictionary of nutrient data.
    """
    path = os.path.join(os.path.dirname(__file__), "data", "nutrient_info.json")
    with open(path, "r") as f:
        nutrients_data = json.load(f)
    return nutrients_data


@app.route("/nutrient", methods=["GET", "POST"])
def nutrients() -> Response:
    """
    Gets the nutrient from the frontend and redirects to the information page based on given nutrient.
    
    :return: Redirect to detail view for the nutrient.
    """
    nutrient = request.args.get("nutrient")
    if not nutrient:
        assert 404
    return redirect(url_for("nutrients_info_page", nutrient_name=nutrient))


@app.route("/nutrient/<nutrient_name>", methods=["GET", "POST"])
def nutrients_info_page(nutrient_name: str) -> Union[str, Response]:
    """
    Shows the information of the given nutrient.

    :param nutrient_name: Name of the nutrient (e.g., 'iron').
    :return: Nutrient info page if found, else 404.
    """
    nutrient_info = get_nutrient_info()
    nutrient = nutrient_info.get(nutrient_name.upper())

    if nutrient:
        return render_template(
            "nutrient_info_page.html", name=nutrient_name.upper(), info=nutrient
        )

    return "Nutrient not found", 404


@app.route("/search", methods=["GET", "POST"])
def search_bar() -> Response:
    """
    Handles the search request from the search button on the frontend.
    If the search request is POST, and a valid submit, it redirects to the search results.
    Else, it redirects to the home page.
    """
    form = SearchForm()
    if request.method == "POST" and form.validate_on_submit():
        query = form.search_bar.data
        return redirect((url_for("search_results", query=query)))
    return redirect((url_for("home")))


@app.route("/search_bar_result/<query>")
def search_results(query: str) -> Union[str, Response]:
    """
    Displays the search bar results.

    :param query: The given nutrient name.
    :return: Info page or error message.
    """
    nutrient_info = get_nutrient_info()
    nutrient = nutrient_info.get(query.upper())

    if nutrient:
        return render_template(
            "nutrient_info_page.html", name=query.upper(), info=nutrient
        )

    return "No nutrient", 404


@app.route("/profile", methods=["GET", "POST"])
def profile() -> Union[str, Response]:
    """
    Displays the user profile page with the information from the user profile.
    Users can update their profile information and save it.

    :returns:
        str: Rendered HTML for the profile page either with or without an error message.
        Response: Redirects to the authentication page if the user is not logged in.
    """
    # Checks if user is logged in, if not redirects to the authentication page.
    user: UserProfile = userAuthHelper()
    if not user:
        return redirect(url_for("auth_page"))

    # Retrieves the form data from the profile page and updates the user profile.
    if request.method == "POST":
        # Uses the helperfunction to check if the required fields are not left blank, for it would show a error message.
        error = validate_required_fields_profile(request.form)
        if error:
            return render_template("profile.html", user=user, message=error)

        user.password = request.form.get("password")
        user.name = request.form.get("name")
        user.age = int(request.form.get("age"))
        user.sex = request.form.get("sex")
        user.height = float(request.form.get("height"))
        user.weight = float(request.form.get("weight"))
        user.skin_color = request.form.get("skin_color")
        user.country = request.form.get("country")
        user.medication = request.form.get("medication", "").split(",")
        user.diet = request.form.get("diet")
        user.existing_conditions = request.form.get("existing_conditions", "").split(
            ","
        )
        user.allergies = request.form.get("allergies", "").split(",")

        # Saves the updated data to the users data file.
        users_data.save_to_file()

        message: str = "Profile updated!"
        return render_template("profile.html", user=user, message=message)

    return render_template("profile.html", user=user)


def validate_required_fields_profile(form) -> Union[None, str]:
    """
    Helper function for the profile page to check whether the required fields are left blank to return the correct error.

    :param form: a html form.
    :returns:
        str: An error message stating that the field is required to fill in.
        None: If a required fields are filled in.
    """

    required_fields = [
        "name",
        "age",
        "sex",
        "height",
        "weight",
        "skin_color",
        "country",
        "password",
    ]
    for field in required_fields:
        value = form.get(field)
        # Returns an error message if a required field is left blank.
        if value is None or str(value).strip() == "":
            return f"{field.capitalize()} is required."
    return None


if __name__ == "__main__":
    app.run(debug=True)
