from pathlib import Path


def show_cmd(task):
    return "executing... %s" % task.name


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
        "actions": ["python {}".format(action_path)],
        "title": show_cmd,
    }
