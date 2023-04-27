from .db import Database
from .user import User
from .posts import Posts

class Handler:
    def __init__(self):
        '''Initializes the Handler and the Database.'''

        self.db = Database('db.json')
        self.user = User(self.db)
        self.posts = Posts(self.db)
    


