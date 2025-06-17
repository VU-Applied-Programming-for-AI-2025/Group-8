### first backend tests file ###

import json, os, pytest
from context import app, UserProfile, UsersData
from app import app, users_data, home, analyze_symptoms, extract_food_recs, display_results, recipe_details
from unittest.mock import patch
from dotenv import load_dotenv

load_dotenv()

@pytest.fixture
def client():
    """
    Set up for a Flask test client.
    """
    app.config['TESTING'] = True
    client = app.test_client()
    yield client


@pytest.fixture
def set_users_data():
    """
    Set up of a UserData object with a test storage file.
    """
    # Sets a json file to store the test users data
    test_users_file = 'test_users.json'

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


def set_user_login(client):
    """
    Helper function to add a testuser to the database and login.
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
            "None"
        )

        # Saves the object to the user_data object
        users_data.add_user(user)

    # Makes sure the client is logged in for the session
    with client.session_transaction() as sess:
        sess["logged_in"] = True
        sess["username"] = "testusername"


def assert_200(response):
    """
    Helper function to assert that the response status code is 200.
    """
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"


###############################################################################
#                                                                             #
#                   CONSENT FORM PAGE TESTS                                   #
#                                                                             #
###############################################################################

def test_show_consent(client):
    """
    Tests that the consent form is displayed when the web is started.
    """
    response = client.get("/")
    assert_200(response)
    assert b"consent form" in response.data.lower()


def test_handle_consent(client):
    """
    Tests that submitting the consent form causes redirection to the authentication page.
    """
    response = client.post("/consentform", data={"accept": "true"}, follow_redirects=True)
    assert_200(response)
    assert b"login" in response.data.lower()


def test_redirect_to_consent_when_no_consent(client):
    """
    Tests that accessing the authentication page with no consent redirects to the consent form.
    """
    response = client.get("/auth", follow_redirects=True)
    assert_200(response)
    assert b"consent form" in response.data.lower()


###############################################################################
#                                                                             #
#                   LOGIN PAGE TESTS                                          #
#                                                                             #
###############################################################################

def test_login_works_correctly(client, set_users_data):
    """
    Tests that logging in with an existing user works correctly, redirects to home page.
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
            "None"
        )
    # Stores the user object in the user data.
    set_users_data.add_user(user)

    # Checks if the consentform has been accepted.
    client.post("/consentform", data={"accept": "true"}, follow_redirects=True)

    # Checks the response if the client logs in with their username and password.
    response = client.post("/auth/login", data={"name": "testusername", "password": "testpassword"}, follow_redirects=True)
    assert_200(response)
    assert b"homepage" in response.data.lower()


def test_login_with_false_user_fails(client, set_users_data):
    """
    Tests that logging in with an non-existing user will not redirect to home page and gives the correct error message.
    """

    # Checks if the consentform has been accepted.
    client.post("/consentform", data={"accept": "true"}, follow_redirects=True)

    # Checks if the correct error message is displayed if the client logs in with a false username and password.
    response = client.post("/auth/login", data={"name": "testusername", "password": "testpassword"}, follow_redirects=True)
    assert b"username not found in database" in response.data.lower()
    assert_200(response)

###############################################################################
#                                                                             #
#                   REGISTER PAGE TESTS                                       #
#                                                                             #
###############################################################################

def test_register_works_correctly(client, set_users_data):
    """
    Tests that registering a new user works correctly and redirects to the home page.
    """
    # Checks if the consentform has been accepted.
    client.post("/consentform", data={"accept": "true"}, follow_redirects=True)

    # Posts the register form with the information of a test user
    client.post("/auth/register", data={
        "username": "testuser",
        "password": "testpassword",
        "name": "Test User",
        "age": 25,
        "sex": "Female",
        "hight": 170.0,
        "weight": 60.0,
        "skin_color": "medium",
        "country": "The Netherlands",
        "medication": "",
        "diet": "None",
        "existing_conditions": "",
        "allergies": ""}, follow_redirects=True)
    
    # Checks if the testuser's data is stored in the test users data file.
    assert "testuser" in set_users_data.users

    # Checks if the redirect to the homepages succeded
    response = client.get("/home", follow_redirects=True)
    assert_200(response)
    assert b"homepage" in response.data.lower()


