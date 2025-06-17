from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas import LocationCreate, LocationRead
from app.models import Location, User
from app.auth import get_current_user, get_db

from app.utils import habersine
from sqlalchemy import desc
from collections import defaultdict
from datetime import datetime, timedelta
from app.config import LOCATION_TIME_LIMIT_HOURS
from app.utils import haversine


router = APIRouter(
    prefix="/locations",
    tags=["locations"]
)

@router.post("/", response_model=LocationRead)
def create_location(
    location: LocationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    new_location = Location(
        latitude=location.latitude,
        longitude=location.longitude,
        user_id=current_user.id
    )
    db.add(new_location)
    db.commit()
    db.refresh(new_location)
    return new_location


@router.get("/group/status")
def get_group_status(db: Session = Depends(get_db)):
    cutoff = datetime.utcnow() - timedelta(hours=LOCATION_TIME_LIMIT_HOURS)
    
    # Get latest location for each user
    all_locations = db.query(Location).filter(Location.timestamp >= cutoff).all()

    # Keep the latest location for each user
    latest_by_user = {}
    for loc in sorted(all_locations, key=lambda x: x.timestamp, reverse=True):
        if loc.user_id not in latest_by_user:
            latest_by_user[loc.user_id] = loc

    # Get all riders
    riders = list(latest_by_user.values())

    if len(riders) < 2:
        return {"message": "not enough riders"}
    
    # Find the most distant pair of riders
    max_distance = 0
    front_user = None
    back_user = None

    for i in range(len(riders)):
        for j in range(i+1, len(riders)):
            distance = haversine(riders[i].latitude, riders[i].longitude, riders[j].latitude, riders[j].longitude)
            if distance > max_distance:
                max_distance = distance
                front_user = riders[i]
                back_user = riders[j]
    
    return {
        "total_riders" : len(riders),
        "front_user": front_user,
        "back_user": back_user,
        "distance_meters": round(max_distance, 2),
        "timestamp_front":  front_user.timestamp,
        "timestamp_back": back_user.timestamp
        }











