import json

import flask_unittest
from mock import patch
import flask.globals
from app import app


class TestRoutes(flask_unittest.ClientTestCase):
    app = app

    def test_index_returns_200(self, client):
        self.assertStatus(client.get("/index"), 200)

    def test_submit_endpoint(self, client):
        expected = '{"hello": "world", "survey_id": "009"}'
        client.post('/submit', data={'post-data': '{"hello": "world", "survey_id": "009"}'})
        # check result from server with expected data
        self.assertEqual(flask.request.form.get('post-data'), expected)


