### first backend tests file ###

import json
from context import app, UserProfile, UsersData
from app import app, users_data
from user_data.user_profile import UserProfile
import os

def assert_ok(response):
    """
    Helper function to assert that the response status code is 200.
    """
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

client = app.test_client()

def set_user(client):
    if "testusername" not in users_data.users:
        user = UserProfile(
            'testusername', 'testpassword', 'Test User', 20, 'Female',
            1.75, 70, 'medium', 'The Netherlands'
        )
        users_data.add_user(user)
    
    with client.session_transaction() as sess:
        sess["logged_in"] = True
        sess["username"] = 'testusername'
        
def assert_200(response):
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

def test_add_saving():
    client = app.test_client()
    set_user(client)
    response = client.post("/save_favorite/140")
    assert_200(response)
    assert b"OK" in response.data

def test_add_saving_duplicates():
    client = app.test_client()
    set_user(client)
    response = client.post("/save_favorite/140")
    assert_200(response)
    assert b"already exist" in response.data
    

def test_remove_saving():
    client = app.test_client()
    # and removing
    set_user(client)
    response = client.delete("/remove_favorite/140")
    assert_200(response)
    assert b"OK" in response.data
    

def test_list_saving_empty():
    client = app.test_client()
    set_user(client)
    response = client.get("/show_favorites")
    assert_200(response)
    assert b"[]" in response.data
    
def test_remove_absent():
    client = app.test_client()
    set_user(client)
    #print(client.get("/savings/1").data)
    response = client.delete("/remove_favorite/140")
    assert_200(response)
    #print(response.data)
    assert b"not exist" in response.data

def test_list_saving():
    client = app.test_client()
    response = client.get("/savings")
    assert_200(response)
    savingList = json.loads(response.data)
    assert 140 == savingList[0]
    
def test_save_results():
    client = app.test_client()
    set_user(client)
    TestResults = {"Zink": 70,
                   "Iron": 40,
                   "Vitamin A": 20}
    
    response = client.post("/save_results", data = json.dumps(TestResults),content_type="application/json")
    
    assert_200(response)
    assert b"OK" in response.data
    
    
def test_visualization():
    client = app.test_client()
    set_user(client)
    
    response = client.post("/result_visualization", data = json.dumps({}),content_type="application/json")
    
    assert_200(response)
    #print(response.data)
    result = json.loads(response.data)
    assert "High" in result["Zink"]
    assert "Low" in result["Vitamin A"]
    assert "Medium" in result["Iron"]
    


# Consent form page tests

def test_show_consent():
    """
    Tests that the consent form is displayed when the web is started.
    """
    response = client.get("/")
    assert_ok(response)
    assert b"consent form" in response.data.lower()

def test_handle_consent():
    """
    Tests that submitting the consent form causes redirection to the authentication page.
    """
    response = client.post("/consentform", data={"accept": "true"}, follow_redirects=True)
    assert_ok(response)
    assert b"login" in response.data.lower()

def test_redirect_to_consent_when_no_consent():
    """
    Tests that accessing the authentication page with no consent redirects to the consent form,
    and if consent is given, redirects to login or home depending on login status.
    """
    with app.test_client() as client:
        response = client.get("/auth", follow_redirects=True)
        assert_ok(response)
        assert b"consent form" in response.data.lower()

# Authentication page tests

def test_redirect_to_login_when_consent_and_not_logged_in():
    """
    Tests that accessing the authentication page a consent and without being loggged in will redirect to the login page.
    """
    with app.test_client() as client:
        client.post("/consentform", data={"accept": "true"}, follow_redirects=True)
        response = client.get("/auth", follow_redirects=True)
        assert_ok(response)
        assert b"login" in response.data.lower()


# def test_register_works_correctly():
#     """
#     Tests that registering a new user works correctly and redirects to the home page. 
#     """
#     with app.test_client() as client:
#         client.post("/consentform", data={"accept": "true"}, follow_redirects=True)
#         client.post("/auth/register", data={
#             "username": "testuser",
#             "password": "testpassword",
#             "name": "Test User",
#             "age": 25,
#             "sex": "Female",
#             "hight": 170,
#             "weight": 60,
#             "skin_color": "medium",
#             "country": "The Netherlands",
#             "medication": "",
#             "diet": "None",
#             "existing_conditions": "",
#             "allergies": ""}, follow_redirects=True)
#         response = client.get("/home", follow_redirects=True)
#         assert 'testuser' in 
#         assert_ok(response) 

def test_login_works_correctly():
    """
    Tests that logging in with an existing user works correctly, redirects to home page.
    """
    with app.test_client() as client:
        client.post("/consentform", data={"accept": "true"}, follow_redirects=True)
        client.post("/auth/login", data={
            "username": "testuser",
            "password": "testpassword"}, follow_redirects=True)

# User profile objects and users data object tests

def test_add_user_to_users_data():
    """
    Tests that the add_user function works correctly by adding a UserProfile object to the UsersData object.
    """
    test_users_data_path = 'test_users.json'
    if os.path.exists(test_users_data_path):
        os.remove(test_users_data_path)
    user = UserProfile('testusername', 'testpassword', 'Test User', 20, 'Female', 1.75, 70, 'medium', 'The Netherlands')
    users_data = UsersData(test_users_data_path)
    users_data.add_user(user)
    assert user.username in users_data.users
    if os.path.exists(test_users_data_path):
        os.remove(test_users_data_path)

