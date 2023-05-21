from django.db import models


# create django model Team and Profile
class Team(models.Model):
    name = models.CharField(max_length=50)
    members = models.ManyToManyField("Profile", blank=True, related_name="teams")
    on_call = models.ForeignKey(
        "Profile", on_delete=models.SET_NULL, null=True, blank=True, related_name="on_call_teams"
    )

    def __str__(self):
        return self.name

# create django mdel named Profile
class Profile(models.Model):
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE, null=True, related_name="profile")
    name = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=20)

    def __str__(self):
        return self.name

