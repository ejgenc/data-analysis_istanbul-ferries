from shapely.geometry import Point, LineString


def check_line_validity(line_points):
    try:
        LineString(line_points)
    except Exception:
        raise Exception


def check_point_validity(c1, c2):
    try:
        Point(c1, c2)
    except Exception:
        raise Exception
