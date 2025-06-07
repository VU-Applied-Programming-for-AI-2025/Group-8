### first backend tests file ###

from context import app
import json

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
    
test_list_saving_empty() # list empty
test_add_saving() # add 1 recipe
test_add_saving_duplicates() # ignore adding the same recipe
test_list_saving() # return 1 recipe
test_remove_saving() # remove the existed recipe
test_remove_absent() # ignore removing because it's already removed
test_add_saving() # add 1 recipe
test_list_saving() # return 1 recipe
