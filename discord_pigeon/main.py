import argparse
import asyncio
import datetime
import logging

import discord
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from pydantic import BaseSettings
from pymongo import MongoClient

parser = argparse.ArgumentParser(description="discord-pigeon")
parser.add_argument(
    "-c", "--clear", action="store_true", help="clear all jobs in mongodb."
)
parser.add_argument(
    "-m", "--manual", action="store_true", help="create a `request_vote` job manually."
)
parser.add_argument("-l", "--list_jobs", action="store_true", help="shows job list.")
parser.add_argument("-a", "--announce", action="store_true", help="announce manually.")
args = parser.parse_args()

logging.basicConfig(
    format="%(asctime)s : [%(levelname)s] %(message)s", level=logging.INFO
)


class Settings(BaseSettings):
    mongodb_host: str = "localhost"
    mongodb_user: str
    mongodb_password: str
    discord_channel_id: int
    discord_token: str

    class Config:
        env_file = ".env"


mongo_cli = MongoClient(
    host=Settings().mongodb_host,
    username=Settings().mongodb_user,
    password=Settings().mongodb_password,
    port=27017,
)

jobstore = MongoDBJobStore(client=mongo_cli)
scheduler = AsyncIOScheduler(job_defaults={"misfire_grace_time": 10})
scheduler.add_jobstore(jobstore)
scheduler.start()
client = discord.Client()


# 次の金曜, 土曜のdatetimeを返す
def next_weekend():
    day = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    while day.weekday() != 4:  # 4は金曜日を表す
        day += datetime.timedelta(days=1)
    day2 = day + datetime.timedelta(days=1)
    return day, day2


async def request_vote():
    day, day2 = next_weekend()
    ch = client.get_channel(Settings().discord_channel_id)

    await ch.send(f"{day.strftime('%m/%d')}に参加可能")
    await ch.send(f"{day2.strftime('%m/%d')}に参加可能")


async def announce():
    day, day2 = next_weekend()
    ch = client.get_channel(Settings().discord_channel_id)
    msgs = []
    async for msg in ch.history(limit=50):
        if msg.author == client.user and "に参加可能" in msg.content:
            msgs.append(msg)
        if len(msgs) == 2:
            break

    msgs = msgs[::-1]
    votes = []
    for msg in msgs:
        votes_num = sum(map(lambda x: x.count, msg.reactions))
        votes.append(votes_num)

    if votes[0] >= votes[1]:
        decision = day
    else:
        decision = day2

    await ch.send(f"中央委員会より攻撃命令!\n開始日時: {decision.month}/{decision.day} 21:00")

    trigger = DateTrigger(decision + datetime.timedelta(hours=20, minutes=45))
    scheduler.add_job(start_in_15min, trigger)


async def start_in_15min():
    msg = "戦闘開始15分前です!"
    ch = client.get_channel(Settings().discord_channel_id)
    await ch.send(msg)


def main():
    asyncio.get_event_loop().create_task(client.start(Settings().discord_token))

    cron_is_enabled = any(
        map(lambda x: "Cron" in repr(x.trigger), scheduler.get_jobs())
    )
    if not cron_is_enabled:
        scheduler.add_job(
            request_vote, "cron", week="2-53/2", day_of_week="sun", hour=12, minute=0
        )
        scheduler.add_job(
            announce, "cron", week="*/2", day_of_week="thu", hour=0, minute=0
        )

    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        asyncio.get_event_loop().create_task(client.logout())


if __name__ == "__main__":
    if args.clear:
        scheduler.remove_all_jobs()
        logging.info("all jobs removed.")
    elif args.manual:
        now = datetime.datetime.now()
        trigger = DateTrigger(now + datetime.timedelta(seconds=30))
        scheduler.add_job(request_vote, trigger)
    elif args.announce:
        now = datetime.datetime.now()
        trigger = DateTrigger(now + datetime.timedelta(seconds=30))
        scheduler.add_job(announce, trigger)
    elif args.list_jobs:
        jobs = scheduler.get_jobs()
        for j in jobs:
            logging.info(j)
    else:
        main()
