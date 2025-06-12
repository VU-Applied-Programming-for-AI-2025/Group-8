import json

class Recipe:
    def __init__(self, id, title) -> None:
        self.id = id
        self.title = title
    
    def toJSON(self):
        return {
            "id": self.id,
            "title": self.title
        }