
def cellDist(cenOne, cenTwo):
    x_dist = abs(cenOne.centroid[0] - cenTwo.centroid[0])
    y_dist = abs(cenOne.centroid[1] - cenTwo.centroid[1])
    return x_dist + y_dist