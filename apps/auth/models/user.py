from datetime import datetime
import uuid
from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, first_name, last_name, email, id="", verified=False):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.id = uuid.uuid4().hex if not id else id
        self.verified = verified

    @classmethod
    def make_from_dict(cls, d):
        return cls(d['first_name'], d['last_name'], d['email'], d['id'], d['verified'])
    
    def dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "verified": self.verified,
        }
    
    def display_name(self):
        return f"{self.first_name} {self.last_name}"
        
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_active(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return self.id
    

# @login_manager.user_loader
# def user_loader(user_id):
#     user_data = db.users.find_one({'id': user_id})
#     user = User.make_from_dict(user_data)
#     return user

# @login_manager.request_loader
# def request_loader(request):
#     userid = request.form.get('userid')
#     user_data = db.users.find_one({'id': userid})
#     user = User.make_from_dict(user_data)
#     return user if user else None