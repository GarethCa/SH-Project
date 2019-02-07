class Point:

    def __init__(self,time,x,y,z):
        self.time = time
        self.x = x
        self.y = y
        self.z = z

    def get_x_y(self):
        return (self.x, self.y)

class TimeTuple:

    def __init__(self,point, time):
        self.val = (point,time)