def test_register_with_missing_password_fails(client, set_users_data):
    """
    Tests that registering a new user with missing information of a mandatory part such as password gives the corresponding error message.
    """
    # Checks if the consentform has been accepted.
    client.post("/consentform", data={"accept": "true"}, follow_redirects=True)

    # Posts the users information to the register form without a password
    response = client.post("/auth/register", data={
        "username": "testuser",
        "name": "Test User",
        "age": 25,
        "sex": "Female",
        "hight": 170.0,
        "weight": 60.0,
        "skin_color": "medium",
        "country": "The Netherlands",
        "medication": "",
        "diet": "None",
        "existing_conditions": "",
        "allergies": ""}, follow_redirects=True)
    
    # Checks if the user's data has not been stored as a userprofile object.
    assert "testuser" not in set_users_data.users

    # Checks if the correct errormessage is displayed.
    assert b"password is required" in response.data.lower()
    assert_200(response)




# def test_register_with_existing_username_fails(client, set_users_data):
#     """
#     Tests that when the user tried to register with an already existing username, it raises an ValueError.
#     """

#     # Creates a user profile to directly add to the users data.
#     user = UserProfile(
#         "Hansklok",
#         "testpassword2",
#         "Test User 2",
#         25,
#         "Male",
#         1.80,
#         80,
#         "light",
#         "Germany",
#         "None",
#         "None"
#     )
#     # Adds the user to the users data test file.
#     set_users_data.add_user(user)

#     # Checks if the consentform has been accepted.
#     client.post("/consentform", data={"accept": "true"}, follow_redirects=True)

#     # Posts the users information to the register form with an existing username.
#     response = client.post("/auth/register", data={
#         "username": "Hansklok",
#         "name": "Test User",
#         "age": 25,
#         "sex": "Female",
#         "hight": 170,
#         "weight": 60,
#         "skin_color": "medium",
#         "country": "The Netherlands",
#         "medication": "",
#         "diet": "None",
#         "existing_conditions": "",
#         "allergies": ""}, follow_redirects=True)
    
#     # Checks if the user's data has not been stored as a userprofile object.
#     assert "testuser" not in set_users_data.users

#     # Checks if the correct errormessage is displayed.
#     assert b"already exists" in response.data.lower()
#     assert_200(response)
    


###############################################################################
#                                                                             #
#                   LOGOUT PAGE TESTS                                         #
#                                                                             #
###############################################################################

