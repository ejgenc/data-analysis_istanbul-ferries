import numpy as np
from shapely.wkt import loads


def try_wkt_conversion(shape_str):
    try:
        shape_str = loads(shape_str).wkt
    except Exception:
        shape_str = np.nan
    finally:
        return shape_str


def convert_coord(coord_str, from_format, to_format):
    format_dict = {
        "degrees_minutes": {"degrees": degrees_minutes_to_degrees},
        "degrees_minutes_seconds": {"degrees": degrees_minutes_seconds_to_degrees},
    }
    return format_dict[from_format][to_format](coord_str)


def degrees_minutes_to_degrees(coord_str):
    degrees, minutes, orientation = coord_str.split(" ")
    degrees = int(degrees.strip("⁰"))
    minutes = int(minutes.strip("’"))

    result = (degrees + (minutes / 60)) * (-1 if orientation in {"S", "W"} else 1)
    return result


def degrees_minutes_seconds_to_degrees(coord_str):
    coord_str = coord_str.replace(" ", "").replace("°", "⁰")  # right?
    degrees, minutes = coord_str.split("⁰")
    minutes, seconds = minutes.replace("′", "'").replace("\\", "").split("'")
    seconds, orientation = seconds.replace('"', "″").split("″")

    result = (int(degrees) + (int(minutes) / 60) + (float(seconds) / 3600)) * (
        -1 if orientation in {"S", "W"} else 1
    )
    return result
