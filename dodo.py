from pathlib import Path
from doit.tools import run_once


def show_cmd(task):
    return "executing... %s" % task.name


def task_prepare():
    action_path = Path("src/utility-scripts/prepare.py")
    return {
        "actions": ["python {}".format(action_path)],
        "uptodate": [run_once],
        "title": show_cmd,
    }


def task_clean_raw():
    action_path = Path("src/cleaning/clean_raw.py")
    return {
        "file_dep": [
            Path("data/raw/geolocation/automated-weather-stations-geoloc.csv"),
            Path("data/raw/geolocation/ferry-lines-geoloc.csv"),
            Path("data/raw/geolocation/ferry-terminals-geoloc.csv"),
            Path("data/raw/geolocation/icing-sensors-geoloc.csv"),
            Path(
                "data/raw/historic-transportation-load/transportation-load_202001.csv"
            ),
            Path("data/raw/historic-weather-observations/observations_202001.csv"),
            Path("data/raw/summary-stats/trips-per-ferry-line_2020.csv"),
        ],
        "task_dep": ["prepare"],
        "actions": ["python {}".format(action_path)],
        "title": show_cmd,
    }
