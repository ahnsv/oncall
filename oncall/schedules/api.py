from ninja import Router
from .models import Schedule
from pydantic import BaseModel
from typing import List
from datetime import datetime

# add ninja router for schedules
schedule_router = Router(tags=["schedules"])


# schema for ScheduleIn
class ScheduleIn(BaseModel):
    team: int
    start_time: datetime
    end_time: datetime
    on_call: int


# schema for ScheduleOut
class ScheduleOut(ScheduleIn):
    id: int
    team = int
    start_time = datetime
    end_time = datetime
    on_call = int


@schedule_router.get("/schedules", response=List[ScheduleOut])
def get_schedules(request):
    return Schedule.objects.all()


@schedule_router.post("/schedules")
def create_schedule(request, payload: ScheduleIn):
    return Schedule.objects.create(**payload.dict())


@schedule_router.post("/schedules/team")
def create_team_schedule(request, payload: List[ScheduleIn]):
    return Schedule.objects.create(**payload.dict())
