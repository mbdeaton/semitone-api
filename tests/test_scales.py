"""Tests for the scales router."""

import unittest

from fastapi.testclient import TestClient

from semitone_api.main import app


class TestHealth(unittest.TestCase):
    """Tests for the health check endpoint."""
    def setUp(self):
        self.client = TestClient(app)

    def test_health(self):
        r = self.client.get("/health")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {"status": "ok"})


class TestScales(unittest.TestCase):
    """Tests for the scales endpoints."""
    def setUp(self):
        self.client = TestClient(app)

    def test_major_scale_c(self):
        r = self.client.get("/scales/major/C")
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertEqual(body["scale_type"], "major")
        self.assertEqual(body["root"], "C")
        self.assertGreater(len(body["tones"]), 0)

    def test_minor_scale_a(self):
        r = self.client.get("/scales/minor/A")
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertEqual(body["scale_type"], "minor")
        self.assertEqual(body["root"], "A")
        self.assertGreater(len(body["tones"]), 0)

    def test_invalid_scale_type(self):
        r = self.client.get("/scales/dorian/C")
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json()["error"], "invalid_scale_type")

    def test_invalid_root_note(self):
        r = self.client.get("/scales/major/Z9")
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json()["error"], "invalid_note")
