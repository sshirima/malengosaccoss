from django.test import TestCase

# Create your tests here.

# class TemplateTestCase(TestCase):
#     def setUp(self):
#         # Setup run before every test method.
#         pass

#     def tearDown(self):
#         # Clean up run after every test method.
#         pass

#     def test_something_that_will_pass(self):
#         self.assertFalse(False)

#     def test_something_that_will_fail(self):
#         self.assertTrue(False)
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

class MemberLoginTest(TestCase):

    def setUp(self):
        # Setup run before every test method.
        pass

    def tearDown(self):
        # Clean up run after every test method.
        pass

    def test_login_page(self):
        driver = webdriver.Chrome()
        
        driver.get('http://127.0.0.1:8000/authentication/login')

        field_username = driver.find_element_by_id('email')
        field_password = driver.find_element_by_id('password')
        btn_submit = driver.find_element_by_id('submit')

        field_username.send_keys('admin@localhost.com')
        field_password.send_keys('jimaya79')

        btn_submit.send_keys(Keys.RETURN)

        self.assertIn('Fails to authenticate username', driver.page_source)
