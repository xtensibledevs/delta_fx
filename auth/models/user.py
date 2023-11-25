from datetime import datetime
import uuid

class User():
    def __init__(self, username, first_name, last_name, email, id="", verified=False):
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.id = uuid.uuid4().hex if not id else id
        self.verified = verified

    @classmethod
    def make_from_dict(cls, d):
        return cls(d['username'], d['first_name'], d['last_name'], d['email'], d['id'], d['verified'])
    
    def dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "verified": self.verified
        }
    
    def display_name(self):
        return f"{self.first_name} {self.last_name}"
        
    @property
    def is_authed(self):
        return True
    
    @property
    def is_active(self):
        return True
    
    def get_id(self):
        return self.id
    
