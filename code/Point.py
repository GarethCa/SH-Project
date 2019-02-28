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
        string = str(self.x)  + " " + str(self.y) + " " +  str(self.z)
        return string

class TimeTuple:

    def __init__(self, point, time):
        self.val = (point, time)
