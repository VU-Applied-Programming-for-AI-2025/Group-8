### first backend tests file ###

from context import app

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
    

def test_list_saving():
    client = app.test_client()
    response = client.get("/savings/1")
    assert_200(response)
    assert b"[]" in response.data
    
test_add_saving()
test_add_saving_duplicates()
test_remove_saving()
test_list_saving()
