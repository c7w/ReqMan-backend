from django.test import TestCase
from django.urls import resolve

import backend.views


class RoutingTests(TestCase):
    def test_root(self):
        """Test if path `/` is configurated normally"""
        resolver = resolve("/")
        self.assertEqual(resolver.func, backend.views.root)
