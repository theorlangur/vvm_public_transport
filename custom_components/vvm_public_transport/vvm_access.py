"""VVM access module."""
from datetime import datetime
import json

import aiohttp


class VVMAccessApi:
    """VVM access API."""

    @staticmethod
    async def fetch_data(url, params):
        """Make an async HTTP request with given url and parameters."""
        async with aiohttp.ClientSession() as session, session.get(
            url, params=params
        ) as response:
            if response.status == 200:
                resp_text = await response.text()
                dec = resp_text
                return json.loads(dec)
            return None

    @staticmethod
    async def get_stop_list(keyword):
        """Obtain list of stops based on the passed keyword."""
        base_url = "https://mobile.defas-fgi.de/vvmapp/XML_STOPFINDER_REQUEST"
        params = {
            "name_sf": keyword,
            "regionID_sf": "1",
            "type_sf": "any",
            "outputFormat": "json",
        }

        data = await VVMAccessApi.fetch_data(base_url, params)
        result = []
        if data:
            points = data["stopFinder"]["points"]
            for p in points:
                if p["type"] == "any" and p["anyType"] == "stop":
                    i = {}
                    i["name"] = p["name"]
                    i["id"] = p["stateless"]
                    result.append(i)
        return result

    @staticmethod
    def try_find_name(p):
        """Try finding the name among the attributes."""
        if "attrs" in p:
            for x in p["attrs"]:
                if x["name"] == "STOP_NAME_WITH_PLACE":
                    return x["value"]
        return None

    @staticmethod
    async def get_stops_nearby(lat, lon, radius=500):
        """Obtain list of stops based on the passed coordinates and radius."""
        # https://mobile.defas-fgi.de/vvmapp/XML_COORD_REQUEST?
        # coord=9.913781952051163:49.79625562837197:WGS84[DD.ddddd]&max=10&inclFilter=1&radius_1=500
        # &type_1=STOP&stateless=1&language=en&outputFormat=XML&coordOutputFormat=WGS84[DD.ddddd]&coordOutputFormatTail=7
        base_url = "https://mobile.defas-fgi.de/vvmapp/XML_COORD_REQUEST"
        params = {
            "coord": f"{lon}:{lat}:WGS84[DD.ddddd]",
            "max": "10",
            "inclFilter": "1",
            "radius_1": f"{radius}",
            "type_1": "STOP",
            "stateless": "1",
            "language": "en",
            "coordOutputFormat": "WGS84[DD.ddddd]",
            "coordOutputFormatTail": "7",
            "outputFormat": "json",
        }

        data = await VVMAccessApi.fetch_data(base_url, params)
        result = []
        if data and "pins" in data:
            points = data["pins"]
            for p in points:
                if p["type"] == "STOP":
                    i = {}
                    i["id"] = p["id"]
                    i["name"] = VVMAccessApi.try_find_name(p)
                    if i["name"] is None:
                        i["name"] = p["desc"]
                    result.append(i)
        return result


class VVMStopMonitor:
    """VVM stop monitoring class."""

    stop_id: str

    def __init__(self, stop_id):
        """Contstruct VVMStopMonitor instance."""
        self.stop_id = stop_id

    @staticmethod
    async def get_departure_monitor_request(stop_id):
        """Make a low-level request to retrieve realtime departures for a given stop."""
        base_url = "https://mobile.defas-fgi.de/vvmapp/XML_DM_REQUEST"
        params = {
            "useRealtime": 1,
            "mode": "direct",
            "name_dm": stop_id,
            "type_dm": "stop",
            "useAllStops": "1",
            "mergeDep": "1",
            "maxTimeLoop": "2",
            "outputFormat": "json",
        }

        return await VVMAccessApi.fetch_data(base_url, params)

    @staticmethod
    async def is_stop_id_valid(stop_id):
        """Check if given stop Id is valid."""
        data = await VVMStopMonitor.get_departure_monitor_request(stop_id)
        err_code = None
        err_msg = None
        if data:
            if data["departureList"]:
                stop_name = None
                if (
                    data["dm"]
                    and data["dm"]["points"]
                    and data["dm"]["points"]["point"]
                ):
                    stop_name = data["dm"]["points"]["point"]["name"]
                return (True, stop_name)
            if data["dm"]:
                dm = data["dm"]
                if dm["message"]:
                    for m in dm["message"]:
                        if m["name"] == "code":
                            err_code = int(m["value"])
                        elif m["name"] == "error":
                            err_msg = m["value"]
                    return (False, err_code, err_msg)
        return (False, err_code, err_msg)

    async def get_stop_departures(self, timespan=30):
        """Retrieve the current departures for a stop of the current instance."""
        data = await self.get_departure_monitor_request(self.stop_id)
        result = []
        if data:
            deps = data["departureList"]
            for d in deps:
                countdown = int(d["countdown"])
                if countdown < timespan:
                    i = {}
                    i["left"] = countdown
                    i["delay"] = int(d["servingLine"]["delay"])
                    i["type"] = d["servingLine"]["name"]
                    i["num"] = d["servingLine"]["number"]
                    i["to"] = d["servingLine"]["direction"]
                    i["from"] = d["servingLine"]["directionFrom"]
                    dt = d["realDateTime"]
                    i["real_time"] = datetime(
                        int(dt["year"]),
                        int(dt["month"]),
                        int(dt["day"]),
                        int(dt["hour"]),
                        int(dt["minute"]),
                    )
                    i["real_time_simple"] = dt["hour"] + ":" + dt["minute"]
                    dt = d["dateTime"]
                    i["should_time"] = datetime(
                        int(dt["year"]),
                        int(dt["month"]),
                        int(dt["day"]),
                        int(dt["hour"]),
                        int(dt["minute"]),
                    )
                    i["should_time_simple"] = dt["hour"] + ":" + dt["minute"]
                    result.append(i)
        return result


