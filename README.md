# Main README file
# NutriSpoon: Nourishing your health, one smart bite at a time

## Brief description of the project

We are group 8 and this is our app called `NutriSpoon`, an application which allows users to improve their health with food. Users can register with their personal information and input their symptoms to get an AI-driven analysis on possible inadequate nutrient intake. Specific nutrients with corresponding foods are recommended to consume and users then have the option to get custom recipes based on the nutrients recommended to consume. The different nutrients tested are: Copper, Calcium, Choline, Cholesterol, Fluoride, SaturatedFat, VitaminA, VitaminC, VitaminD, VitaminE, VitaminK, VitaminB1, VitaminB2, VitaminB3, VitaminB5, VitaminB6, VitaminB12, Fiber, Folate, FolicAcid, Iodine, Iron, Magnesium, Manganese, Phosphorus, Potassium, Selenium, Sodium and Zinc. Each nutrient has it's own page with the it's function, why it's important, deficiency symptoms and top food sources. To make it even more convenient for the user, they can choose to generate a custom made mealplan. With NutriSpoon, we strive to improve the health of users all over the world and to spread more awareness about nutrient inadequacy.

## Team members

**Feruza Bakhtiyorova**
**Yasmina Assarrar**
**Sevval Yelmer**
**Dora Koshimova**

## Installation details

### Prerequisites:
- Ensure you have python == 3.12 installed.
- Ensure you have all dependencies installed. These are listed in a file named `requirements.txt`. You can install them using `pip install -r requirements.txt`.

#### 1. Set up environment variables

Create a `.env` file in the project root with the following content (replace with your actual keys):

```
GROQ_API_KEY=your_groq_api_key
API_KEY=your_spoonacular_api_key
```

Keys can be retrieved from following sites:
- **Groq API:** https://console.groq.com/keys
- **Spoonacular API:**  https://spoonacular.com/food-api/console#Dashboard

### Starting the server:

1. Open a terminal window.
2. In that terminal, navigate to the ferufera-keik0o-sevvalyelmer-yassie101-general-template directory using `cd` followed by the path.
3. Then, run `python3 app.py` to start the `NutriSpoon` Flask server.

### Accessing the servers:

Once the server is running, you should be able to access it using the provided port number.

## Project Structure

Below is an overview of the folder structure for this project. It’s organized to separate backend, frontend, configuration files, and tests clearly.

```
backend/                                # Backend source code
│
├── __pycache__/                        # Python bytecode cache for backend modules
│
├── app.py                              # Main Flask application
├── forms.py                            # Flask-WTF or custom form definitions
│
├── data/                               # Data files used by backend
│   └── nutrient_info.json              # JSON file with nutrient information
│
├── tests/                              # Backend test suite
│   ├── __pycache__/                    # Bytecode cache for tests
│   ├── .pytest_cache/                  # pytest cache for test runs (inside tests)
│   ├── context.py                      # Test fixtures and setup
│   └── test_nutrispoon.py              # Main backend test cases
│
├── user_data/                          # User-related backend data and logic
│   ├── __pycache__/                    # Bytecode cache for user_data module
│   │   ├── __init__.cpython-310.pyc    # Compiled __init__.py
│   │   └── user_profile.cpython-310.pyc# Compiled user_profile.py
│   ├── __init__.py                     # Marks directory as Python package
│   ├── recipes.py                      # Logic for handling recipes
│   ├── user_profile.py                 # Logic for user profiles and data
│   └── users.json                      # JSON file storing user data
│
frontend/                               # Frontend source code
│
├── templates/                          # HTML templates rendered by Flask
│   ├── auth.html                       # Authentication form page
│   ├── base.html                       # Base template for inheritance
│   ├── builtin_meal_planner.html       # Built-in meal planner page
│   ├── consentform.html                # Consent form page
│   ├── create_meal_planner.html        # Create custom meal planner page
│   ├── edit_mealplanner.html           # Edit meal planner page
│   ├── favorites.html                  # User's favorite recipes page
│   ├── homepage.html                   # Homepage for logged-in users
│   ├── index.html                      # Landing page
│   ├── mealplanner.html                # Meal planner overview page
│   ├── nutrient_info_page.html         # Nutrient information page
│   ├── profile.html                    # User profile page
│   ├── recipe_details.html             # Recipe details page
│   ├── recipes.html                    # Recipes overview page
│   ├── registration.html               # Registration form page
│   └── results.html                    # Results page for recommendations/analysis
│
├── requirements.txt                    # The app requirements
│
.env                                    # Environment variables for Flask and other tools
.gitignore                              # Git ignore rules
README.md                               # Project documentation  
requirements.md                 
```


## Requirements

For the requirements of this project, see [requirements](requirements.md) for a detailed featue list.


