from django.test import TestCase
from django.urls import reverse
# Create your tests here.
class TestPage(TestCase):
    def test_home_page_works(self):
        response= self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/home.html')
        self.assertContains(response, 'BookTime')
    def test_about_us_page_works(self):
        response = self.client.get(reverse("about_us"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/about_us.html')
        self.assertContains(response, 'BookTime')    