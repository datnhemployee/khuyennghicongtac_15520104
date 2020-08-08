class Author():
    def __init__(self, _id: int, name: str, similarity=None, isAcquantaince=None, isCollaborated=None):
        self._id = _id
        self.name = name
        self.similarity = similarity
        self.isAcquantaince = isAcquantaince
        self.isCollaborated = isCollaborated
