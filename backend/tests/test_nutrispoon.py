### first backend tests file ###

import json, os, pytest
import time
from context import app, UserProfile, UsersData
from unittest.mock import patch, MagicMock
from flask.testing import FlaskClient
from app import (
    app,
    users_data,
    home,
    analyze_symptoms,
    extract_food_recs,
    display_results,
    recipe_details,
    get_nutrient_info,
    calculate_bmr,
    vitamin_intake
)
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture
def client() -> FlaskClient:
    """
    Set up for a Flask test client.
    :returns:
        FlaskClient: a Flask test client.
    """
    app.config["TESTING"] = True

    client = app.test_client()
    yield client


@pytest.fixture
def set_users_data() -> UsersData:
    """
    Set up of a UserData object with a test storage file.
    :returns:
        UsersData: The usersdata object where the testuser's data will be stored.
    """
    # Sets a json file to store the test users data
    test_users_file = "test_users.json"

    # Removes any pre-existing test file
    if os.path.exists(test_users_file):
        os.remove(test_users_file)

    # Initializes a usersdata object to store of the test users data.
    users_data = UsersData(test_users_file)
    with patch("app.users_data", users_data):
        yield users_data

    # Removes the temporary test file
    if os.path.exists(test_users_file):
        os.remove(test_users_file)


def set_user_login(client) -> None:
    """
    Helper function to add a testuser to the database and login.
    :param client: the Flask test client
    """
    # Creates a UserProfile object for a testuser
    if "testusername" not in users_data.users:
        user = UserProfile(
            "testusername",
            "testpassword",
            "Test User",
            20,
            "Female",
            175.0,
            70.0,
            "medium",
            "The Netherlands",
            "None",
            "None",
        )

        # Saves the object to the user_data object
        users_data.add_user(user)

    # Makes sure the client is logged in for the session
    with client.session_transaction() as sess:
        sess["logged_in"] = True
        sess["username"] = "testusername"


def assert_200(response) -> None:
    """
    Helper function to assert that the response status code is 200.
    :param response: The response object to check.
    """
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"


###############################################################################
#                                                                             #
#                   CONSENT FORM PAGE TESTS                                   #
#                                                                             #
###############################################################################


def test_show_consent(client) -> None:
    """
    Tests that the consent form is displayed when the web is started.
    :param client: the Flask test client
    """
    response = client.get("/")
    assert_200(response)
    assert b"consent form" in response.data.lower()


def test_handle_consent(client) -> None:
    """
    Tests that submitting the consent form causes redirection to the authentication page.
    :param client: the Flask test client
    """
    response = client.post(
        "/consentform", data={"accept": "true"}, follow_redirects=True
    )
    assert_200(response)
    assert b"login" in response.data.lower()


def test_redirect_to_consent_when_no_consent(client) -> None:
    """
    Tests that accessing the authentication page with no consent redirects to the consent form.
    :param client: the Flask test client
    """
    response = client.get("/auth", follow_redirects=True)
    assert_200(response)
    assert b"consent form" in response.data.lower()


###############################################################################
#                                                                             #
#                   LOGIN PAGE TESTS                                          #
#                                                                             #
###############################################################################


def test_login_works_correctly(client, set_users_data) -> None:
    """
    Tests that logging in with an existing user works correctly, and redirects to the home page.
    :param client: the Flask test client
    :param set_users_data: The usersdata object where the test users data will be stored.
    """
    # Creates a new userprofile object .
    user = UserProfile(
        "testusername",
        "testpassword",
        "Test User",
        20,
        "Female",
        175.0,
        70.0,
        "medium",
        "The Netherlands",
        "None",
        "None",
    )
    # Stores the user object in the user data.
    set_users_data.add_user(user)

    # Checks if the consentform has been accepted.
    client.post("/consentform", data={"accept": "true"}, follow_redirects=True)

    # Checks the response if the client logs in with their username and password.
    response = client.post(
        "/auth/login",
        data={"name": "testusername", "password": "testpassword"},
        follow_redirects=True,
    )
    assert_200(response)
    assert b"homepage" in response.data.lower()


