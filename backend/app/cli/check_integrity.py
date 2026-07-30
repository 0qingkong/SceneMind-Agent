from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.db import Database
from app.services.data_integrity import DataIntegrityValidator
from app.services.demo_data import DemoDataService
from app.services.image_storage import ImageStorage


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate an isolated SceneMind database and storage root.")
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--storage", type=Path, required=True)
    parser.add_argument("--seed-demo", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    database = Database(f"sqlite:///{args.database.resolve()}")
    database.create_tables()
    storage = ImageStorage(args.storage)
    try:
        with database.session_factory() as session:
            if args.seed_demo:
                DemoDataService(session, storage).seed()
            report = DataIntegrityValidator(session, storage).run()
        payload = report.to_dict()
        if args.json:
            print(json.dumps(payload, ensure_ascii=False))
        else:
            for item in report.checks:
                print(f"{'PASS' if item.passed else 'FAIL'} {item.name}: {item.detail}")
        raise SystemExit(0 if report.ok else 1)
    finally:
        database.engine.dispose()


if __name__ == "__main__":
    main()
