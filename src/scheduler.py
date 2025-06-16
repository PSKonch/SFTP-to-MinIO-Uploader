from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio

from src.tasks.tasks import scan_all_servers_task, stream_all_files_task

def start_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(lambda: scan_all_servers_task.send(), 'interval', minutes=5)
    scheduler.add_job(lambda: stream_all_files_task.send(), 'interval', minutes=5)
    scheduler.start()
    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass

if __name__ == "__main__":
    start_scheduler()