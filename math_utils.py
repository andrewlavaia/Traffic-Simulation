import math


def pythag(side1, side2):
    """pythagorean theorem"""
    return math.sqrt((side1 * side1) + (side2 * side2))


def angle(dx, dy):
    '''returns radians in cartesian coordinates'''
    radians = math.atan2(dy, dx)
    return radians


def degrees_clockwise(dx, dy):
    '''returns rotation degrees assuming 0 is 12 o'clock'''
    radians = angle(dx, dy)  # between -pi and pi
    degrees = radians * 180/math.pi
    if degrees > 90:
        degrees = 450 - degrees
    else:
        degrees = 90 - degrees
    return degrees


def rotate_point(point, angle, center_point=(0, 0)):
    """Rotates a point around center_point(origin by default)
    Angle is in degrees.
    Rotation is counter-clockwise

    https://stackoverflow.com/questions/20023209/function-for-rotating-2d-objects
    """
    angle_rad = math.radians(angle % 360)
    # Shift the point so that center_point becomes the origin
    new_point = (point[0] - center_point[0], point[1] - center_point[1])
    new_point = (new_point[0] * math.cos(angle_rad) - new_point[1] * math.sin(angle_rad),
                 new_point[0] * math.sin(angle_rad) + new_point[1] * math.cos(angle_rad))
    # Reverse the shifting we have done
    new_point = (new_point[0] + center_point[0], new_point[1] + center_point[1])
    return new_point