class VVMStopMonitorHA:
    """Class to hold the summary information for a given stop ID."""

    api: VVMStopMonitor
    timespan: int
    departures: list[dict]
    last_updated: datetime
    nearest_summary: str
    nearest_left_minutes: int
    nearest_delay_minutes: int
    nearest_vehicle_type: str
    nearest_vehicle_num: str
    _filters: dict
    _stop_name: str

    def __init__(self, stop_id, stop_name, timespan=30):
        """Construct VVMStopMonitorHA instance."""
        self.api = VVMStopMonitor(stop_id)
        self.timespan = timespan
        self._filters = {}
        self._stop_name = stop_name

    def filter_departure_in(self, d):
        """Filter departure in if it fits."""
        if "types" in self._filters and len(self._filters["types"]) > 0:
            if len([t for t in self._filters["types"] if t == d["type"]]) == 0:
                return False
        if "numbers" in self._filters and len(self._filters["numbers"]) > 0:
            if (
                len(
                    [
                        t
                        for t in self._filters["numbers"]
                        if t.strip().lower() == d["num"].lower()
                    ]
                )
                == 0
            ):
                return False
        if "direction" in self._filters and len(self._filters["direction"]) > 0:
            if (
                len(
                    [
                        t
                        for t in self._filters["direction"]
                        if d["to"].lower().find(t.lower()) != -1
                    ]
                )
                == 0
            ):
                return False

        return True

    async def async_update(self):
        """Update departures async."""
        deps = await self.api.get_stop_departures(self.timespan)
        self.departures = [d for d in deps if self.filter_departure_in(d)]
        self.last_updated = datetime.now()
        if len(self.departures) > 0:
            closest = self.departures[0]
            self.nearest_summary = "({:d} min) {} {} ({})".format(
                closest["left"], closest["type"], closest["num"], closest["to"]
            )
            self.nearest_left_minutes = closest["left"]
            self.nearest_delay_minutes = closest["delay"]
            self.nearest_vehicle_type = closest["type"]
            self.nearest_vehicle_num = closest["num"]
        else:
            self.nearest_summary = "Unknown"
            self.nearest_left_minutes = 0
            self.nearest_delay_minutes = 0
            self.nearest_vehicle_type = "Unknown"
            self.nearest_vehicle_num = "Unknown"

    @property
    def stop_name(self):
        """Access stop name as a property."""
        return self._stop_name

    @property
    def stop_id(self):
        """Access stop id as a property."""
        return self.api.stop_id

    @property
    def filter_types(self):
        """Access filter types if they exist."""
        if "types" not in self._filters:
            self._filters["types"] = []
        return self._filters["types"]

    @filter_types.setter
    def filter_types(self, types):
        """Set filter types."""
        self._filters["types"] = types

    @property
    def filter_nums(self):
        """Access filter numbers if they exist."""
        if "numbers" not in self._filters:
            self._filters["numbers"] = []
        return self._filters["numbers"]

    @filter_nums.setter
    def filter_nums(self, v):
        """Set filter numbers."""
        if isinstance(v, str):
            v = v.strip()
            if v not in ("*", ""):
                self._filters["numbers"] = [x.lower().strip() for x in v.split(",")]
            else:
                self._filters["numbers"] = []
        else:
            self._filters["numbers"] = v

    @property
    def filter_direction(self):
        """Access filter direction if it exist."""
        if "direction" not in self._filters:
            self._filters["direction"] = []
        return self._filters["direction"]

    @filter_direction.setter
    def filter_direction(self, d):
        """Set filter direction."""
        if isinstance(d, str):
            d = d.strip()
            if d not in ("*", ""):
                self._filters["direction"] = [x.lower().strip() for x in d.split(",")]
            else:
                self._filters["direction"] = []
        else:
            self._filters["direction"] = d