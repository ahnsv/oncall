# create django ninja router for user app
import logging
from datetime import timedelta, datetime, date
from typing import List

from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Max
from django.shortcuts import get_object_or_404
from ninja import Router, Schema, ModelSchema, Field
from ninja.errors import HttpError

from schedules.models import Schedule, RotationSchedule, Rotation
from .models import Profile, Team

user_router = Router(tags=["users"])

logger = logging.getLogger(__name__)


# schema for Profile
class ProfileIn(Schema):
    name: str
    email: str
    phone: str


# schema for ProfileOut
class ProfileOut(Schema):
    id: int
    name: str
    email: str
    phone: str


# schema TeamIn
class TeamIn(Schema):
    name: str
    members: list[int]
    on_call: int


class TeamOut(ModelSchema):
    class Config:
        model = Team
        model_fields = ["id", "name", "members", "on_call"]


class TeamOncallOut(ModelSchema):
    on_call_: ProfileOut = Field(alias="on_call")

    class Config:
        model = Team
        model_fields = ["id", "name"]
        allow_population_by_field_name = True


@user_router.get("/profiles", response=List[ProfileOut])
def get_profiles(request: WSGIRequest):
    return Profile.objects.all()


@user_router.get("/profiles/{id}", response=ProfileOut)
def get_profile(request: WSGIRequest, id: int):
    return Profile.objects.get(id=id)


@user_router.post("/profiles", response=ProfileOut)
def create_profile(request: WSGIRequest, payload: ProfileIn):
    created = Profile.objects.create(**payload.dict())
    return created


@user_router.put("/profiles/{id}", response={200: ProfileOut})
def update_profile(request: WSGIRequest, id: int, payload: ProfileIn):
    profile = Profile.objects.get(id=id)
    profile.name = payload.name
    profile.email = payload.email
    profile.phone = payload.phone
    profile.save()
    return profile


@user_router.delete("/profiles/{id}", response={204: None})
def delete_profile(request, id: int):
    profile = Profile.objects.get(id=id)
    profile.delete()
    return {"message": "Profile deleted successfully!"}


@user_router.get("/profiles/{id}/teams", response={200: List[TeamOut]})
def get_profile_teams(request: WSGIRequest, id: int):
    profile = Profile.objects.get(id=id)
    return profile.teams.all()


@user_router.get("/profiles/{id}/on_call_teams")
def get_on_call_teams(request: WSGIRequest, id: int):
    profile = Profile.objects.get(id=id)
    return profile.on_call_teams.all()


@user_router.get("/profiles/{id}/on_call")
def get_on_call(request: WSGIRequest, id: int):
    profile = Profile.objects.get(id=id)
    return profile.on_call_teams.all()


@user_router.get("/teams", response=List[TeamOncallOut])
def get_teams(request: WSGIRequest):
    return Team.objects.select_related("on_call").all()


@user_router.get("/teams/{id}", response={200: TeamOut, 404: None})
def get_team(request: WSGIRequest, id: int):
    try:
        teams = Team.objects.filter(id=id).all()
        assert len(teams) == 1
        return teams
    except (Team.DoesNotExist, AssertionError):
        raise HttpError(404, "Team not found")


@user_router.get("/teams/{id}/on_call", response={200: ProfileOut, 404: None})
def get_team_on_call(request: WSGIRequest, id: int):
    try:
        team = Team.objects.get(id=id)
        return team.on_call
    except Team.DoesNotExist:
        raise HttpError(404, "Team not found")


@user_router.post("/teams")
def create_team(request: WSGIRequest, payload: TeamIn):
    return Team.objects.create(**payload.dict())


@user_router.put("/teams/{id}", response={200: TeamOut})
def update_team(request: WSGIRequest, id: int, payload: TeamIn):
    team = Team.objects.get(id=id)
    team.name = payload.name
    team.members.set(payload.members)
    team.on_call = Profile.objects.get(id=payload.on_call)
    team.save()
    return team


@user_router.delete("/teams/{id}", response={204: None})
def delete_team(request: WSGIRequest, id: int):
    team = Team.objects.get(id=id)
    team.delete()
    return {"message": "Team deleted successfully!"}


class RotationIn(Schema):
    name: str
    description: str
    start_date: date
    end_date: date
    cadence_in_days: int  # TODO: add enum


@user_router.post("/team/{team_id}/rotation/")
def create_rotation(request, team_id: int, rotation_in: RotationIn):
    team = get_object_or_404(Team, id=team_id)
    profiles = team.members.all()

    if len(profiles) < 2:
        return {"message": "Rotation requires at least two team members."}

    # # Determine the maximum rotation end date for the team
    # max_end_date = RotationSchedule.objects.filter(rotation__team=team).aggregate(Max("end_date"))["end_date__max"]
    # if max_end_date:
    #     start_date = max_end_date + timedelta(days=1)
    # else:

    start_date = rotation_in.start_date
    # Generate schedules based on rotation start and end dates
    schedules = generate_schedules(rotation_in.start_date, rotation_in.end_date, profiles, team_id=team_id)

    # Create the rotation
    rotation = Rotation.objects.create(team=team, name=rotation_in.name,
                                       description=rotation_in.description)

    rotation_schedules = []
    # Create rotation schedules for each team member
    for i, profile in enumerate(profiles):
        next_index = (i + 1) % len(profiles)
        next_profile = profiles[next_index]
        next_schedule_index = (i + 1) % len(schedules)
        schedule = schedules[i % len(schedules)]
        next_schedule = schedules[next_schedule_index]

        rotation_schedule = RotationSchedule.objects.create(
            rotation=rotation,
            schedule=schedule,
            start_date=start_date,
            end_date=None  # Set the end date later
        )

        # Calculate the end date based on the start date and the next team member's start date
        end_date = start_date + (next_schedule.start_time - start_date)
        rotation_schedule.end_date = end_date
        rotation_schedule.save()
        rotation_schedules.append(rotation_schedule)

        start_date = end_date + timedelta(days=1)

    rotation.rotationschedule_set.add(*rotation_schedules)

    return {"message": "Rotation schedule created successfully."}


def generate_schedules(start_date, end_date, profiles, team_id: int):
    num_days = (end_date - start_date).days + 1
    num_profiles = len(profiles)
    num_schedules = min(num_days, num_profiles)
    schedules = []

    # Generate schedules based on the number of days and profiles
    for i in range(num_schedules):
        schedule_start = start_date + timedelta(days=i)
        schedule_end = schedule_start + timedelta(days=1)
        schedule = Schedule.objects.create(start_time=schedule_start, end_time=schedule_end, on_call_id=profiles[i].id,
                                           team_id=team_id)
        schedules.append(schedule)

    return schedules
