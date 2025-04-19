import ast
import csv
import os
import shutil
import subprocess
import sys
from pathlib import Path
from sqlite3 import IntegrityError

import sqlalchemy as sa

root_dir = Path(__file__).resolve().parents[1]
sys.path.append(str(root_dir))


from app.models import (
    Author,
    Award,
    Character,
    Genre,
    Publisher,
    ReadingStatus,
    Setting,
)
from bookie import Book, app, db


def get_or_create(model, **kwargs):
    instance = db.session.scalar(sa.select(model).filter_by(**kwargs))
    if instance:
        return instance
    instance = model(**kwargs)
    db.session.add(instance)
    return instance


def parse_list_field(value: str, duplicates=False):
    """Parses the field stored in the database as a list of values.
    `value` is either formatted as `["a", "b", "c"]` or `"a, b, c"`"""
    if not value:
        return []
    if value.startswith("[") and value.endswith("]"):
        if duplicates:
            return (x.strip() for x in ast.literal_eval(value))
        seen = set()
        return (
            x.strip() for x in ast.literal_eval(value) if not (x in seen or seen.add(x))
        )
    return (x.strip() for x in value.split(","))


def num_or_none(value: str, numtype):
    try:
        return numtype(value)
    except (ValueError, TypeError):
        return None


def import_books(csv_path, batch_size=1000):
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        batch_count = 0

        for row in reader:
            print(f"Importing book {row["title"]}...")

            existing_book = db.session.get(Book, row["id"])

            if existing_book:
                print("\tAlready exists. Skipping...")
                continue

            authors = (
                get_or_create(Author, name=name)
                for name in parse_list_field(row["author"])
            )
            genres = (
                get_or_create(Genre, name=name)
                for name in parse_list_field(row["genres"])
            )
            characters = (
                get_or_create(Character, name=name)
                for name in parse_list_field(row["characters"])
            )
            awards = (
                get_or_create(Award, name=name)
                for name in parse_list_field(row["awards"])
            )
            settings = (
                get_or_create(Setting, name=name)
                for name in parse_list_field(row["setting"])
            )
            publisher = get_or_create(Publisher, name=row["publisher"])

            ratings_by_stars = [
                int(n) for n in ast.literal_eval(row["ratings_by_stars"])
            ]

            # to ensure ratings_by_stars has 5 elements (fill with 0)
            if (length := len(ratings_by_stars)) < 5:
                ratings_by_stars = ratings_by_stars + [0] * (5 - length)

            book = Book(
                id=row["id"],
                title=row["title"],
                series=row["series"],
                description=row["description"],
                language=row["language"],
                isbn=row["isbn"],
                book_format=row["book_format"],
                edition=row["edition"],
                publish_date=row["publish_date"],
                first_publish_date=row["first_publish_date"],
                five_star_ratings=ratings_by_stars[0],
                four_star_ratings=ratings_by_stars[1],
                three_star_ratings=ratings_by_stars[2],
                two_star_ratings=ratings_by_stars[3],
                one_star_ratings=ratings_by_stars[4],
                cover_img=row["cover_img"],
                rating=num_or_none(row["rating"], float),
                pages=num_or_none(row["pages"], int),
                num_ratings=num_or_none(row["num_ratings"], int),
                liked_percent=num_or_none(row["liked_percent"], float),
                bbe_score=num_or_none(row["bbe_score"], int),
                bbe_votes=num_or_none(row["bbe_votes"], int),
                price=num_or_none(row["price"], float),
            )

            db.session.add(book)

            book.authors.extend(authors)
            book.genres.extend(genres)
            book.characters.extend(characters)
            book.awards.extend(awards)
            book.settings.extend(settings)

            book.publisher = publisher

            batch_count += 1

            if batch_count >= batch_size:
                db.session.commit()
                batch_count = 0

        if batch_count > 0:
            db.session.commit()


if __name__ == "__main__":

    def run_command(command, shell=True, check=True):
        print(f"> {command}")
        result = subprocess.run(command, shell=shell, check=check, capture_output=True)
        print(result.stdout.decode())
        if result.stderr:
            print(result.stderr.decode())

    # https://stackoverflow.com/a/3430395
    script_dir = Path(__file__).parent.resolve()
    root_dir = script_dir.parent
    db_file = os.path.join(root_dir, "bookie.db")

    dataset_name = "best_books_dataset.csv"
    dataset_path = os.path.join(script_dir, dataset_name)

    database_name = "bookie.db"
    database_path = os.path.join(root_dir, database_name)

    print(f"\nScript directory: {script_dir}")
    print(f"Root directory: {root_dir}")
    print(f"Dataset path: {dataset_path}\n\n")

    print("Deleting .db file and .\\migrations folder...\n")
    if os.path.exists(database_path):
        os.remove(database_path)
    shutil.rmtree("migrations")
    print("Done!\n")

    run_command("flask db init")
    run_command("flask db migrate")
    run_command("flask db upgrade")

    print(f"Checking if {dataset_name} exists in the script directory...")
    if not os.path.exists(dataset_path):
        print(f"{dataset_name} not found. Exiting...")
        sys.exit(1)
    print(f"{dataset_name} exists.\n")

    print("Syncing database with Flask-Migrate...")
    run_command("flask db upgrade")
    print("Done.\n")

    with app.app_context():
        print("Populating 'reading_statuses' table...")
        plan_to_read = ReadingStatus(name="Plan to Read")
        currently_reading = ReadingStatus(name="Currently Reading")
        finished = ReadingStatus(name="Finished")
        dropped = ReadingStatus(name="Dropped")
        db.session.add_all((plan_to_read, currently_reading, finished, dropped))
        db.session.commit()
        print("Done!\n")

        print("Populating 'books' table...")
        import_books(app.config["DATASET_PATH"])
        print("Done!\n")

    print("Database setup completed successfully.")
