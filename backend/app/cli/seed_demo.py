from __future__ import annotations

import argparse
import json

from app.core.config import Settings
from app.db import Database
from app.services.demo_data import DemoDataService
from app.services.image_storage import ImageStorage


def main() -> None:
    parser = argparse.ArgumentParser(description="Idempotently seed SceneMind demo evidence.")
    parser.add_argument("--reset-first", action="store_true")
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args()

    settings = Settings.from_env()
    database = Database(settings.database_url)
    database.create_tables()
    storage = ImageStorage(settings.scene_storage_dir)
    with database.session_factory() as session:
        service = DemoDataService(session, storage)
        reset_result = service.reset() if args.reset_first else None
        seed_result = service.seed()
    payload: dict[str, object] = {"seed": seed_result.to_dict()}
    if reset_result is not None:
        payload["reset"] = reset_result.to_dict()
    if args.json_output:
        print(json.dumps(payload, ensure_ascii=False))
    else:
        print(
            "Demo seed complete: "
            f"inserted {seed_result.inserted_observations} observation(s) and "
            f"{seed_result.inserted_sessions} session(s); "
            f"skipped {seed_result.skipped_observations} observation(s) and "
            f"{seed_result.skipped_sessions} session(s)."
        )
        print("Observation IDs: " + ", ".join(seed_result.demo_observation_ids))
        print("Session IDs: " + ", ".join(seed_result.demo_session_ids))
        print("Sample queries: " + " | ".join(seed_result.sample_queries))


if __name__ == "__main__":
    main()
