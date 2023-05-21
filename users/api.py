# create django ninja router for user app
from ninja import Router
from .models import User
from .schemas import UserSchema
 
user_router = Router()
 
 # create user
@user_router.post("/")
def create_user(request, user: UserSchema):
    return User.objects.create_user(**user.dict())
 
 # get user by id
@user_router.get("/{user_id}")
def get_user(request, user_id: int):
    return User.objects.get(id=user_id)

# get all users
@user_router.get("/")
def get_users(request):
    return User.objects.all()

# update user by id
@user_router.patch("/{user_id}")
def update_user(request, user_id: int, user: UserSchema):
    user_obj = User.objects.get(id=user_id)
    user_obj.email = user.email
    user_obj.first_name = user.first_name
    user_obj.last_name = user.last_name
    user_obj.save()
    return user_obj

 # delete user by id
@user_router.delete("/{user_id}")
def delete_user(request, user_id: int):
   user_obj = User.objects.get(id=user_id)
   user_obj.delete()
   return {'message': 'User deleted successfully'}
 
