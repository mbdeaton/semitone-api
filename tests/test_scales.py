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
        r = self.client.get("/scales/major/c")
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertEqual(body["scale_type"], "major")
        self.assertEqual(body["root"], "C")
        self.assertGreater(len(body["tones"]), 0)

    def test_minor_scale_a(self):
        r = self.client.get("/scales/minor/a")
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertEqual(body["scale_type"], "minor")
        self.assertEqual(body["root"], "A")
        self.assertGreater(len(body["tones"]), 0)

    def test_chromatic_scale_c(self):
        r = self.client.get("/scales/chromatic/c")
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertEqual(body["scale_type"], "chromatic")
        self.assertEqual(body["root"], "C")
        self.assertGreater(len(body["tones"]), 0)

    def test_diatonic_mode_ionian(self):
        r = self.client.get("/scales/diatonic-mode/1/c")
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertEqual(body["scale_type"], "diatonic-mode")
        self.assertEqual(body["root"], "C")
        self.assertGreater(len(body["tones"]), 0)

    def test_diatonic_mode_dorian(self):
        r = self.client.get("/scales/diatonic-mode/2/d")
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertEqual(body["scale_type"], "diatonic-mode")
        self.assertEqual(body["root"], "D")
        self.assertGreater(len(body["tones"]), 0)

    def test_diatonic_mode_invalid(self):
        r = self.client.get("/scales/diatonic-mode/0/c")
        self.assertEqual(r.status_code, 400)

    def test_harmonic_octave(self):
        r = self.client.get("/scales/harmonic-octave/12/c")
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertEqual(body["scale_type"], "harmonic-octave")
        self.assertEqual(body["root"], "C")
        self.assertGreater(len(body["tones"]), 0)

    def test_harmonic_series(self):
        r = self.client.get("/scales/harmonic-series/12/c")
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertEqual(body["scale_type"], "harmonic-series")
        self.assertEqual(body["root"], "C")
        self.assertGreater(len(body["tones"]), 0)
