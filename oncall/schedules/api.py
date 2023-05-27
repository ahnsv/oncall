from ninja import Router, ModelSchema, Schema
from .models import Schedule
from typing import List
from datetime import datetime

# add ninja router for schedules
schedule_router = Router(tags=["schedules"])


# schema for ScheduleIn
class ScheduleIn(Schema):
    team_id: int
    start_time: datetime
    end_time: datetime
    on_call_id: int


# schema for ScheduleOut
class ScheduleOut(ModelSchema):
    class Config:
        model = Schedule
        model_fields = ["id", "team", "start_time", "end_time", "on_call"]


@schedule_router.get("/schedules", response=List[ScheduleOut])
def get_schedules(request):
    return Schedule.objects.all()


@schedule_router.post("/schedules")
def create_schedule(request, payload: ScheduleIn):
    return Schedule.objects.create(**payload.dict())


@schedule_router.post("/schedules/team", response={200: List[ScheduleOut]})
def create_team_schedule(request, payload: List[ScheduleIn]):
    schedules = [Schedule.objects.create(**schedule.dict()) for schedule in payload]
    return schedules
