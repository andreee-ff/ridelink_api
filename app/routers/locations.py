from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas import LocationCreate, LocationRead
from app.models import Location, User
from app.auth import get_current_user, get_db

from sqlalchemy import desc
from collections import defaultdict
from datetime import datetime, timedelta, UTC
from app.config import LOCATION_TIME_LIMIT_HOURS
from app.utils import haversine
from typing import Dict, Any, List


router = APIRouter(
    prefix="/locations",
    tags=["locations"]
)

@router.post("/", response_model=LocationRead, status_code=status.HTTP_201_CREATED)
def create_location(
    location: LocationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Location:
    """
    Create a new location entry for the current user.
    
    Args:
        location: Location data including latitude and longitude
        db: Database session
        current_user: Currently authenticated user
        
    Returns:
        Location: Created location entry
        
    Raises:
        HTTPException: If location data is invalid
    """
    try:
        new_location = Location(
            latitude=location.latitude,
            longitude=location.longitude,
            user_id=current_user.id
        )
        db.add(new_location)
        db.commit()
        db.refresh(new_location)
        return new_location
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create location: {str(e)}"
        )


@router.get("/group/status")
def get_group_status(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get the status of the riding group, including the most distant pair of riders.
    
    Args:
        db: Database session
        
    Returns:
        Dict containing:
        - total_riders: Number of active riders
        - distance_meters: Distance between most distant riders
        - front_user: Information about the front rider
        - last_user: Information about the last rider
        - group_last_updated: Timestamp of the last update
        
    Raises:
        HTTPException: If there are not enough riders
    """
    cutoff = datetime.now(UTC) - timedelta(hours=LOCATION_TIME_LIMIT_HOURS)
    
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough riders to calculate group status"
        )
    
    # Find the most distant pair of riders
    max_distance = 0
    front_user = None
    back_user = None

    for i in range(len(riders)):
        for j in range(i+1, len(riders)):
            distance = haversine(
                riders[i].latitude, 
                riders[i].longitude, 
                riders[j].latitude, 
                riders[j].longitude
            )
            if distance > max_distance:
                max_distance = distance
                front_user = riders[i]
                back_user = riders[j]
    
    return {
        "total_riders": len(riders),
        "distance_meters": round(max_distance, 2),
        "front_user": {
            "id": front_user.user_id,
            "lat": front_user.latitude,
            "lon": front_user.longitude,
            "timestamp": front_user.timestamp.isoformat()
        },
        "last_user": {
            "id": back_user.user_id,
            "lat": back_user.latitude,
            "lon": back_user.longitude,
            "timestamp": back_user.timestamp.isoformat()
        },
        "group_last_updated": datetime.now(UTC).isoformat()
    } 