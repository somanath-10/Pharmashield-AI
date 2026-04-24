from __future__ import annotations

import asyncio

from app.db.session import SessionLocal, init_db
from app.services.demo_data import DemoDataService


async def _run() -> None:
    init_db()
    with SessionLocal() as db:
        created = await DemoDataService().ingest_public_sources(db)
        print(f"Public ingest complete. Records created: {created}")


def main() -> None:
    asyncio.run(_run())


if __name__ == "__main__":
    main()
