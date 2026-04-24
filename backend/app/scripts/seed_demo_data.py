from __future__ import annotations

from app.db.session import SessionLocal, init_db
from app.services.demo_data import DemoDataService


def main() -> None:
    init_db()
    with SessionLocal() as db:
        created = DemoDataService().seed_demo_dataset(db)
        print(f"Seeded demo dataset. Records created: {created}")


if __name__ == "__main__":
    main()