def test_login_with_false_username_fails(client, set_users_data) -> None:
    """
    Tests that logging in with an non-existing user will not redirect to home page and gives the correct error message.
    :param client: the Flask test client
    :param set_users_data: The usersdata object where the test users data will be stored.
    """

    # Checks if the consentform has been accepted.
    client.post("/consentform", data={"accept": "true"}, follow_redirects=True)

    # Checks if the correct error message is displayed if the client logs in with a false username and password.
    response = client.post(
        "/auth/login",
        data={"name": "testusername", "password": "testpassword"},
        follow_redirects=True,
    )
    assert b"username not found in database" in response.data.lower()
    assert_200(response)


def test_login_with_false_password_fails(client, set_users_data) -> None:
    """
    Tests that logging in with an existing username and false password will not redirect to home page and gives the correct error message.
    :param client: the Flask test client
    :param set_users_data: The usersdata object where the test users data will be stored.
    """
    # Creates a new userprofile object .
    user = UserProfile(
        "testusername",
        "testpassword",
        "Test User",
        20,
        "Female",
        175.0,
        70.0,
        "medium",
        "The Netherlands",
        "None",
        "None",
    )
    # Stores the user object in the user data.
    set_users_data.add_user(user)

    # Checks if the consentform has been accepted.
    client.post("/consentform", data={"accept": "true"}, follow_redirects=True)

    # Checks if the correct error message is displayed if the client logs in with a correct username and false password.
    response = client.post(
        "/auth/login",
        data={"name": "testusername", "password": "falsepassword"},
        follow_redirects=True,
    )
    assert b"wrong password" in response.data.lower()
    assert_200(response)


###############################################################################
#                                                                             #
#                   REGISTER PAGE TESTS                                       #
#                                                                             #
###############################################################################


def test_register_works_correctly(client, set_users_data) -> None:
    """
    Tests that registering a new user works correctly and redirects to the home page.
    :param client: the Flask test client
    :param set_users_data: The usersdata object where the test users data will be stored.
    """
    # Checks if the consentform has been accepted.
    client.post("/consentform", data={"accept": "true"}, follow_redirects=True)

    # Posts the register form with the information of a test user
    client.post(
        "/auth/register",
        data={
            "username": "testuser",
            "password": "testpassword",
            "name": "Test User",
            "age": 25,
            "sex": "Female",
            "height": 170.0,
            "weight": 60.0,
            "skin_color": "medium",
            "country": "The Netherlands",
            "medication": "",
            "diet": "None",
            "existing_conditions": "",
            "allergies": "",
        },
        follow_redirects=True,
    )

    # Checks if the testuser's data is stored in the test users data file.
    assert "testuser" in set_users_data.users

    # Checks if the redirect to the homepages succeded
    response = client.get("/home", follow_redirects=True)
    assert_200(response)
    assert b"homepage" in response.data.lower()


def test_register_with_missing_password_fails(client, set_users_data) -> None:
    """
    Tests that registering a new user with missing information of a mandatory part such as password gives the corresponding error message.
    :param client: the Flask test client
    :param set_users_data: The usersdata object where the test users data will be stored.
    """
    # Checks if the consentform has been accepted.
    client.post("/consentform", data={"accept": "true"}, follow_redirects=True)

    # Posts the users information to the register form without a password
    response = client.post(
        "/auth/register",
        data={
            "username": "testuser",
            "name": "Test User",
            "age": 25,
            "sex": "Female",
            "height": 170.0,
            "weight": 60.0,
            "skin_color": "medium",
            "country": "The Netherlands",
            "medication": "",
            "diet": "None",
            "existing_conditions": "",
            "allergies": "",
        },
        follow_redirects=True,
    )

    # Checks if the user's data has not been stored as a userprofile object.
    assert "testuser" not in set_users_data.users

    # Checks if the correct errormessage is displayed.
    assert b"password is required" in response.data.lower()
    assert_200(response)