def test_logout(client):
    """
    Tests that when logging out the session is cleared and the user will be redirected to the consent form.
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


def test_profile_page(client):
    """
    Tests that the profile page can be accessed when the user is logged in.
    """
    set_user_login(client)
    response = client.get("/profile")
    assert_200(response)
    assert b"Profile" in response.data


def test_profile_page_change_age(client, set_users_data):
    """
    Tests that when the user changes their age on the profile page, it will be changed in the user data object.
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
        "None"
    )
    set_users_data.add_user(user)

    # Logges in the user
    with client.session_transaction() as session:
        session["logged_in"] = True
        session["username"] = "agetestuser"

    # Changes the user;s age on the profile page form.
    response = client.post("/profile", data={
            "name": "Test User",
            "age": 19, # Age changed to 19
            "sex": "Female",
            "hight": 175.0,
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


def test_profile_leave_blank_password_fails(client, set_users_data):
    """
    Tests a user profile change where a required userprofile parameter such as password is left blank to check if an error will occur and the password is not saved in the database.
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
        "None"
    )

    # Saves the user profile object to the user data.
    set_users_data.add_user(user)

    # Log in the user
    with client.session_transaction() as session:
        session["logged_in"] = True
        session["username"] = "testusername"

    # Submits a form on the profile page to update the users information.
    response = client.post("/profile", data={
            "name": "Test User",
            "age": 19, 
            "sex": "Female",
            "hight": 175.0,
            "weight": 70.0,
            "skin_color": "medium",
            "country": "The Netherlands",
            "medication": "",
            "diet": "None",
            "existing_conditions": "",
            "allergies": "",
            "password": "", # Leaves the password empty
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
#                   HOME PAGE TEST                                            #
#                                                                             #
###############################################################################

def test_extract_food_recs_list():
    """
    Tests if the extract_food_recs function returns a correcly extracted list of foods from the groq ai analysis response.
    """
    test_response = (" - Foods: almonds, dairy, strawberries\n"
    "- Foods: carrots, red meat, apple"
    )

    with patch("app.analyze_symptoms", return_value = test_response):
        result = extract_food_recs()
        assert set(result) == {"almonds", "dairy", "strawberries", "carrots", "red meat", "apple"}

def test_display_results(client):
    """
    Tests if the display_results function and /results route correctly display groq ai's response as in the prompt, so explanation, foods and a tip.
    """
    test_response = (
        "Vitamin A\n"
        "- Why: acne\n"
        "- Foods: carrot, eggs\n"
        "- Tip: foods rich in vitamin A"
    )
    with patch("app.analyze_symptoms", return_value = test_response):

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
        test_get.return_value.json.return_value = {"title": "test recipe", "ingredients": "a, b, c", "nutrition": "A, B, C", "instructions": "step1"}
        response = client.get("/recipe/12345")
        assert_200(response)
        assert b"test recipe" in response.data
    



# def test_add_saving():
#     """
#     Tests whether recipe is succesfully saved to the profile.
#     Tests whether the duplicate saving will throw an error.
#     """
#     # print("it works!")
#     client = app.test_client()
#     set_user(client)
#     with client.session_transaction() as session:
#         session["logged_in"] = True
#         session["username"] = "testusername"

#     users_data.get_user("testusername").saved_recipes = []

#     response = response = client.post("/save_favorite/4")
#     assert_200(response)
#     assert b"OK" in response.data

#     response2 = client.post("/save_favorite/4")
#     assert response2.status_code == 401
#     assert b"Already saved" in response2.data


# def test_remove_saving():
#     """
#     Tests whether recipe is succesfully removed from the profile.
#     Tests whether trying to remove the not existed recipe will throw an error.
#     """
#     # print("it works!")
#     client = app.test_client()
#     set_user(client)
#     with client.session_transaction() as session:
#         session["logged_in"] = True
#         session["username"] = "testusername"

#     users_data.get_user("testusername").saved_recipes = []

#     response = response = client.post("/save_favorite/4")
#     assert_200(response)
#     assert b"OK" in response.data

#     response2 = client.post("/remove_favorite/4")
#     assert_200(response)
#     assert b"OK" in response2.data

#     response2 = client.post("/remove_favorite/4")
#     assert response2.status_code == 401
#     assert b"Not exists" in response2.data


# def test_save_results():
#     """
#     Tests whether results are succesfully saved to the profile.
#     Tests whether trying to save "None" result will throw an error.
#     """
#     client = app.test_client()
#     set_user(client)
#     with client.session_transaction() as session:
#         session["logged_in"] = True
#         session["username"] = "testusername"

#     users_data.get_user("testusername").analysis_results = {}

#     response_empty = client.post(
#         "/save_results", data="", content_type="application/json"
#     )
#     assert response_empty.status_code == 401
#     assert b"No result" in response_empty.data

#     test_data = {"Vitamin A": 45, "Iron": 20}

#     response = client.post(
#         "/save_results", data=json.dumps(test_data), content_type="application/json"
#     )
#     assert_200(response)
#     assert b"OK" in response.data



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
# test_add_saving()
# test_remove_saving()
# test_save_results()
