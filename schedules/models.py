from django.db import models
from users.models import Team, Profile

class Schedule(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    on_call = models.ForeignKey(Profile, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.team.name} - {self.on_call.name} - {self.start_time} to {self.end_time}"
