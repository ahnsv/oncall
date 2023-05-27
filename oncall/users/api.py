# create django ninja router for user app
from django.core.handlers.wsgi import WSGIRequest
from ninja import Router, Schema, ModelSchema, Field
from pydantic import BaseModel

from .models import Profile, Team
from typing import List
import logging

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


@user_router.put("/teams/{id}")
def update_team(request: WSGIRequest, id: int, payload: TeamIn):
    team = Team.objects.get(id=id)
    team.name = payload.name
    team.members = payload.members
    team.on_call = payload.on_call
    team.save()
    return team


@user_router.delete("/teams/{id}", response={204: None})
def delete_team(request: WSGIRequest, id: int):
    team = Team.objects.get(id=id)
    team.delete()
    return {"message": "Team deleted successfully!"}
