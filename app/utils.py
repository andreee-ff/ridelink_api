from math import radians, sin, cos, sqrt, atan2

# Later 'geopy' could be used for this
# Now we're using the haversine formula with zero overhead

def haversine(lat1, lon1, lat2, lon2):
    # Radius of the Earth in meters
    R = 6371000 

    # Convert degrees to radians
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = sin(dlat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c

