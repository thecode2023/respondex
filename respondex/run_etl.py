"""Run the full ETL pipeline: Extract → Transform → Load."""

from scripts.etl.extract import run as extract
from scripts.etl.transform import run as transform
from scripts.etl.load import run as load


def main():
    extract()
    print()
    transform()
    print()
    load()
    print("\n✅ ETL pipeline complete. Database ready at data/respondex.db")


if __name__ == "__main__":
    main()
