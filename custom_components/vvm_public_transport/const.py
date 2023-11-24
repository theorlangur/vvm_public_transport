"""Constants for the vvm_transport integration."""

DOMAIN = "vvm_public_transport"

CONF_STATION = "station"
CONF_STOP_ID = "stop_id"
CONF_TIMEFRAME = "timeframe"
CONF_FILTER_DIRECTION = "filter_direction"
CONF_FILTER_TYPE = "filter_type"
CONF_FILTER_NUM = "filter_num"

V_TYPE_TRAM = "Straßenbahn"
V_TYPE_BUS = "Bus"
V_TYPE_REGIONAL_BUS = "Regionalbus"
V_TYPE_NIGHT_BUS = "Nachtbus"
V_TYPE_REPLACEMENT = "Ersatzverkehr"
V_TYPE_S_BAHN = "S-Bahn"
V_TYPE_U_BAHN = "U-Bahn"

V_TYPE_LIST = [
    V_TYPE_TRAM,
    V_TYPE_BUS,
    V_TYPE_REGIONAL_BUS,
    V_TYPE_NIGHT_BUS,
    V_TYPE_REPLACEMENT,
    V_TYPE_S_BAHN,
    V_TYPE_U_BAHN,
]
