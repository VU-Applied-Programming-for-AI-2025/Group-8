### first backend tests file ###

import json
from context import app, UserProfile, UsersData

def assert_200(response):
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

def test_add_saving():
    client = app.test_client()
    response = client.post("/savings/1/101")
    assert_200(response)
    assert b"OK" in response.data

def test_add_saving_duplicates():
    client = app.test_client()
    response = client.post("/savings/1/101")
    assert_200(response)
    assert b"already exist" in response.data
    

def test_remove_saving():
    client = app.test_client()
    # and removing
    response = client.delete("/savings/1/101")
    assert_200(response)
    assert b"OK" in response.data
    

def test_list_saving_empty():
    client = app.test_client()
    response = client.get("/savings/1")
    assert_200(response)
    assert b"[]" in response.data
    
def test_remove_absent():
    client = app.test_client()
    #print(client.get("/savings/1").data)
    response = client.delete("/savings/1/101")
    assert_200(response)
    #print(response.data)
    assert b"not exist" in response.data

def test_list_saving():
    client = app.test_client()
    response = client.get("/savings/1")
    assert_200(response)
    savingList = json.loads(response.data)
    assert 101 == savingList[0]["id"]

def assert_ok(response):
    """
    Helper function to assert that the response status code is 200.
    """
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

client = app.test_client()

# Consent form tests

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


def test_register_works_correctly():
    """
    Tests that registering a new user works correctly and redirects to the home page. 
    """
    with app.test_client() as client:
        client.post("/consentform", data={"accept": "true"}, follow_redirects=True)
        client.post("/auth/register", data={
            "username": "testuser",
            "password": "testpassword",
            "name": "Test User",
            "age": "25",
            "sex": "Female",
            "hight": "170",
            "weight": "60",
            "skin_color": "medium",
            "country": "The Netherlands",
            "medication": "",
            "diet": "",
            "existing_conditions": "",
            "allergies": ""}, follow_redirects=True)
        response = client.get("/home", follow_redirects=True)
        assert_ok(response) 

# User profile objects and users data object tests

def test_add_user_to_users_data():
    """
    Tests that the add_user function works correctly by adding a UserProfile object to the UsersData object.
    """
    user = UserProfile('testusername', 'testpassword', 'Test User', '20', 'Female', '1.75', '70', 'medium', 'The Netherlands')
    users_data = UsersData()
    users_data.add_user(user)
    assert user.username in users_data.users

def test_adding_user_with_existing_username():
    """
    Tests that the add_user function works correctly when trying to add a user with an existing username. Which should raise a ValueError.
    """
    user_1 = UserProfile('Hansklok', 'testpassword', 'Test User', '20', 'Female', '1.75', '70', 'medium', 'The Netherlands')
    user_2 = UserProfile('Hansklok', 'testpassword2', 'Test User 2', '25', 'Male', '1.80', '80', 'light', 'Germany')
    users_data = UsersData()
    users_data.add_user(user_1)
    try:
        users_data.add_user(user_2)
        assert False, "Expected ValueError for existing username"
    except ValueError as e:
        assert True

def test_successful_user_authentication():
    """
    Tests a successful authentication with the user_authentication function by checking if the provided username and password match the stored ones.
    """
    user = UserProfile('testusername', 'testpassword', 'Test User', '20', 'Female', '1.75', '70', 'medium', 'The Netherlands')
    users_data = UsersData()
    users_data.add_user(user)
    assert users_data.user_authentication('testusername', 'testpassword') == (True, 'Authentication successful')

def test_wrong_password_user_authentication():
    """
    Tests a unsuccessful authentication with the user_authentication function by checking if the provided username and wrong password match the stored ones.
    """
    user = UserProfile('testusername', 'testpassword', 'Test User', '20', 'Female', '1.75', '70', 'medium', 'The Netherlands')
    users_data = UsersData()
    users_data.add_user(user)
    assert users_data.user_authentication('testusername', 'wrongpassword') == (False, "Wrong password")

def test_wrong_username_user_authentication():
    """
    Tests a unsuccessful authentication with the user_authentication function by checking if the provided wrong username and password match the stored ones.
    """
    user = UserProfile('testusername', 'testpassword', 'Test User', '20', 'Female', '1.75', '70', 'medium', 'The Netherlands')
    users_data = UsersData()
    users_data.add_user(user)
    assert users_data.user_authentication('wrongusername', 'testpassword') == (False, 'Username not found in database')



# Run tests of the consent form
test_show_consent()
test_handle_consent()
test_redirect_to_consent_when_no_consent()
test_redirect_to_login_when_consent_and_not_logged_in()
test_register_works_correctly()
test_add_user_to_users_data()
test_adding_user_with_existing_username()
test_successful_user_authentication()
test_wrong_password_user_authentication()
test_wrong_username_user_authentication()

test_list_saving_empty() # list empty
test_add_saving() # add 1 recipe
test_add_saving_duplicates() # ignore adding the same recipe
test_list_saving() # return 1 recipe
test_remove_saving() # remove the existed recipe
test_remove_absent() # ignore removing because it's already removed
test_add_saving() # add 1 recipe
test_list_saving() # return 1 recipe

