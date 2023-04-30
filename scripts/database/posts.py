from operator import itemgetter
import datetime
import uuid

class Posts:
    def __init__(self, db):
        self.db = db
        self.default_post = {
            "id": None,
            "title": None,
            "description": None,
            "author": None,
            "timestamp": None,
            "tags": [],
            "comments": []
        }

        self.default_comment = {
            'id': None,
            'author': None,
            'text': None,
            'timestamp': None
        }

    def _timestamp(self):
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    def get_all(self):
        return self.db.data['posts']
    
    def add(self, title, description, author):

        post = self.default_post.copy()
        post['id'] = str(uuid.uuid4())
        post['title'] = title
        post['description'] = description
        post['author'] = author
        post['timestamp'] = self._timestamp()

        posts = self.get_all()
        posts.insert(0, post)

        self.db.save()
    
    def remove(self, id):
        posts = self.get_all()
        out = False
        for p in posts:
            if p['id'] == id:
                posts.remove(p)
                out = True
        return out
    
    def get(self, id):
        out = None
        for p in self.get_all():
            if p['id'] == id:
                out = p
        return out
    
    def add_comment(self, post_id, comment_text, author):
        post = self.get(post_id)
        if post != None:
            comment = self.default_comment.copy()
            comment['id'] = str(uuid.uuid4())
            comment['author'] = author
            comment['text'] = comment_text
            comment['timestamp'] = self._timestamp()

            post['comments'].insert(0, comment)
            self.db.save()
            return True
        else:
            return False

    def migrate(self):
        new_posts = []
        old_posts = self.get_all()
        for old_p in old_posts:
            new_p = self.default_post.copy()
            for k in old_p:
                if k in new_p:
                    new_p[k] = old_p[k]

            new_posts.append(new_p)


        self.db.data['posts'] = new_posts

        self.db.save()