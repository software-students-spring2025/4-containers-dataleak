"""testing for web app"""
# pylint: disable=redefined-outer-name
# pylint: disable=import-error

import pytest
from app import create_app

@pytest.fixture
def test_client():
    """
    Create and yield flask app
    """
    app = create_app()
    app.testing = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_user(test_client):
    """
    Create a user to test logged in routes
    """
    test_client.post("/register", data={
        "username": "mockuser1234",
        "password": "RandomPass22$$",
        "confirm_password": "RandomPass22$$"
    })

    test_client.post("/", data={
        "username": "mockuser1234",
        "password": "RandomPass22$$",
    })
    return test_client


def test_index(test_client):
    """
    Test index route of web page
    """
    response = test_client.get("/")
    html = response.data.decode("utf-8")
    assert response.status_code == 200
    assert "login to your account" in html

def test_register(test_client):
    """
    Test register route of web page
    """
    response = test_client.get("/register")
    html = response.data.decode("utf-8")
    assert response.status_code == 200
    assert "Create An Account" in html

def test_invalid_login(test_client):
    """
    Test login with invalid information
    """
    response = test_client.post("/", data={
        "username": "invalidusername1234",
        "password": "randompassword1234"
    })
    html = response.data.decode("utf-8")
    assert response.status_code == 200
    assert "User not found" in html

def test_login_wrong_password(test_client):
    """
    Test login page with wrong password
    """
    test_client.post("/register", data={
        "username": "mockuser1234",
        "password": "RandomPass22$$",
        "confirm_password": "RandomPass22$$"
    })
    response = test_client.post("/", data={
        "username": "mockuser1234",
        "password": "wrongpassword",
    }, follow_redirects=True)

    html = response.data.decode("utf-8")
    assert response.status_code == 200
    assert "Incorrect Password" in html


def test_invalid_register(test_client):
    """
    Test registration with invalid passwords
    """
    response = test_client.post("/register", data={
        "username": "invalidusername1234",
        "password": "randompassword1234",
        "confirm_password": "wrongpass"
    })
    html = response.data.decode("utf-8")
    assert response.status_code == 200
    assert "Passwords do not match" in html

def test_fridge(mock_user):
    """
    Test fridge route when logged in
    """
    response = mock_user.get("/fridge")
    html = response.data.decode("utf-8")
    assert response.status_code == 200
    assert "Virtual Fridge" in html

def test_add_food(mock_user):
    """
    Test adding a food route when logged in
    """
    response = mock_user.get("/add-food")
    html = response.data.decode("utf-8")
    assert response.status_code == 200
    assert "Scan Your Food" in html

def test_logout(mock_user):
    """
    Test logging user out
    """
    response = mock_user.get("/logout", follow_redirects=True)
    html = response.data.decode("utf-8")
    assert response.status_code == 200
    assert "login to your account" in html
