"""One-at-a-time PDF report queue.

Render's free instance has 0.1 CPU and 512 MB: two WeasyPrint renders at once can exhaust memory, and a
burst (say, launch day) would time out HTTP requests. Requests are therefore accepted immediately, queued,
built one by one by a single worker, and delivered to the user's chat. Quota is charged only on delivery.
"""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Awaitable, Callable

from aiogram import Bot
from aiogram.types import BufferedInputFile
from fastapi.concurrency import run_in_threadpool

log = logging.getLogger(__name__)


@dataclass
class Job:
    uid: int
    kind: str                                   # natal | synastry
    lang: str
    build: Callable[[], tuple[bytes, str, str]]  # -> (pdf, filename, caption); runs in a thread
    on_done: Callable[[], Awaitable[None]]       # charge quota / log usage
    queued_at: float = field(default_factory=lambda: asyncio.get_event_loop().time())


_queue: asyncio.Queue[Job] | None = None
_pending: dict[int, Job] = {}
_running: Job | None = None
_worker: asyncio.Task | None = None


def start(bot: Bot) -> None:
    global _queue, _worker
    _queue = asyncio.Queue()
    _worker = asyncio.create_task(_work(bot))


def busy(uid: int) -> bool:
    return uid in _pending


def position(uid: int) -> int:
    """1 = being built now."""
    if _running and _running.uid == uid:
        return 1
    order = [j.uid for j in list(_queue._queue)] if _queue else []  # noqa: SLF001
    return (order.index(uid) + 1 + (1 if _running else 0)) if uid in order else 0


async def enqueue(job: Job) -> int:
    if job.uid in _pending:
        raise RuntimeError("report_in_progress")
    _pending[job.uid] = job
    await _queue.put(job)
    return position(job.uid)


async def _work(bot: Bot) -> None:
    global _running
    while True:
        job = await _queue.get()
        _running = job
        try:
            pdf, filename, caption = await run_in_threadpool(job.build)
            await bot.send_document(job.uid, BufferedInputFile(pdf, filename), caption=caption)
            await job.on_done()
        except Exception as e:
            log.exception("report %s for %s failed", job.kind, job.uid)
            try:
                await bot.send_message(job.uid, "⚠️ صار خطأ أثناء تجهيز التقرير، وما انحسب عليك. جرّب مرة تانية بعد شوي."
                                       if job.lang == "ar" else
                                       "⚠️ Something went wrong while preparing the report; it was not counted. "
                                       "Please try again shortly.")
            except Exception:
                pass
            del e
        finally:
            _running = None
            _pending.pop(job.uid, None)
            _queue.task_done()
