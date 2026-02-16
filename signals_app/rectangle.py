class Rectangle:
    def __init__(self, length: int, width: int):
        if not isinstance(length, int):
            raise TypeError("length must be an int")
        if not isinstance(width, int):
            raise TypeError("width must be an int")
        self.length = length
        self.width = width

    def dimensions_generator(self):
        yield {"length": self.length}
        yield {"width": self.width}
