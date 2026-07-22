from app.core.config import Settings
from app.db import Database
from app.services.demo_data import DemoDataService
from app.services.image_storage import ImageStorage


def main() -> None:
    settings = Settings.from_env()
    database = Database(settings.database_url)
    database.create_tables()
    with database.session_factory() as session:
        count = DemoDataService(session, ImageStorage(settings.scene_storage_dir)).seed()
    print(f"Seeded {count} demo observation(s).")


if __name__ == "__main__":
    main()
