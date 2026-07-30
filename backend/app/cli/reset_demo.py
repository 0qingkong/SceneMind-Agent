from __future__ import annotations

import argparse
import json

from app.core.config import Settings
from app.db import Database
from app.services.demo_data import DemoDataService
from app.services.image_storage import ImageStorage


def main() -> None:
    parser = argparse.ArgumentParser(description="Remove only marked SceneMind demo data.")
    parser.add_argument("--confirm-reset", action="store_true", required=True)
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args()

    settings = Settings.from_env()
    database = Database(settings.database_url)
    database.create_tables()
    with database.session_factory() as session:
        result = DemoDataService(session, ImageStorage(settings.scene_storage_dir)).reset()
    if args.json_output:
        print(json.dumps(result.to_dict(), ensure_ascii=False))
    else:
        print(
            f"Removed {result.removed_observations} demo observation(s), "
            f"{result.removed_sessions} demo session(s), and "
            f"{result.removed_files} demo image file(s)."
        )
        print("User data was not selected by this operation.")


if __name__ == "__main__":
    main()
