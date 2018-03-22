from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from django.urls import reverse

from .models import Game, Round
from .forms import AddUserForm, LoginForm
# Create your views here.


# basic view with links to login/register
class BasicView(View):
    def get(self, request):
        return render(
            request,
            template_name="main.html",
            context={}
        )


# registration
class AddUserView(View):
    def get(self, request):
        form = AddUserForm()
        ctx = {
            'form': form
        }
        return render(
            request,
            template_name='register.html',
            context=ctx
        )

    def post(self, request):
        form = AddUserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            if User.objects.filter(username=username).exists():
                form.add_error('username', "username already exists")
            password = form.cleaned_data['password']
            password2 = form.cleaned_data['password2']
            if password != password2:
                form.add_error('password', "Passwords don't match")
            if not form.errors:
                User.objects.create_user(
                    username=username,
                    password=password
                )
                return HttpResponse("Created new account")
        ctx = {
            'form': form
        }
        return render(
            request,
            template_name='register.html',
            context=ctx
        )


class UserLoginView(View):
    def get(self, request):
        form = LoginForm()
        ctx = {
            'form': form
        }
        return render(
            request,
            template_name='login.html',
            context=ctx
        )

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "You are logged in")
                return redirect("/lobby")
            return HttpResponse("Try again")
        ctx = {
            'form': form
        }
        return render(
            request,
            template_name='login.html',
            context=ctx
        )


class UserLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("/login")


# lobby with available games and link to game creation
class LobbyView(View):
    @method_decorator(login_required)
    def get(self, request):
        user = request.user
        games = Game.objects.filter(opponent_id=None, completed=False)
        games = games.order_by('-creation_time')
        ctx = {
            "games": games,
            "user": user,
        }
        return render(
            request,
            template_name="lobby.html",
            context=ctx
        )


# game creation
class LoggedUserView(View):
    def get(self, request):
        user = request.user
        ctx = {
            "user": user,
        }
        return render(
            request,
            template_name="create.html",
            context=ctx
        )

    def post(self, request):
        user = request.user
        new_game = Game.objects.create(creator_id=user)

        ctx = {
            "user": user,
            "new_game": new_game
        }
        return redirect("/game-view/{}".format(new_game.id))


class GameView(View):
    def get(self, request, id):
        game = Game.objects.get(id=id)
        user = request.user
        game_creator = game.creator_id
        round_count = game.rounds.all().count()
        ctx = {
            "game": game,
            "user": user,
            "game_creator": game_creator,
            "round_count": round_count,
        }
        return render(
            request,
            template_name="game_view.html",
            context=ctx
        )

    def post(self, request, id):
        game = Game.objects.get(id=id)
        user = request.user
        game_creator = game.creator_id
        if user == game_creator:
            new_round = Round.objects.create(round=game)
            ctx = {
                "game": game,
                "user": user,
                "new_round": new_round,
            }
            return redirect("{}/round/{}".format(game.id, new_round.id))
        return HttpResponse("You are not a game creator!")


class GameRoundView(View):
    def get(self, request, id, round_id):
        game = Game.objects.get(id=id)
        user = request.user
        game_creator = game.creator_id
        round = Round.objects.get(id=round_id)
        ctx = {
            "game": game,
            "round": round,
            "user": user,
        }
        return render(
            request,
            template_name="round_view.html",
            context=ctx,
        )

    def post(self, request, id, round_id):
        game = Game.objects.get(id=id)
        user = request.user
        game_creator = game.creator_id
        round = Round.objects.get(id=round_id)
        if "rock" in request.POST:
            round.creator_move = 1
            round.save()
        elif "paper" in request.POST:
            round.creator_move = 2
            round.save()
        elif "scissors" in request.POST:
            round.creator_move = 3
            round.save()
        return redirect("/game-view/{}".format(game.id))


class JoinGameView(View):
    def get(self, request, game_id):
        game = Game.objects.get(id=game_id)
        user = request.user
        creator = game.creator_id
        rounds = game.rounds.filter(opponent_move=None)
        if user.username != creator.username and game.opponent_id is None:
            game.opponent_id = user
            game.save()
        elif user.username == creator.username:
            return HttpResponse("You cannot play against yourself!")
        ctx = {
            "game": game,
            "user": user,
            "creator": creator,
            "rounds": rounds,
        }
        return render(
            request,
            template_name="join_game.html",
            context=ctx
        )


class JoinRoundView(View):
    def get(self, request, game_id, round_id):
        game = Game.objects.get(id=game_id)
        round = Round.objects.get(id=round_id)
        user = request.user
        creator = game.creator_id
        ctx = {
            "game": game,
            "user": user,
            "creator": creator,
            "round": round,
        }
        return render(
            request,
            template_name="join_round.html",
            context=ctx
        )

    def post(self, request, game_id, round_id):
        game = Game.objects.get(id=game_id)
        user = request.user
        game_creator = game.creator_id
        round = Round.objects.get(id=round_id)
        if "rock" in request.POST:
            round.opponent_move = 1
            round.save()
        elif "paper" in request.POST:
            round.opponent_move = 2
            round.save()
        elif "scissors" in request.POST:
            round.opponent_move = 3
            round.save()
        return redirect("/join-game/{}".format(game.id))


class ResultsView(View):
    def get(self, request, game_id):
        pass
