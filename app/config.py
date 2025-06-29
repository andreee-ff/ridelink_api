import os
from dotenv import load_dotenv

load_dotenv()

LOCATION_TIME_LIMIT_HOURS = int(os.getenv("LOCATION_TIME_LIMIT_HOURS", 24))

if LOCATION_TIME_LIMIT_HOURS < 0: 
    print("LOCATION_TIME_LIMIT_HOURS must be greater than 0. Using default value of 24 hours.")
    LOCATION_TIME_LIMIT_HOURS = 24 