def test_register_with_existing_username_fails(client, set_users_data) -> None:
    """
    Tests that when the user tried to register with an already existing username, it gives the corresponding error message.
    :param client: the Flask test client
    :param set_users_data: The usersdata object where the test users data will be stored.
    """

    # Creates a user profile to directly add to the users data.
    user = UserProfile(
        "Hansklok",
        "testpassword2",
        "Test User 2",
        25,
        "Male",
        187.0,
        80.0,
        "light",
        "Germany",
        "None",
        "None",
    )
    # Adds the user to the users data test file.
    set_users_data.add_user(user)

    # Checks if the consentform has been accepted.
    client.post("/consentform", data={"accept": "true"}, follow_redirects=True)

    # Posts the users information to the register form with an existing username.
    response = client.post(
        "/auth/register",
        data={
            "username": "Hansklok",
            "password": "testpassword",
            "name": "Test User",
            "age": 25,
            "sex": "Female",
            "height": 170.0,
            "weight": 60.0,
            "skin_color": "medium",
            "country": "The Netherlands",
            "medication": "",
            "diet": "None",
            "existing_conditions": "",
            "allergies": "",
        },
        follow_redirects=True,
    )

    # Checks if the correct errormessage is displayed.
    assert (
        b"user with username &#39;hansklok&#39; already exists" in response.data.lower()
    )
    assert_200(response)


###############################################################################
#                                                                             #
#                   LOGOUT PAGE TESTS                                         #
#                                                                             #
###############################################################################


def test_logout(client) -> None:
    """
    Tests that when logging out the session is cleared and the user will be redirected to the consent form.
    :param client: the Flask test client.
    """
    # Logges in the user and creates a session
    set_user_login(client)

    # The user loggs out
    response = client.get("/logout", follow_redirects=True)

    # Tests if the session is cleared
    assert_200(response)
    with client.session_transaction() as session:
        assert "logged_in" not in session
        assert "username" not in session

    # Test if the user is redirected to the consent form.
    assert b"consent" in response.data.lower()


###############################################################################
#                                                                             #
#                   PROFILE PAGE TESTS                                        #
#                                                                             #
###############################################################################


def test_profile_page(client) -> None:
    """
    Tests that the profile page can be accessed when the user is logged in.
    :param client: the Flask test client
    """
    set_user_login(client)
    response = client.get("/profile")
    assert_200(response)
    assert b"Profile" in response.data


def test_profile_page_change_age(client, set_users_data) -> None:
    """
    Tests that when the user changes their age on the profile page, it will be changed in the user data object.
    :param client: the Flask test client
    :param set_users_data: The usersdata object where the test users data will be stored.
    """
    # Sets a user profile and adds it to the test user data.
    user = UserProfile(
        "agetestuser",
        "testpassword",
        "Test User",
        18,
        "Female",
        175.0,
        70.0,
        "medium",
        "The Netherlands",
        "None",
        "None",
    )
    set_users_data.add_user(user)

    # Logges in the user
    with client.session_transaction() as session:
        session["logged_in"] = True
        session["username"] = "agetestuser"

    # Changes the user;s age on the profile page form.
    response = client.post(
        "/profile",
        data={
            "name": "Test User",
            "age": 19,  # Age changed to 19
            "sex": "Female",
            "height": 175.0,
            "weight": 70.0,
            "skin_color": "medium",
            "country": "The Netherlands",
            "medication": "",
            "diet": "None",
            "existing_conditions": "",
            "allergies": "",
            "password": "testpassword",
        },
        follow_redirects=True,
    )
    # Retrieves the user's profile object from the users data
    updated_user = set_users_data.get_user("agetestuser")

    # Checks if the age has been adjusted in the data.
    assert updated_user.age == 19
    assert_200(response)


def test_profile_leave_blank_password_fails(client, set_users_data) -> None:
    """
    Tests a user profile change where a required userprofile parameter such as password is left blank to check if an error will occur and the password is not saved in the database.
    :param client: the Flask test client
    :param set_users_data: The usersdata object where the test users data will be stored.
    """
    # Sets a new user profile.
    user = UserProfile(
        "testusername",
        "testpassword",
        "Test User",
        20,
        "Female",
        175.0,
        70.0,
        "medium",
        "The Netherlands",
        "None",
        "None",
    )

    # Saves the user profile object to the user data.
    set_users_data.add_user(user)

    # Log in the user
    with client.session_transaction() as session:
        session["logged_in"] = True
        session["username"] = "testusername"

    # Submits a form on the profile page to update the users information.
    response = client.post(
        "/profile",
        data={
            "name": "Test User",
            "age": 19,
            "sex": "Female",
            "height": 175.0,
            "weight": 70.0,
            "skin_color": "medium",
            "country": "The Netherlands",
            "medication": "",
            "diet": "None",
            "existing_conditions": "",
            "allergies": "",
            "password": "",  # Leaves the password empty
        },
        follow_redirects=True,
    )

    # Retrieves the user's profile object from the users data
    updated_user = set_users_data.get_user("testusername")

    # Checks if the old password is still remaining in the data. Old password = testpassword
    assert updated_user.password == "testpassword"
    assert_200(response)


