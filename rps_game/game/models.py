from django.contrib.auth.models import User
from datetime import datetime
from django.db import models

# Create your models here.


class Game(models.Model):
    # players info
    creator_id = models.ForeignKey(User, related_name='creator', on_delete=models.CASCADE)
    opponent_id = models.ForeignKey(User, related_name='opponent', null=True, blank=True, on_delete=models.CASCADE)
    creator_results = models.IntegerField(default=0)
    opponent_results = models.IntegerField(default=0)
    winner = models.ForeignKey(User, related_name='won', null=True, blank=True, on_delete=models.CASCADE)
    # state
    creation_time = models.DateTimeField(auto_now_add=True)
    ending_time = models.DateTimeField(null=True, blank=True)
    completed = models.BooleanField(default=False)


DECISION = {
    (1, "rock"),
    (2, "paper"),
    (3, "scissors")
}


class Round(models.Model):
    round = models.ForeignKey(Game, related_name='rounds', on_delete=models.CASCADE)
    # player moves
    creator_move = models.IntegerField(choices=DECISION, null=True, blank=True)
    opponent_move = models.IntegerField(choices=DECISION, null=True, blank=True)



