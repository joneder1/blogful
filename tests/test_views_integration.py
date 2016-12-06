import os
import unittest
from urllib.parse import urlparse

from werkzeug.security import generate_password_hash

# Configure your app to use the testing database
os.environ["CONFIG_PATH"] = "blog.config.TestingConfig"

from blog import app
from blog.database import Base, engine, session, User, Entry

class TestViews(unittest.TestCase):
    def setUp(self):
        """ Test setup """
        self.client = app.test_client()

        # Set up the tables in the database
        Base.metadata.create_all(engine)

        # Create an example user
        self.user = User(name="Alice", email="alice@example.com",
                         password=generate_password_hash("test"))
        session.add(self.user)
        session.commit()

    def simulate_login(self):
        with self.client.session_transaction() as http_session:
            http_session["user_id"] = str(self.user.id)
            http_session["_fresh"] = True

    def test_add_edit_delete_entry(self):
        self.simulate_login()

        response = self.client.post("/entry/add", data={
            "title": "Test Entry",
            "content": "Test content"
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.location).path, "/")
        #should be one entry 
        entries = session.query(Entry).all()
        self.assertEqual(len(entries), 1)
        
        #checks that title and content appear correctly
        entry = entries[0]
        self.assertEqual(entry.title, "Test Entry")
        self.assertEqual(entry.content, "Test content")
        self.assertEqual(entry.author, self.user)
        
        #tests edit entry function
        response = self.client.post("/entry/1/edit", data={
            "title": "Edited Test Entry",
            "content": "Edited Test content"
        })
        
        self.assertEqual(response.status_code, 302)  
        self.assertEqual(urlparse(response.location).path, "/") 
        # Test post data
        entry = session.query(Entry).all() 
        entry = entries[0]
        #New title/content after edit
        self.assertEqual(entry.title, "Edited Test Entry")
        self.assertEqual(entry.content, "Edited Test content")
        self.assertEqual(entry.author, self.user)    
        
        #deletes the entry
        response = self.client.post("/entry/1/delete")
        self.assertEqual(response.status_code, 302)  
        self.assertEqual(urlparse(response.location).path, "/")  
        # Should not be any entries left
        entries = session.query(Entry).all() 
        self.assertEqual(len(entries), 0)
        
    def test_Logout(self):
        self.simulate_login()
        response = self.client.get("/logout")
        self.assertEqual(urlparse(response.location).path, "/login")

    def tearDown(self):
        """ Test teardown """
        session.close()
        # Remove the tables and their data from the database
        Base.metadata.drop_all(engine)

if __name__ == "__main__":
    unittest.main()