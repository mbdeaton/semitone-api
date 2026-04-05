"""Tests for the scales router, root spellings."""

import unittest

from fastapi.testclient import TestClient
from semitone_api.main import app


class TestRootSpelling(unittest.TestCase):
    """Tests scales endpoint root note spellings."""

    def setUp(self):
        self.client = TestClient(app)

    def test_major_scale_d(self):
        r = self.client.get("/scales/major/d")
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertEqual(body["root"], "D")

    def test_major_scale_d_sharp(self):
        r = self.client.get("/scales/major/Dsharp")
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertEqual(body["root"], "D#")

    def test_minor_scale_d_flat(self):
        r = self.client.get("/scales/minor/Dflat")
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertEqual(body["root"], "Db")

    def test_minor_scale_uppercase_dflat(self):
        r = self.client.get("/scales/minor/DFLAT")
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertEqual(body["root"], "Db")
