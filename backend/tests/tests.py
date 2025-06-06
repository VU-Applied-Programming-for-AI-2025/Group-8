### first backend tests file ###
from context import app


def assert_ok(response):
    """
    Helper function to assert that the response status code is 200 (OK).
    """
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"



# Consent form tests

def test_show_consentform():
    """
    Tests that the consent form is displayed correctly.
    """
    client = app.test_client()
    response = client.get("/")
    assert_ok(response)
    assert b"consent form" in response.data.lower()

def test_submit_consentform():
    """
    Tests that submitting the consent form redirects to the authentication page.
    """
    client = app.test_client()
    response = client.post("/consentform", data={"accept": "true"}, follow_redirects=True)
    assert_ok(response)
    assert b"login" in response.data.lower()

def test_access_auth_without_consent():
    """
    Tests that access to the authentication page is denied without consent.
    """
    client = app.test_client()
    response = client.get("/auth")
    assert response.status_code == 403, f"Expected 403, got {response.status_code}"
    assert b"access denied" in response.data.lower()


# Run tests of the consent form
test_show_consentform()
test_submit_consentform()
test_access_auth_without_consent()



# Authentication page tests