###############################################################################
#                                                                             #
#                            RECOMMENDATIONS TESTS                            #
#                                                                             #
###############################################################################


def test_generate_recipe_structure():
    from app import generate_recipe

    with app.app_context():
        with patch("app.requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {
                "recipes": [{"title": "Test Recipe", "id": 1234}]
            }
            with patch("app.userAuthHelper") as mock_auth:
                mock_auth.return_value = MagicMock(diet="", allergies=[])
                result = generate_recipe("breakfast")
                assert result.status_code == 200


def test_extract_food_recs_parsing():
    with patch(
        "app.analyze_symptoms",
        return_value="""
Vitamin D:
- Why: lack of sunlight causes poor absorption of calcium
- Foods: salmon, egg yolk, mushrooms
- Tip: spend 15 minutes in the sun daily
""",
    ):
        from app import extract_food_recs

        _, foods = extract_food_recs()
        assert "salmon" in foods
        assert "egg yolk" in foods
        assert "mushrooms" in foods
        assert len(foods) == 3


def test_display_results(client):
    """
    Tests if the display_results function and /results route correctly display groq ai's response as in the prompt, so explanation, foods and a tip.
    """
    test_response = (
        "Vitamin A\n- Why: acne\n- Foods: carrot, eggs\n- Tip: foods rich in vitamin A"
    )
    with patch("app.analyze_symptoms", return_value=test_response):
        with client.session_transaction() as session:
            session["logged_in"] = True
            session["username"] = "testusername"

        result = client.get("/results?symptoms=acne")
        assert b"acne" in result.data
        assert b"carrot" in result.data
        assert b"eggs" in result.data
        assert b"foods rich in vitamin A" in result.data


def test_recipe_details(client):
    """
    Tests if the recipe_details function correctly retrieves the recipe details such as ingredients, nutrients and instructions.
    """
    with patch("app.requests.get") as test_get:
        test_get.return_value.json.return_value = {
            "title": "test recipe",
            "image": "https://example.com/image.jpg",
            "instructions": "step1",
            "extendedIngredients": [],
            "nutrition": {},
        }
        response = client.get("/recipe/12345")
        assert_200(response)
        assert b"test recipe" in response.data


###############################################################################
#                                                                             #
#                   FAVORITE RECIPE SAVING/REMOVING                           #
#                                                                             #
###############################################################################


def test_add_saving(client, set_users_data):
    """
    Tests whether recipe is succesfully saved to the profile.
    Tests whether the duplicate saving will throw an error.
    """
    # print("it works!")
    user = UserProfile(
        "testusername",
        "testpassword",
        "Test User",
        20,
        "Female",
        175.0,
        70.0,
        "medium",
        "The Netherlands",
        "None",
        "None",
    )

    # Saves the user profile object to the user data.

    set_users_data.add_user(user)

    # Log in the user
    with client.session_transaction() as session:
        session["logged_in"] = True
        session["username"] = "testusername"

    set_users_data.get_user("testusername").saved_recipes = []

    response = response = client.post("/save_favorite/4")
    assert_200(response)
    assert b"OK" in response.data

    response2 = client.post("/save_favorite/4")
    assert response2.status_code == 401
    assert b"Already saved" in response2.data


def test_remove_saving(client, set_users_data):
    """
    Tests whether recipe is succesfully removed from the profile.
    Tests whether trying to remove the not existed recipe will throw an error.
    """
    user = UserProfile(
        "testusername",
        "testpassword",
        "Test User",
        20,
        "Female",
        175.0,
        70.0,
        "medium",
        "The Netherlands",
        "None",
        "None",
    )

    # Saves the user profile object to the user data.

    set_users_data.add_user(user)

    # Log in the user
    with client.session_transaction() as session:
        session["logged_in"] = True
        session["username"] = "testusername"

    set_users_data.get_user("testusername").saved_recipes = []

    response = response = client.post("/save_favorite/4")
    assert_200(response)
    assert b"OK" in response.data

    response2 = client.post("/remove_favorite/4")
    assert_200(response)
    assert b"OK" in response2.data

    response2 = client.post("/remove_favorite/4")
    assert response2.status_code == 401
    assert b"Not exists" in response2.data


