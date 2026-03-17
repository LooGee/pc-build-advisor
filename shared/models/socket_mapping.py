# CPU Socket → Compatible Chipsets
SOCKET_CHIPSET_MAP = {
    # Intel 12th/13th/14th Gen
    "LGA1700": ["Z790", "B760", "H770", "H710", "Z690", "B660", "H670", "H610"],
    # Intel 15th Gen (Arrow Lake)
    "LGA1851": ["Z890", "B860", "H810"],
    # AMD AM5 (Ryzen 7000/8000/9000)
    "AM5": ["X870E", "X870", "B850", "X670E", "X670", "B650E", "B650"],
    # AMD AM4 (Ryzen 1000-5000)
    "AM4": ["X570", "B550", "B450", "X470", "B350", "X370"],
}

# Chipset → Socket (reverse mapping)
CHIPSET_SOCKET_MAP = {
    chipset: socket
    for socket, chipsets in SOCKET_CHIPSET_MAP.items()
    for chipset in chipsets
}

# CPU brand → typical sockets
BRAND_SOCKET_MAP = {
    "Intel": ["LGA1700", "LGA1851"],
    "AMD": ["AM5", "AM4"],
}

# DDR generation per socket
SOCKET_DDR_MAP = {
    "LGA1700": ["DDR4", "DDR5"],  # Some Z690/B660 support DDR4
    "LGA1851": ["DDR5"],
    "AM5": ["DDR5"],
    "AM4": ["DDR4"],
}
