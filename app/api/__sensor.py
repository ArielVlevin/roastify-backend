from fastapi import APIRouter
from services.mock_sensor import MockSensor
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter()

sensor = MockSensor(interval=1.0)

# מודל לתוצאה בודדת
class TemperaturePoint(BaseModel):
    time: str
    temperature: float

# מצב הסשן הנוכחי
class SessionState:
    is_active: bool = False
    start_time: Optional[datetime] = None
    data: List[TemperaturePoint] = []

session = SessionState()
latest_value: float = 0.0


# איסוף נתונים – רק אם יש סשן פעיל
@sensor.start
def handle_data(val: float):
    global latest_value
    latest_value = val
    if session.is_active:
        session.data.append(
            TemperaturePoint(time=datetime.now().isoformat(), temperature=val)
        )


@router.post("/sensor/start")
def start_session():
    session.is_active = True
    session.start_time = datetime.now()
    session.data = []
    return {"message": "Session started"}


@router.post("/sensor/stop")
def stop_session():
    session.is_active = False
    return {
        "message": "Session stopped",
        "start_time": session.start_time,
        "num_points": len(session.data),
        "data": session.data,
    }


@router.get("/sensor/data")
def get_current_value():
    return {"temperature": latest_value}


@router.get("/sensor/status")
def get_session_status():
    return {
        "is_active": session.is_active,
        "start_time": session.start_time,
        "data_length": len(session.data),
    }


@router.get("/sensor/history")
def get_session_data():
    return {"data": session.data}