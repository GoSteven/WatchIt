__author__ = 'silyou'

class User:

    def __init__(self, id, name):
        self.id = id
        self.name = name

    def is_active(self):
        return True

    def get_id(self):
        return self.id;

    def is_anonymous(self):
        if self.name:
            return True
        else:
            return False

    def is_authenticated(self):
        return self.is_anonymous()

    @staticmethod
    def get(id):
        return User(id, id)


