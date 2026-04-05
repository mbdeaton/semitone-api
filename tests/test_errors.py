"""Tests for errors from the scales router."""

import unittest

from fastapi.testclient import TestClient
from semitone_api.main import app


class TestErrors(unittest.TestCase):
    """Tests for error replies from scales endpoints."""

    def setUp(self):
        self.client = TestClient(app)

    def test_invalid_scale_type(self):
        r = self.client.get("/scales/dorian/C")
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json()["error"], "invalid_scale_type")

    def test_invalid_root_note(self):
        r = self.client.get("/scales/major/Z9")
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json()["error"], "invalid_note")
