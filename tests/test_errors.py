"""Tests for errors from the scales router."""

import unittest

from fastapi.testclient import TestClient
from semitone_api.main import app


class TestErrors(unittest.TestCase):
    """Tests for error replies from scales endpoints."""

    def setUp(self):
        self.client = TestClient(app)

    def test_invalid_scale_type(self):
        r = self.client.get("/scales/dorian/c")
        self.assertEqual(r.status_code, 422)
        self.assertIn("detail", r.json())

    def test_invalid_root_note(self):
        r = self.client.get("/scales/major/h")
        self.assertEqual(r.status_code, 422)
        self.assertIn("detail", r.json())

    def test_invalid_root_spelling(self):
        r = self.client.get("/scales/major/bb")
        self.assertEqual(r.status_code, 422)
        self.assertIn("detail", r.json())