def test_adding_user_with_existing_username():
    """
    Tests that the add_user function works correctly when trying to add a user with an existing username. Which should raise a ValueError.
    """
    test_users_data_path = 'test_users.json'
    if os.path.exists(test_users_data_path):
        os.remove(test_users_data_path)
    user_1 = UserProfile('Hansklok', 'testpassword', 'Test User', 20, 'Female', 1.75, 70, 'medium', 'The Netherlands')
    user_2 = UserProfile('Hansklok', 'testpassword2', 'Test User 2', 25, 'Male', 1.80, 80, 'light', 'Germany')
    users_data = UsersData(test_users_data_path)
    users_data.add_user(user_1)
    try:
        users_data.add_user(user_2)
        assert False, "Expected ValueError for existing username"
    except ValueError as e:
        assert True
    finally:
        if os.path.exists(test_users_data_path):
            os.remove(test_users_data_path)

def test_successful_user_authentication():
    """
    Tests a successful authentication with the user_authentication function by checking if the provided username and password match the stored ones.
    """
    test_users_data_path = 'test_users.json'
    if os.path.exists(test_users_data_path):
        os.remove(test_users_data_path)
    user = UserProfile('testusername', 'testpassword', 'Test User', 20, 'Female', 1.75, 70, 'medium', 'The Netherlands')
    users_data = UsersData(test_users_data_path)
    users_data.add_user(user)
    assert users_data.user_authentication('testusername', 'testpassword') == (True, 'Authentication successful')
    if os.path.exists(test_users_data_path):
        os.remove(test_users_data_path)

def test_wrong_password_user_authentication():
    """
    Tests a unsuccessful authentication with the user_authentication function by checking if the provided username and wrong password match the stored ones.
    """
    test_users_data_path = 'test_users.json'
    if os.path.exists(test_users_data_path):
        os.remove(test_users_data_path)
    user = UserProfile('testusername', 'testpassword', 'Test User', 20, 'Female', 1.75, 70, 'medium', 'The Netherlands')
    users_data = UsersData(test_users_data_path)
    users_data.add_user(user)
    assert users_data.user_authentication('testusername', 'wrongpassword') == (False, "Wrong password")
    if os.path.exists(test_users_data_path):
        os.remove(test_users_data_path)

def test_wrong_username_user_authentication():
    """
    Tests a unsuccessful authentication with the user_authentication function by checking if the provided wrong username and password match the stored ones.
    """
    test_users_data_path = 'test_users.json'
    if os.path.exists(test_users_data_path):
        os.remove(test_users_data_path)
    user = UserProfile('testusername', 'testpassword', 'Test User', 20, 'Female', 1.75, 70, 'medium', 'The Netherlands')
    users_data = UsersData(test_users_data_path)
    users_data.add_user(user)
    assert users_data.user_authentication('wrongusername', 'testpassword') == (False, 'Username not found in database')
    if os.path.exists(test_users_data_path):
        os.remove(test_users_data_path)

# Profile page tests

def test_profile_page():
    """
    Tests that the profile page is shown when the user is logged in.
    """
    client = app.test_client()
    set_user(client)
    with client.session_transaction() as session:
        session["logged_in"] = True
        session["username"] = 'test'
    response = client.get("/profile")
    assert_ok(response)
    assert b"Profile" in response.data
    

def test_profile_page_change_info():
    """
    Tests that when the user changes their age on the profile page, it will be changed in the user data object.
    """
    test_users_data_path = 'backend/tests/test_users.json'
    if os.path.exists(test_users_data_path):
        os.remove(test_users_data_path)
    client = app.test_client()
    user = UserProfile('agetestuser', 'testpassword', 'Test User', 18, 'Female', 1.75, 70, 'medium', 'The Netherlands')
    users_data = UsersData(test_users_data_path)
    users_data.add_user(user)
    response = client.post("/profile", data={
        "name": "Test User",
        "age": 19,
        "sex": "Female",
        "hight": 1.75,
        "weight": 70,
        "skin_color": "medium",
        "country": "The Netherlands",
        "medication": "",
        "diet": "None",
        "existing_conditions": "",
        "allergies": "",
        "password": "testpassword"
    }, follow_redirects=True)
    assert response.status_code == 200
    updated_user = users_data.get_user('agetestuser')
    assert updated_user.age == 19
    if os.path.exists(test_users_data_path):
        os.remove(test_users_data_path)

def test_logout():
    """
    Tests that when logging out the session is cleared and the user will be redirected to the home page.
    """
    client = app.test_client()
    set_user(client)
    with client.session_transaction() as session:
        session["logged_in"] = True
        session["username"] = 'testusername'
    response = client.get("/logout", follow_redirects=True)
    assert_ok(response)
    with client.session_transaction() as session:
        assert "logged_in" not in session
        assert "username" not in session


"""Run tests for the consent form"""
test_show_consent()
test_handle_consent()
test_redirect_to_consent_when_no_consent()

"""Run tests of the authentication page (register and login)"""
test_redirect_to_login_when_consent_and_not_logged_in()
# test_register_works_correctly()
test_login_works_correctly()

"""Run tests of user profile and user data objects"""
test_add_user_to_users_data()
test_adding_user_with_existing_username()
test_successful_user_authentication()
test_wrong_password_user_authentication()
test_wrong_username_user_authentication()

"""Run profile page tests"""
test_profile_page()
# test_profile_page_change_info()

"""Run homepage tests"""
test_logout()


# test_list_saving_empty() # list empty
# test_add_saving() # add 1 recipe
# test_add_saving_duplicates() # ignore adding the same recipe
# #test_list_saving() # return 1 recipe
# test_remove_saving() # remove the existed recipe
# test_remove_absent() # ignore removing because it's already removed
# test_add_saving() # add 1 recipe
# #test_list_saving() # return 1 recipe
# test_save_results()
# test_visualization()

