from django.db import models
from .forms import UsernameForm

import aiohttp, aiofiles
import json

class Player(models.Model):
    uuid = models.CharField(max_length=36)
    username = models.CharField(max_length=16)

    def __str__(self):
        return self.uuid

    async def get_uuid(name):
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f'https://api.mojang.com/users/profiles/minecraft/{name}') as r:
                return (await r.json())["id"]

    async def get_name(uuid):
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f'https://api.mojang.com/user/profile/{uuid}') as r:
                return (await r.json())["name"]
                
    async def get_stats(uuid):
        jsondata = open("private.json", "r")
        data = json.load(jsondata)
        form = UsernameForm()
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f'https://api.hypixel.net/player?key={data["apiKey"]}&uuid={uuid}') as r:
                res = await r.json()
                if r.ok and res['player'] != None:
                    
                    username = await Player.get_name(uuid)

                    sw = res['player']['stats']['SkyWars'] if 'SkyWars' in res['player']['stats'] else res['player']
                    sw_kills = int(sw['kills']) if 'kills' in sw else 0
                    sw_deaths = int(sw['deaths']) if 'deaths' in sw else 0
                    sw_wins = int(sw['wins']) if 'wins' in sw else 0
                    sw_losses = int(sw['losses']) if 'losses' in sw else 0

                    bw = res['player']['stats']['Bedwars'] if 'Bedwars' in res['player']['stats'] else res['player']
                    bw_kills = int(bw['kills_bedwars']) if 'kills_bedwars' in bw else 0
                    bw_deaths = int(bw['deaths_bedwars']) if 'deaths_bedwars' in bw else 0
                    bw_wins = int(bw['wins_bedwars']) if 'wins_bedwars' in bw else 0
                    bw_losses = int(bw['losses_bedwars']) if 'losses_bedwars' in bw else 0
                    bw_ws = int(bw['winstreak']) if 'winstreak' in bw else 0
                    bw_final_kills = int(bw['final_kills_bedwars']) if 'final_kills_bedwars' in bw else 0
                    bw_final_deaths = int(bw['final_deaths_bedwars']) if 'final_deaths_bedwars' in bw else 0
                    bw_beds_broken = int(bw['beds_broken_bedwars']) if 'beds_broken_bedwars' in bw else 0
                    bw_beds_lost = int(bw['beds_lost_bedwars']) if 'beds_lost_bedwars' in bw else 0
                    context = {
                        # Misc
                        'form': form,
                        'username': username,
                        'uuid': uuid,
                        # Skywars
                        'sw_kills': sw_kills,
                        'sw_deaths': sw_deaths,
                        'sw_kdr': round(sw_kills / sw_deaths, 2) if sw_kills != 0 and sw_deaths != 0 else 0,
                        'sw_wins': sw_wins,
                        'sw_losses': sw_losses,
                        'sw_wlr': round(sw_wins / sw_losses, 2) if sw_wins != 0 and sw_losses != 0 else 0,
                        # Bedwars
                        'bw_kills': bw_kills,
                        'bw_deaths': bw_deaths,
                        'bw_kdr': round(bw_kills / bw_deaths, 2) if bw_kills != 0 and bw_deaths != 0 else 0,
                        'bw_wins': bw_wins,
                        'bw_losses': bw_losses,
                        'bw_wlr': round(bw_wins / bw_losses, 2) if bw_wins != 0 and bw_losses != 0 else 0,
                        'bw_ws': bw_ws,
                        'bw_final_kills': bw_final_kills,
                        'bw_final_deaths': bw_final_deaths,
                        'bw_fkdr': round(bw_final_kills / bw_final_deaths, 2) if bw_final_kills != 0 and bw_final_deaths != 0 else 0,
                        'bw_beds_broken': bw_beds_broken,
                        'bw_beds_lost': bw_beds_lost,
                        'bw_bblr': round(bw_beds_broken / bw_beds_lost, 2) if bw_beds_broken != 0 and bw_beds_lost != 0 else 0,

                    }
                    return context
                else:
                    pass

    async def get_skin(uuid):
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f"https://crafatar.com/renders/body/{uuid}") as res:
                f = await aiofiles.open(f'res/{uuid}.png', mode='wb')
                await f.write(await res.read())
                await f.close()