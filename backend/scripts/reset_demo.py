import sys

from app.cli.reset_demo import main


if __name__ == "__main__":
    if "--confirm-reset" not in sys.argv:
        sys.argv.append("--confirm-reset")
    main()
