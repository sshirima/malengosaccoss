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
from selenium.webdriver.support.ui import Select
import factory
import random
from factory.faker import faker
import factory.fuzzy as factory_fuzzy

class MemberLoginTest(TestCase):
    fake_email = faker.Faker().email()
    fake_gender_choice = random.randint(0, 1)
    fake_gender = ['male', 'female'][fake_gender_choice]
    fake_first_name = faker.Faker().first_name_male() if fake_gender == 'male' else faker.Faker().first_name_female()
    fake_middle_name = faker.Faker().first_name_male()
    fake_last_name = faker.Faker().last_name()
    fake_mobile_number = faker.Faker().msisdn()
    activation_url = ''
    

    def setUp(self):
        # Setup run before every test method.
        pass

    def tearDown(self):
        # Clean up run after every test method.
        pass

    # def test_member_registration_success(self):
        

    #     register.send_keys(Keys.RETURN)
    #     self.assertIn('Account created successful', driver.page_source)

    def test_0001_register_member_success(self):
        driver = webdriver.Chrome()
        driver.get('http://127.0.0.1:8000/authentication/register')
        email = driver.find_element_by_name('email')
        password1 = driver.find_element_by_name('password1')
        password2 = driver.find_element_by_name('password2')
        gender = driver.find_element_by_name('gender')
        mobile_number = driver.find_element_by_name('mobile_number')
        first_name = driver.find_element_by_name('first_name')
        middle_name = driver.find_element_by_name('middle_name')
        last_name = driver.find_element_by_name('last_name')
        register = driver.find_element_by_id('submit')
        select_gender = Select(gender)

        email.send_keys(self.fake_email)
        password1.send_keys('Changeme_123')
        password2.send_keys('Changeme_123')
        select_gender.select_by_value(self.fake_gender)
        mobile_number.send_keys(self.fake_mobile_number)
        first_name.send_keys(self.fake_first_name)
        middle_name.send_keys(self.fake_middle_name)
        last_name.send_keys(self.fake_last_name)
        register.send_keys(Keys.RETURN)

        self.assertIn('Account created successful', driver.page_source)

    def test_0002_register_member_fail_password_mismatch(self):
        driver = webdriver.Chrome()
        driver.get('http://127.0.0.1:8000/authentication/register')

        email = driver.find_element_by_name('email')
        password1 = driver.find_element_by_name('password1')
        password2 = driver.find_element_by_name('password2')
        gender = driver.find_element_by_name('gender')
        mobile_number = driver.find_element_by_name('mobile_number')
        first_name = driver.find_element_by_name('first_name')
        middle_name = driver.find_element_by_name('middle_name')
        last_name = driver.find_element_by_name('last_name')
        register = driver.find_element_by_id('submit')

        fake_email = faker.Faker().email()
        fake_gender_choice = random.randint(0, 1)
        fake_gender = ['male', 'female'][fake_gender_choice]
        fake_first_name = faker.Faker().first_name_male() if fake_gender == 'male' else faker.Faker().first_name_female()
        fake_middle_name = faker.Faker().first_name_male()
        fake_last_name = faker.Faker().last_name()
        fake_mobile_number = faker.Faker().msisdn()
        select_gender = Select(gender)

        email.send_keys(fake_email)
        password1.send_keys('Changeme_')
        password2.send_keys('Changeme_123')
        select_gender.select_by_value(fake_gender)
        mobile_number.send_keys(fake_mobile_number)
        first_name.send_keys(fake_first_name)
        middle_name.send_keys(fake_middle_name)
        last_name.send_keys(fake_last_name)

        register.send_keys(Keys.RETURN)
        self.assertIn('Password confirmation - The two password fields didn’t match', driver.page_source)


    def test_0003_sending_activation_link_success(self):
        
        driver = self.login_member('admin@localhost.com', 'jimaya792')
        self.assertIn('Dashboard', driver.page_source)
        #Go to members list
        driver.get('http://127.0.0.1:8000/members/members?name='+self.fake_first_name)
        self.assertIn('Members', driver.page_source)

        #Go to member details
        select_member = driver.find_element_by_link_text('{} {} {}'.format(self.fake_first_name, self.fake_middle_name, self.fake_last_name))
        select_member.click()
        self.assertIn('Member details', driver.page_source)

        #Send activation link to member
        send_activation_link = driver.find_element_by_id('send_activation_link')
        send_activation_link.click()
        self.assertIn('Account activation has been sent to:', driver.page_source)

    
        #Activate email with link
        alert_info = driver.find_element_by_class_name('activation_url')
        url_text = alert_info.text
        url_text = url_text.partition('http')[2]
        url_text = '{}{}'.format('http', url_text)
    #     self.activation_url = url_text

    #     #Activate Account
    # def test_0004_activating_member_account_success(self):
    #     driver = webdriver.Chrome()
        # print(self.activation_url)
        driver.get(url_text)
        self.assertIn('Account activated successfully', driver.page_source)
    
    def test_0005_change_member_password_success(self):
        driver = self.login_member(self.fake_email, 'Changeme_123')
        self.assertIn('Dashboard', driver.page_source)

        #Test profile
        driver.get('http://127.0.0.1:8000/authentication/user-profile')
        self.assertIn('User profile', driver.page_source)

        change_password = driver.find_element_by_id('change_password')
        change_password.click()
        self.assertIn('Change password', driver.page_source)

        old_password = driver.find_element_by_name('old_password')
        new_password1 = driver.find_element_by_name('new_password1')
        new_password2 = driver.find_element_by_name('new_password2')
        submit = driver.find_element_by_id('submit')

        old_password.send_keys('Changeme_123')
        new_password1.send_keys('Chagepass_123')
        new_password2.send_keys('Chagepass_123')
        submit.send_keys(Keys.RETURN)
        self.assertIn('Dashboard', driver.page_source)

    

    def test_0006_change_member_profile_success(self):
        driver = self.login_member(self.fake_email, 'Chagepass_123')
        self.assertIn('Dashboard', driver.page_source)

        driver.get('http://127.0.0.1:8000/authentication/user-profile-update')
        self.assertIn('User profile', driver.page_source)
        first_name = driver.find_element_by_name('first_name')
        middle_name = driver.find_element_by_name('middle_name')
        last_name = driver.find_element_by_name('last_name')
        mobile_number = driver.find_element_by_name('mobile_number')
        submit = driver.find_element_by_id('submit')

        first_name.send_keys('Joe')
        last_name.send_keys('Sam')
        middle_name.send_keys('David')
        mobile_number.send_keys('')

        submit.send_keys(Keys.RETURN)
        self.assertIn('User profile updated successful', driver.page_source)


    def test_0007_super_admin_login_success(self):
        driver = self.login_member('admin@localhost.com', 'jimaya792')
        self.assertIn('Dashboard', driver.page_source)
    

    def test_0008_super_admin_login_fails(self):
        driver = self.login_member('admin@localhost.com', 'WrongPassword')
        self.assertIn('Fails to authenticate user', driver.page_source)

    def test_0009_force_password_change_success(self):
        driver = webdriver.Chrome()
        driver.get('http://127.0.0.1:8000/admin')
        email_field = driver.find_element_by_name('username')
        password_field = driver.find_element_by_name('password')
        submit_button = driver.find_element_by_xpath("//div[@class='submit-row']//input[@type='submit']")
        email_field.send_keys('admin@localhost.com')
        password_field.send_keys('jimaya792')
        submit_button.send_keys(Keys.RETURN)
        self.assertIn('Site administration', driver.page_source)

        users_link = driver.find_element_by_xpath("//table/tbody/tr[@class='model-user']/th[@scope='row']/a")
        users_link.click()

        search_field = driver.find_element_by_xpath("//form[@id='changelist-search']/div/input[@id='searchbar']")
        search_submit = driver.find_element_by_xpath("//form[@id='changelist-search']/div/input[@type='submit']")

        search_field.send_keys(self.fake_email)
        search_submit.send_keys(Keys.RETURN)

        user_link = driver.find_element_by_xpath("//table[@id='result_list']/tbody/tr/th[@class='field-email']/a")
        user_link.click()

        password_change_checkbox = driver.find_element_by_id("id_password_change")
        password_change_checkbox.click()
        #arthur93@example.net
        save_changes = driver.find_element_by_name('_save')
        save_changes.click()
        self.assertIn('was changed successfully.', driver.page_source)


    def test_0010_change_password_required_success(self):
        driver = self.login_member(self.fake_email, 'Chagepass_123')
        self.assertIn('You must change you password', driver.page_source)

        driver.get('http://127.0.0.1:8000/dashboard')
        self.assertIn('You must change you password', driver.page_source)

        old_password = driver.find_element_by_name('old_password')
        new_password1 = driver.find_element_by_name('new_password1')
        new_password2 = driver.find_element_by_name('new_password2')
        submit = driver.find_element_by_id('id_submit')

        old_password.send_keys('Chagepass_123')
        new_password1.send_keys('Changeme_123')
        new_password2.send_keys('Changeme_123')
        submit.click()

        self.assertIn('Login', driver.page_source)
        driver = self.login_member(self.fake_email, 'Changeme_123')
        self.assertIn('Dashboard', driver.page_source)


    def test_0011_import_statement_xlsx_success(self):
        pass






    def login_member(self, email, password):
        driver = webdriver.Chrome()
        driver.get('http://127.0.0.1:8000/authentication/login')
        email_field = driver.find_element_by_id('email')
        password_field = driver.find_element_by_id('password')
        submit_button = driver.find_element_by_id('submit')

        email_field.send_keys(email)
        password_field.send_keys(password)
        submit_button.send_keys(Keys.RETURN)

        return driver

    
