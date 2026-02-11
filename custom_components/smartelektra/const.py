DOMAIN = "smartelektra"

CONF_HOST = "host"
CONF_PORT = "port"
CONF_SLAVE = "slave"
CONF_DEVICE = "device"
CONF_COILS = "coils"

DEFAULT_PORT = 502
DEVICE_MINI = "mini"
DEVICE_MEGA = "mega"

COILS_MINI = 7
COILS_MEGA = 30

# Modbus holding register map for configuration (must match Arduino firmware)
HREG_CFG_BASE = 0
HREG_PULSE_BASE = 100
HREG_COMMIT = 200

# cfg_flags bitmask (must match Arduino firmware)
CFG_INVERT = 1 << 0
CFG_BTN_MONO = 1 << 1
CFG_HA_MONO = 1 << 2
