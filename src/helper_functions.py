import numpy as np
from shapely.wkt import loads


def try_wkt_conversion(shape_str):
    try:
        shape_str = loads(shape_str).wkt
    except Exception:
        shape_str = np.nan
    finally:
        return shape_str