def test_show_favs(client):
    """
    Tests if the saved mealplan page is loading correctly for a logged in user.
    """
    with client.session_transaction() as session:
        session["logged_in"] = True
        session["username"] = "testusername"
    response = client.get("/show_favorites")
    assert_200(response)


###############################################################################
#                                                                             #
#                                BMR CALCULATION                              #
#                                                                             #
###############################################################################
def test_bmr_calculation_for_male(client, set_users_data):
    """
    Tests to see if thr BMR calcualtion works correctly.
    """
    user = UserProfile(
        "testusername",
        "testpassword",
        "Test User",
        20,
        "male",
        175.0,
        70.0,
        "medium",
        "The Netherlands",
        "None",
        "None",
    )

    # Saves the user profile object to the user data.

    set_users_data.add_user(user)

    # Log in the user
    with client.session_transaction() as session:
        session["logged_in"] = True
        session["username"] = "testusername"
    with client.application.test_request_context():
        with patch("app.userAuthHelper", return_value=user):
            bmr = calculate_bmr()

    expected_bmr = (
        88.362 + (user.weight * 13.397) + (user.height * 4.799) - (user.age * 5.677)
    )
    assert bmr == expected_bmr


def test_bmr_calculation_for_female(client, set_users_data):
    """
    Tests to see if thr BMR calcualtion works correctly.
    """
    user = UserProfile(
        "testusername",
        "testpassword",
        "Test User",
        20,
        "female",
        175.0,
        70.0,
        "medium",
        "The Netherlands",
        "None",
        "None",
    )

    # Saves the user profile object to the user data.

    set_users_data.add_user(user)

    # Log in the user
    with client.session_transaction() as session:
        session["logged_in"] = True
        session["username"] = "testusername"
    with client.application.test_request_context():
        with patch("app.userAuthHelper", return_value=user):
            bmr = calculate_bmr()

    expected_bmr = (
        447.593 + (user.weight * 9.247) + (user.height * 3.098) - (user.age * 4.330)
    )
    assert bmr == expected_bmr


def test_calorie_calculation_for_male(client, set_users_data):
    """
    Tests to see if thr calorie calcualtion works correctly.
    """
    user = UserProfile(
        "testusername",
        "testpassword",
        "Test User",
        20,
        "male",
        175.0,
        70.0,
        "medium",
        "The Netherlands",
        "None",
        "None",
    )

    # Saves the user profile object to the user data.

    set_users_data.add_user(user)

    diet = "loose"

    # Log in the user
    with client.session_transaction() as session:
        session["logged_in"] = True
        session["username"] = "testusername"

    with client.application.test_request_context():
        with patch("app.userAuthHelper", return_value=user):
            bmr = calculate_bmr()

    expected_bmr = (
        88.362 + (user.weight * 13.397) + (user.height * 4.799) - (user.age * 5.677)
    )
    expected_calories = expected_bmr - 300.00

    assert expected_calories == bmr - 300.00

###############################################################################
#                                                                             #
#                                    GROQ                                     #
#                                                                             #
###############################################################################
    
def test_vitamin_intake():
    test_response = {
        "vitamin_a": {"minVitaminA": 50},         
        "zinc": {"minZinc": 40},                   
        "calcium": {"minCalcium": 30}
    }
    
    with patch("app.client.chat.completions.create") as test_create:
        test_create.return_value.choices[0].message.content = json.dumps(test_response)
        result = vitamin_intake(["VitaminA", "Zinc"])
        assert result == test_response

###############################################################################
#                                                                             #
#                           MEALPLANNER TESTS                                 #
#                                                                             #
###############################################################################


def test_generate_mealplan_structure():
    from app import generate_mealplan, UserProfile

    user = UserProfile(
        "testusername",
        "testpassword",
        "Test User",
        20,
        "Female",
        175.0,
        70.0,
        "medium",
        "The Netherlands",
        "None",
        "None",
    )
    with patch("app.generate_recipe") as mock_gen:
        mock_gen.return_value = {"title": "Test Recipe"}
        plan = generate_mealplan(2, ["breakfast", "dinner"], user)
        assert 1 in plan and 2 in plan
        assert "breakfast" in plan[1]
        assert "dinner" in plan[1]


