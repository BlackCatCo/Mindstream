from operator import itemgetter
import datetime
import uuid

class Posts:
    def __init__(self, db):
        self.db = db
    
    def get_all(self):
        return self.db.data['posts']
    
    def add(self, title, description, author):
        post = {
            "id": str(uuid.uuid4()),
            "title": title,
            "description": description,
            "author": author,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "tags": []
        }

        posts = self.get_all()
        posts.insert(0, post)

        self.db.save()