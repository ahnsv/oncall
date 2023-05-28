from django.db import models
from users.models import Team, Profile


class Schedule(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    on_call = models.ForeignKey(Profile, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.team.name} - {self.on_call.name} - {self.start_time} to {self.end_time}"


class Rotation(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    team = models.ForeignKey("users.Team", on_delete=models.CASCADE, related_name="rotation", null=True)
    schedules = models.ManyToManyField(Schedule, through='RotationSchedule')

    def __str__(self):
        return self.name


class RotationSchedule(models.Model):
    rotation = models.ForeignKey(Rotation, on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(null=True)

    def __str__(self):
        return f'{self.rotation.name} - {self.schedule}'
