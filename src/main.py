import os

from utils import run_calculations


def main():
    os.makedirs("../output", exist_ok=True)

    results = run_calculations()

    for key, rows in results.items():
        print(f"{key}: {len(rows)} rows")


if __name__ == "__main__":
    main()
