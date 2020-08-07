class Author():
    def __init__(self, _id: int, name: str, similarity=None):
        self._id = _id
        self.name = name
        self.similarity = similarity
