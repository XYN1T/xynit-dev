from django.db import models
from .forms import UsernameForm

import aiohttp, aiofiles
import json
import math

class Player(models.Model):
    uuid = models.CharField(max_length=36)
    username = models.CharField(max_length=16)

    def __str__(self):
        return self.username

    async def get_uuid(name):
        session = aiohttp.ClientSession()
        async with session.get(f'https://api.mojang.com/users/profiles/minecraft/{name}') as r:
            await session.close()
            return (await r.json())["id"]

    async def get_name(uuid):
        session = aiohttp.ClientSession()
        async with session.get(f'https://api.mojang.com/user/profile/{uuid}') as r:
            await session.close()
            return (await r.json())["name"]
    
    async def get_exp_needed_sw(level, xp):
        spreadsheet = [20, 70, 150, 250, 500, 1000, 2000, 3500, 6000, 10000]
        if level < 11:
            return spreadsheet[level] - xp
        else:
            return (15000 + (level - 11) * 10000) - xp

    async def get_exp_needed_bw(level, xp):
        spreadsheet = [500, 100, 1500, 3000, 3500, 5000]
        if level < 6:
            return spreadsheet[level] - xp
        elif level >= 100:
            factor_str = str(level)[:-2]
            factor = int(factor_str) + 1
            return xp - ((13000 * factor) + (level - (factor * 5)) * 5000)
        else:
            return xp - (13000 + (level - 5) * 5000)
                
    async def get_stats(uuid):
        jsondata = open("private.json", "r")
        data = json.load(jsondata)
        form = UsernameForm()
        session = aiohttp.ClientSession()
        async with session.get(f'https://api.hypixel.net/player?key={data["apiKey"]}&uuid={uuid}') as r:
            res = await r.json()
            if r.ok and res['player'] != None:
                username = await Player.get_name(uuid)

                if "rank" in res["player"] and res["player"]["rank"] != "NORMAL":
                    rank = res["player"]["rank"]
                elif "newPackageRank" in res["player"]:
                    rank = res["player"]["newPackageRank"]
                elif "packageRank" in res["player"]:
                    rank = res["player"]["packageRank"]
                else:
                    rank = "NON"
                if rank == "MVP_PLUS":
                    rank = "MVP+"

                exp = res['player']['networkExp'] if 'networkExp' in res['player'] else 0
                networklevel = (math.sqrt((2 * exp) + 30625) / 50) - 2.5
                networklevel = round(networklevel, 2)

                totalquests = 0
                for game in res["player"]["quests"]:
                    for quest in res["player"]["quests"][game]:
                        if quest == "completions":
                            for completion in res["player"]["quests"][game]["completions"]:
                                totalquests += len(completion)

                challenges = 0
                for challenge in res['player']['challenges']['all_time']:
                    challenges += res['player']['challenges']['all_time'][challenge]

                karma_unformatted = res['player']['karma']
                karma = format(karma_unformatted, ",")

                achievement_points = res['player']['achievementPoints'] if 'achievementPoints' in res['player'] else 0

                sw = res['player']['stats']['SkyWars'] if 'SkyWars' in res['player']['stats'] else res['player']
                sw_kills = int(sw['kills']) if 'kills' in sw else 0
                sw_deaths = int(sw['deaths']) if 'deaths' in sw else 0
                sw_kdr = round(sw_kills / sw_deaths, 2) if sw_kills != 0 and sw_deaths != 0 else 0
                sw_next_kdr = math.ceil(sw_kdr) - 0.5 if sw_kdr > 5 else math.floor(sw_kdr) + 0.5
                sw_kills_needed_kdr = round(sw_next_kdr * sw_deaths - sw_kills, 2)
                sw_wins = int(sw['wins']) if 'wins' in sw else 0
                sw_losses = int(sw['losses']) if 'losses' in sw else 0
                sw_wlr = round(sw_wins / sw_losses, 2) if sw_wins != 0 and sw_losses != 0 else 0
                sw_next_wlr = (((sw_wlr % 0.10) - 0.1) * -1)  + sw_wlr
                sw_wins_needed_wlr = round(sw_next_wlr * sw_losses - sw_wins, 2)
                sw_star = sw['levelFormatted'] if 'levelFormatted' in sw else 'N/A'
                sw_exp = sw['skywars_experience'] if 'skywars_experience' in sw else 0
                sw_exp_needed = await Player.get_exp_needed_sw(int(sw_star[2:-1]), sw_exp)
                sw_wins_needed_levelup = sw_exp_needed / 13

                bw = res['player']['stats']['Bedwars'] if 'Bedwars' in res['player']['stats'] else res['player']
                bw_level = res['player']['achievements']['bedwars_level'] if 'bedwars_level' in res["player"]["achievements"] else 0
                bw_kills = int(bw['kills_bedwars']) if 'kills_bedwars' in bw else 0
                bw_deaths = int(bw['deaths_bedwars']) if 'deaths_bedwars' in bw else 0
                bw_wins = int(bw['wins_bedwars']) if 'wins_bedwars' in bw else 0
                bw_losses = int(bw['losses_bedwars']) if 'losses_bedwars' in bw else 0
                bw_ws = int(bw['winstreak']) if 'winstreak' in bw else 0
                bw_final_kills = int(bw['final_kills_bedwars']) if 'final_kills_bedwars' in bw else 0
                bw_final_deaths = int(bw['final_deaths_bedwars']) if 'final_deaths_bedwars' in bw else 0
                bw_beds_broken = int(bw['beds_broken_bedwars']) if 'beds_broken_bedwars' in bw else 0
                bw_beds_lost = int(bw['beds_lost_bedwars']) if 'beds_lost_bedwars' in bw else 0
                bw_exp = int(bw["Experience"]) if "Experience" in bw else 0
                bw_exp_needed = await Player.get_exp_needed_bw(bw_level, bw_exp)
                context = {
                    # Misc
                    'form': form,
                    'username': username,
                    'uuid': uuid,
                    # Network
                    'network_level': networklevel,
                    'quests': format(totalquests, ','),
                    'karma': karma,
                    'achievement_points': format(achievement_points, ','),
                    'challenges': format(challenges, ','),
                    # Skywars
                    'sw_kills': sw_kills,
                    'sw_deaths': sw_deaths,
                    'sw_kdr': sw_kdr,
                    'sw_wins': sw_wins,
                    'sw_losses': sw_losses,
                    'sw_wlr': sw_wlr,
                    'sw_star': sw_star[2:],
                    'sw_next_star': int(sw_star[2:-1]) + 1,
                    'sw_exp_needed': format(sw_exp_needed, ','),
                    'sw_wins_needed_levelup': round(sw_wins_needed_levelup, 1),
                    'sw_wins_needed_wlr': sw_wins_needed_wlr,
                    'sw_next_wlr': sw_next_wlr,
                    'sw_next_kdr': sw_next_kdr,
                    'sw_kills_needed_kdr': sw_kills_needed_kdr,
                    # Bedwars
                    'bw_level': bw_level,
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
                    'bw_exp': bw_exp,
                    'bw_exp_needed': format(bw_exp_needed, ','),
                    'bw_next_level': bw_level + 1,

                }
                if rank != "NONE":
                    context['rank'] = rank
                jsondata.close()
                await session.close()
                return context
            else:
                pass

    async def get_skin(uuid):
        session = aiohttp.ClientSession()
        async with session.get(f"https://crafatar.com/renders/body/{uuid}") as res:
            f = await aiofiles.open(f'res/{uuid}.png', mode='wb')
            await f.write(await res.read())
            await f.close()
            await session.close()
