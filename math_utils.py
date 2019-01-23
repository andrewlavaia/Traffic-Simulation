import math


def pythag(side1, side2):
    """pythagorean theorem"""
    return math.sqrt((side1 * side1) + (side2 * side2))


def angle(dy, dx):
    ''' returns radians in cartesian coordinates '''
    radians = math.atan2(dy, dx)
    return radians
