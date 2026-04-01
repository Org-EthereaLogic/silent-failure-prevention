"""Allow running as: python -m stability.runners"""

from stability.runners.local_demo import main


if __name__ == "__main__":
    raise SystemExit(main())
