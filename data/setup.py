import ast
import csv
import os
import shutil
import subprocess
import sys
from pathlib import Path
from sqlite3 import IntegrityError

root_dir = Path(__file__).resolve().parents[1]
sys.path.append(str(root_dir))


from app.models import Author, Award, Character, Genre, Publisher, ReadingStatus
from bookie import Book, app, db


def get_or_create(model, **kwargs):
    instance = db.session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    instance = model(**kwargs)
    db.session.add(instance)
    return instance


def parse_list_field(value: str):
    """Parses the field stored in the database as a list of values.
    `value` is either formatted as `["a", "b", "c"]` or `"a, b, c"`"""
    if not value:
        return []
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        # `set` prevents IntegrityError
        return set(ast.literal_eval(value))
    return (val for val in value.split(","))


def parse_numeric(value: str, numtype=float):
    try:
        value = numtype(value)
        return value
    except ValueError:
        return 0.0


def import_books(csv_path, batch_size=1000):
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        batch = set()

        for row in reader:
            print(f"Importing book {row["title"]}...")

            existing_book = db.session.get(Book, row["id"])

            if existing_book:
                print("\tAlready exists. Skipping...")
                continue

            authors = [
                get_or_create(Author, name=name)
                for name in parse_list_field(row["author"])
            ]
            genres = [
                get_or_create(Genre, name=name)
                for name in parse_list_field(row.get("genres", ""))
            ]
            characters = [
                get_or_create(Character, name=name)
                for name in parse_list_field(row.get("characters", ""))
            ]
            awards = [
                get_or_create(Award, name=name)
                for name in parse_list_field(row.get("awards", ""))
            ]
            publisher = get_or_create(Publisher, name=row.get("publisher"))

            book = Book(
                id=row["id"],
                title=row["title"],
                series=row.get("series"),
                rating=parse_numeric(row.get("rating", 0), float),
                description=row.get("description"),
                language=row.get("language"),
                isbn=row.get("isbn"),
                book_format=row.get("book_format"),
                edition=row.get("edition"),
                pages=row.get("pages"),
                publish_date=row.get("publish_date"),
                first_publish_date=row.get("first_publish_date"),
                num_ratings=parse_numeric(row.get("num_ratings", 0), int),
                ratings_by_stars=row.get("ratings_by_stars"),
                liked_percent=parse_numeric(row.get("liked_percent", 0), float),
                setting=row.get("setting"),
                cover_img=row.get("cover_img"),
                bbe_score=row.get("bbe_score"),
                bbe_votes=row.get("bbe_votes"),
                price=parse_numeric(row.get("price", 0), float),
            )

            db.session.add(book)

            book.authors.extend(authors)
            book.genres.extend(genres)
            book.characters.extend(characters)
            book.awards.extend(awards)

            book.publisher = publisher

            batch.add(book)

            if len(batch) >= batch_size:
                db.session.commit()
                batch = set()

        if batch:
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
        print("No .db file found\n")
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
