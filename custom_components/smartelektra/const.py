DOMAIN = "smartelektra"

CONF_HOST = "host"
CONF_PORT = "port"
CONF_SLAVE = "slave"
CONF_DEVICE = "device"
CONF_COILS = "coils"

DEVICE_MINI = "mini"   # UNO (7)
DEVICE_MEGA = "mega"   # MEGA (30)

DEFAULT_PORT = 502
DEFAULT_SLAVE = 1

COILS_BY_DEVICE = {
    DEVICE_MINI: 7,
    DEVICE_MEGA: 30,
}
