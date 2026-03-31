"""CLI runner — executes the full release control demo and prints results."""

from stability.runners.local_demo import print_demo_report, run_demo

__all__ = ["run_demo", "print_demo_report"]

if __name__ == "__main__":
    print_demo_report()