def test_spoonacular_builtin_mealplanner_success(client, set_users_data):
    user = UserProfile(
        "testusername",
        "testpassword",
        "Test User",
        20,
        "Female",
        175.0,
        70.0,
        "medium",
        "The Netherlands",
        "None",
        "None",
    )
    set_users_data.add_user(user)
    with client.session_transaction() as sess:
        sess["logged_in"] = True
        sess["username"] = "testusername"

    with patch("app.requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = (
            mock_get.return_value.json.return_value
        ) = {
            "meals": [],
            "nutrients": {
                "calories": 2000,
                "protein": 100,
                "fat": 70,
                "carbohydrates": 250,
            },
        }
        response = client.post(
            "/recommendations/mealplanner/spoonacular",
            data={"timeFrame": "day"},
            follow_redirects=True,
        )
        assert_200(response)


def test_spoonacular_builtin_mealplanner_fail(client, set_users_data):
    user = UserProfile(
        "testusername",
        "testpassword",
        "Test User",
        20,
        "Female",
        175.0,
        70.0,
        "medium",
        "The Netherlands",
        "None",
        "None",
    )
    set_users_data.add_user(user)
    with client.session_transaction() as sess:
        sess["logged_in"] = True
        sess["username"] = "testusername"

    with patch("app.requests.get") as mock_get:
        mock_get.return_value.status_code = 500
        response = client.post(
            "/recommendations/mealplanner/spoonacular",
            data={"timeFrame": "day"},
            follow_redirects=True,
        )
        assert_200(response)
        assert b"failed to fetch" in response.data.lower()


def test_mealplanner_create_nutrient_calculation(client, set_users_data):
    user = UserProfile(
        "testusername",
        "testpassword",
        "Test User",
        20,
        "Female",
        175.0,
        70.0,
        "medium",
        "The Netherlands",
        "None",
        "None",
    )
    set_users_data.add_user(user)
    with client.session_transaction() as sess:
        sess["logged_in"] = True
        sess["username"] = "testusername"

    mock_nutrients = {
        "nutrition": {
            "nutrients": [
                {"name": "Calories", "amount": 500},
                {"name": "Protein", "amount": 30},
                {"name": "Fat", "amount": 20},
                {"name": "Carbohydrates", "amount": 50},
            ]
        }
    }
    with patch("app.requests.get") as mock_get:
        mock_get.return_value.json.return_value = mock_nutrients
        mock_get.return_value.status_code = 200

        response = client.post(
            "/recommendations/mealplanner/create",
            data={"meals": ["123"]},
            follow_redirects=True,
        )
        assert_200(response)


def test_mealplanner_view_day(client, set_users_data):
    user = UserProfile(
        "testusername",
        "testpassword",
        "Test User",
        20,
        "Female",
        175.0,
        70.0,
        "medium",
        "The Netherlands",
        "None",
        "None",
    )
    user.mealplan = {
        "meals": ["meal1", "meal2"],
        "nutrients": {
            "calories": 2000,
            "protein": 100,
            "fat": 70,
            "carbohydrates": 250,
        },
    }
    set_users_data.add_user(user)
    with client.session_transaction() as sess:
        sess["logged_in"] = True
        sess["username"] = "testusername"

    response = client.get("/recommendations/mealplanner/view")
    assert_200(response)
    assert b"meal" in response.data.lower()


def test_mealplanner_view_week(client, set_users_data):
    user = UserProfile(
        "testusername",
        "testpassword",
        "Test User",
        20,
        "Female",
        175.0,
        70.0,
        "medium",
        "The Netherlands",
        "None",
        "None",
    )
    user.mealplan = {"week": {"monday": [], "tuesday": []}}
    set_users_data.add_user(user)
    with client.session_transaction() as sess:
        sess["logged_in"] = True
        sess["username"] = "testusername"

    response = client.get("/recommendations/mealplanner/view")
    assert_200(response)
    assert b"monday" in response.data.lower()


