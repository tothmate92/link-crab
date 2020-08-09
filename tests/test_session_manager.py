import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from session_manager import make_session
from exercise_url import exercise_url
from test_app import app
import pytest
from tests.test_app import mock_app

@pytest.fixture(scope='session')
def test_session():
    member_mockuser = {
        'login_url': 'http://127.0.0.1:5000/user/sign-in',
        'email': 'member@example.com',
        'password': 'Password1'
    }
    session = make_session(member_mockuser)
    return session

# These tests are highly dependent on the testapp.py
def test_access(test_session):
    assert exercise_url(test_session,'http://127.0.0.1:5000/members')[3] == True