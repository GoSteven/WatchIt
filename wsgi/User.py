from mongoalchemy.document import Index
from mongoalchemy.fields import StringField
from wsgi.watchit import db

__author__ = 'silyou'

class User(db.Document):
    id = StringField()
    name = StringField()
    email = StringField()
    i_name = Index().ascending('name')
    i_id = Index().ascending('id')


    def is_active(self):
        return True

    def get_id(self):
        return self.id;

    def is_anonymous(self):
        if len(self.name) > 0:
            return True
        else:
            return False

    def is_authenticated(self):
        return self.is_anonymous()



