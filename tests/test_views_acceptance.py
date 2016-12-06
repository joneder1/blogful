import os
import unittest
import multiprocessing
import time
from urllib.parse import urlparse

from werkzeug.security import generate_password_hash
from splinter import Browser

# Configure your app to use the testing database
os.environ["CONFIG_PATH"] = "blog.config.TestingConfig"

from blog import app
from blog.database import Base, engine, session, User

class TestViews(unittest.TestCase):
    def setUp(self):
        """ Test setup """
        self.browser = Browser("phantomjs")

        # Set up the tables in the database
        Base.metadata.create_all(engine)

        # Create an example user
        self.user = User(name="Alice", email="alice@example.com",
                         password=generate_password_hash("test"))
        session.add(self.user)
        session.commit()

        self.process = multiprocessing.Process(target=app.run,
                                               kwargs={"port": 8080})
        self.process.start()
        time.sleep(1)

    def test_login_correct(self):
        self.browser.visit("http://127.0.0.1:8080/login")
        self.browser.fill("email", "alice@example.com")
        self.browser.fill("password", "test")
        button = self.browser.find_by_css("button[type=submit]")
        button.click()
        self.assertEqual(self.browser.url, "http://127.0.0.1:8080/")

    def test_login_incorrect(self):
        self.browser.visit("http://127.0.0.1:8080/login")
        self.browser.fill("email", "bob@example.com")
        self.browser.fill("password", "test")
        button = self.browser.find_by_css("button[type=submit]")
        button.click()
        self.assertEqual(self.browser.url, "http://127.0.0.1:8080/login")
        
    def test_logout(self):
        # Login to blog
        self.test_login_correct()
        # Click on 'Logout' link
        self.browser.click_link_by_text('Logout')
        # Check to see if 'Logout' link is visible
        self.assertEqual(self.browser.is_element_present_by_text('Logout'), False)
        # Check to see if 'Login' link is visible
        self.assertEqual(self.browser.is_element_present_by_text('Login'), True)    
        
    def testAddEntryNotLoggedIn(self):
        self.test_login_incorrect()
        #tries to visit entry page
        self.browser.visit("http://127.0.0.1:8080/entry/add")
        #redirects to login page
        self.assertEqual(self.browser.url, "http://127.0.0.1:8080/login?next=%2Fentry%2Fadd")    
        
    def testAddEntryLoggedIn(self):
        self.test_login_correct()
        #visit the add entry page by clicking on button - how to make this work?
        #self.browser.find_by_css("button[type=add]").first.click()
        self.browser.visit("http://127.0.0.1:8080/entry/add")
        self.browser.fill("title", "Add Entry Logged In Test Title")
        self.browser.fill("content", "Test content for add entry logged in")
        #find button for add entry and click it 
        button = self.browser.find_by_css("button[type=submit]")
        button.click()
        #browser should return to homepage after test entry added
        self.assertEqual(self.browser.url, "http://127.0.0.1:8080/")
        
    def testEditEntryLoggedIn(self):
        self.test_login_correct()
        self.browser.visit("http://127.0.0.1:8080/entry/add")
        self.browser.fill("title", "Edit Entry Logged In Title")
        self.browser.fill("content", "Edit Entry Logged in content")
        self.browser.find_by_css("button[type=submit]").first.click()
        self.browser.click_link_by_partial_href('edit')
        self.browser.fill("title", "edited title")
        self.browser.fill("content", "edited content")
        self.browser.find_by_css("button[type=submit]").first.click()
        self.assertEqual(self.browser.url, "http://127.0.0.1:8080/")
        
    def testDeleteEntryLoggedIn(self):
        self.test_login_correct()
        self.browser.visit("http://127.0.0.1:8080/entry/add")
        self.browser.fill("title", "Test Delete Entry")
        self.browser.fill("content", "Test content for delete entry")
        self.browser.find_by_css("button[type=submit]").first.click()
        self.browser.click_link_by_partial_href('delete')
        button = self.browser.find_by_css("button[type=submit]")
        button.click()
        #browser should return to homepage after delete
        self.assertEqual(self.browser.url, "http://127.0.0.1:8080/")
        
    def test_logout(self):
        self.test_login_correct()
        self.browser.click_link_by_text('Logout')
        self.assertEqual(self.browser.url, "http://127.0.0.1:8080/login")   
        
    def tearDown(self):
        """ Test teardown """
        # Remove the tables and their data from the database
        self.process.terminate()
        session.close()
        engine.dispose()
        Base.metadata.drop_all(engine)
        self.browser.quit()

if __name__ == "__main__":
    unittest.main()