def test_mealplanner_view_empty(client, set_users_data):
    user = UserProfile(
        "testusername",
        "testpassword",
        "Test User",
        20,
        "Female",
        175.0,
        70.0,
        "medium",
        "The Netherlands",
        "None",
        "None",
    )
    user.mealplan = None
    set_users_data.add_user(user)
    with client.session_transaction() as sess:
        sess["logged_in"] = True
        sess["username"] = "testusername"

    response = client.get("/recommendations/mealplanner/view")
    assert_200(response)
    assert b"no meal plan found" in response.data.lower()


def test_show_mealplan(client):
    """
    Tests if the saved mealplan page is loading correctly for a logged in user.
    """
    with client.session_transaction() as session:
        session["logged_in"] = True
        session["username"] = "testusername"
    response = client.get("/recommendations/mealplanner/view")
    assert_200(response)


###############################################################################
#                                                                             #
#                   HOME PAGE TEST                                            #
#                                                                             #
###############################################################################


def test_homepage(client):
    """
    Tests if the homepage is loading correctly for a logged in user.
    """
    with client.session_transaction() as session:
        session["logged_in"] = True
        session["username"] = "testusername"
    response = client.get("/home")
    assert_200(response)


def test_homepage_results_redirect(client):
    """
    Tests that entering symptoms on the homepage correctly redirects to the results page and redirects withiin 10 seconds
    """
    with client.session_transaction() as session:
        session["logged_in"] = True
        session["username"] = "testusername"

    start_time = time.time()
    response = client.post("/home", data={"symptoms": "acne"}, follow_redirects=False)
    duration = time.time() - start_time

    assert response.status_code == 302
    assert "/results?symptoms=acne" in response.headers["Location"]
    assert duration <= 10, f"redirect took too much time: {duration:.2f} seconds"

###############################################################################
#                                                                             #
#                        ANALYSIS RESULTS SAVING                              #
#                                                                             #
###############################################################################

def test_history_analysis(client):
    """
    Tests if the history page is loading correctly for a logged in user.
    """
    with client.session_transaction() as session:
        session["logged_in"] = True
        session["username"] = "testusername"
    response = client.get("/analysis_history")
    assert_200(response)


###############################################################################
#                                                                             #
#                        NUTRIENT PAGE TESTING                                #
#                                                                             #
###############################################################################


def test_getting_json_file():
    """
    Tests if the json file is loaded successfully
    """
    json_data = get_nutrient_info()
    print(json_data)
    assert json_data["IRON"]["symptoms"][0] == "fatigue"


def test_redirecting_nutrient_url(client):
    """
    Tests if redirecting works.
    """
    response = client.get(
        "/nutrient?nutrient=Vitamin+A", follow_redirects=False
    )  # false bc
    assert response.status_code == 302, f"Expected 302, got {response.status_code}"


def test_nutrient_info_page(client):
    """
    Tests if nutrient page can load successfully with the testcase.
    """
    response = client.get("/nutrient/zinc", follow_redirects=False)
    assert_200(response)


###############################################################################
#                                                                             #
#                        SEARCH BAR TESTING                                   #
#                                                                             #
###############################################################################


def test_search_redirecting(client):
    """
    tests if the search bar redirects successfully
    """
    response = client.get("/search", follow_redirects=False)  # false bc
    assert response.status_code == 302, f"Expected 302, got {response.status_code}"


def test_search_bar_info_page(client):
    """
    Tests if the search bar works successfully with the testcase.
    """
    response = client.get("/search_bar_result/zinc", follow_redirects=False)
    assert_200(response)


"""Run tests for the consent form"""
# test_show_consent()
# test_handle_consent()
# test_redirect_to_consent_when_no_consent()

"""Run tests of the authentication page (register and login)"""
# test_redirect_to_login_when_consent_and_not_logged_in()
# test_register_works_correctly()
# test_login_works_correctly()

"""Run tests of user profile and user data objects"""
# test_add_user_to_users_data()
# test_adding_user_with_existing_username()
# test_successful_user_authentication()
# test_wrong_password_user_authentication()
# test_wrong_username_user_authentication()

"""Run profile page tests"""
# test_profile_page()
# test_profile_page_change_info()

"""Run homepage tests"""
# test_logout()

"""Run tests for saving recipes to the user profile"""
# test_add_saving(client, set_users_data)
# test_remove_saving()
# test_save_results()
