from django.shortcuts import render, redirect
from .forms import UsernameForm
from .models import Player

async def show_stats(request):
    return render(request, 'stats/stats.html/')

async def lookup(request, username):
    uuid = await Player.get_uuid(username)
    context = await Player.get_stats(uuid)
    return render(request, 'stats/stats.html', context)

async def search(request):
    if request.method == "POST":
        form = UsernameForm(request.POST)
        if form.is_valid():
            return redirect(f'{form.cleaned_data["username"]}/')
        else:
            return render(request, 'stats/search.html', {'form': UsernameForm()})
    else:
        form = UsernameForm()
        return render(request, 'stats/search.html/', {'form': form})