import aiohttp
import humanize
import time

with open('web_session') as op:
    web_session = op.read()

headers = {
    "Host": "www.quizup.com",
    "Accept": "*/*",
    "Accept-Encoding": "identity",
    "Cookie": f"web_session={web_session}",
    "User-Agent": "UnityPlayer/2018.2.16f1 (UnityWebRequest/1.0, libcurl/7.52.0-DEV)",
    "X-Unity-Version": "2018.2.16f1"
}

follow_headers = {
    "Accept": "application/vnd.plainvanilla.quizup-v2.0.0+json",
    "Accept-Language": "en",
    "User-Agent": "SM-A908N QuizUp Android-7.1.2/4.1.4",
    "QuizUp-Client-Platform": "android",
    "QuizUp-Client-OS-Version": "7.1.2",
    "QuizUp-Client-Version": "4.1.4",
    "QuizUp-Client-App-ID": "com.quizup.core",
    "Quizup-Client-Device": "samsung SM-A908N",
    "Host": "api-android20.quizup.com",
    "Connection": "keep-alive",
    "Accept-Encoding": "gzip",
    "Cookie": f"session={web_session}"
}


class Commands:
    @staticmethod
    async def command_ping(sender):
        t1 = time.perf_counter()

        async with aiohttp.ClientSession() as session:
            async with session.get(
                    "https://www.quizup.com/api/chat",
                    headers=headers
            ) as resp:
                _ = resp.status

        t2 = time.perf_counter()
        diff = round((t2 - t1) * 1000)
        await sender.send(f"Pong! {diff}ms")

    @staticmethod
    async def my_stats(sender):
        data = await utils.get_player_stats(sender)

        if utils.is_private(data):  # Sending follow request is a bit buggy. cant be bothered fixing lul
            await sender.send("Your profile is private. "
                              "Please un-private your profile before running this command again.")

        else:
            msg = utils.format_player_stats(data)
            await sender.send(msg)

    @staticmethod
    async def my_topic_stats(sender, topic_slug):
        data = (await utils.get_player_stats(sender))

        if utils.is_private(data):
            await sender.send("Your profile is private. "
                              "Please un-private your profile before running this command again.")

        else:
            if topic_slug not in data["player"]["topics"].keys():
                return await sender.send("You have not played in this topic yet (or this topic does not exist)")

            msg = utils.format_player_topic_stats(data["player"]["topics"][topic_slug])
            await sender.send(msg)


class Utils:  # Prepare to see code gore
    @staticmethod
    def is_private(data):
        return data["player"]["private"] and not data["player"]["is_followed_by_me"]

    @staticmethod
    def format_player_topic_stats(data):
        games_played = humanize.intcomma(data["games_played"])
        avg_resp_time = round(data["average_response_time"], 4)
        total_xp = humanize.intcomma(data["total_xp"])
        level = humanize.intcomma(data["xp_level"]["level"])

        wins = humanize.intcomma(data["total_wins"])
        draws = humanize.intcomma(data["total_draws"])
        loss = humanize.intcomma(data["total_losses"])
        surrender = humanize.intcomma(data["total_surrenders"])
        disconnects = humanize.intcomma(data["total_network_errors"])

        winpc = round(data["total_wins"] / data["games_played"] * 100, 2)
        drawpc = round(data["total_draws"] / data["games_played"] * 100, 2)
        losepc = round(data["total_losses"] / data["games_played"] * 100, 2)

        sp_count = humanize.intcomma(data["survival_game_count"])
        sp_hs = humanize.intcomma(data["survival_high_score"])
        sp_total_xp = humanize.intcomma(data["survival_total_xp"])

        fmt = f"""Games played: {games_played}
Games won: {wins} (~{winpc}%)
Games drawn: {draws} (~{drawpc}%)
Games lost: {loss} (~{losepc}%)
Surrenders: {surrender}
Disconnections: {disconnects}
Total xp: {total_xp}

Average response time: {avg_resp_time}
Topic level: {level}

Number of singleplayer games: {sp_count}
Singleplayer highscore: {sp_hs}
Total xp gained from singleplayer: {sp_total_xp}"""
        return fmt

    @staticmethod
    def format_player_stats(data):
        player = data["player"]

        total_play = humanize.intcomma(player["games_played_total"])
        total_wins = humanize.intcomma(player["games_won_total"])
        total_draw = humanize.intcomma(player["games_drawn_total"])
        total_loss = humanize.intcomma(player["games_lost_total"])

        winpc = round(player["games_won_total"] / player["games_played_total"] * 100, 2)
        drawpc = round(player["games_drawn_total"] / player["games_played_total"] * 100, 2)
        losepc = round(player["games_lost_total"] / player["games_played_total"] * 100, 2)

        total_exp = humanize.intcomma(player["ulp"]["cumulativeXp"])
        total_scrolls = humanize.intcomma(player["reputation_points"])
        echelon = player["ulp"]["unifiedLevel"]

        followers = humanize.intcomma(player["follower_total"])
        following = humanize.intcomma(player["following_total"])

        fmt = f"""Games played: {total_play}
Games won: {total_wins} (~{winpc}%)
Games drawn: {total_draw} (~{drawpc}%)
Games lost: {total_loss} (~{losepc}%)
Total xp: {total_exp}

Echelon: {echelon}
Scrolls: {total_scrolls}

Followers: {followers}
Following: {following}"""

        return fmt

    @staticmethod
    async def get_player_stats(sender):
        url = "https://www.quizup.com/api/players/" + sender.uid

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                data = await resp.json()

        return data


utils = Utils()
commands = Commands()
