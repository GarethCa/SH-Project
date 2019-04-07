class Point:

    def __init__(self, time, x, y, z):
        self.time = time
        self.x = x
        self.y = y
        self.z = z
        self.comment = ""

    def get_x_y(self):
        return (self.x, self.y)

    def comment(self, text):
        self.comment = text

    def __str__(self):
        string = str(self.time) + " "+str(self.x) + " " + str(self.y) + " " + str(self.z)
        return string

    def to_dict(self):
        return {'x': self.x,
                'y': self.y,
                'z': self.z,
                't': self.time}

    def __lt__(self,other):
        return self.time < other.time
    
    def __eq__(self,other):
        return self.time == other.time


class TimeTuple:

    def __init__(self, point, time):
        self.val = (point, time)
