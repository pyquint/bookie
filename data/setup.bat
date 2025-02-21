@echo off

set db_dir="..\instance"
set db_file="%db_dir%\bookie.db"
set dataset="best_books_dataset.csv"

echo Deleting existing bookie.db file...
if exist %db_file% (
    del %db_file%
)

echo Checking if setup.sql exists...
if not exist setup.sql (
    echo 'setup.sql' file does not exist. Exiting...
    pause
    exit /b 1
)

echo Checking if the dataset csv ("best_books_dataset.csv") file exists...
if not exist %dataset% (
    echo "Dataset file not found. Exiting..."
    pause
    exit /b 1
)

echo Check if instance folder exists...
if not exist %db_dir% (
    echo 'instance' folder does not exist. Creating it now...
    mkdir %db_dir%
)

echo Running setup.sql...
sqlite3 %db_file% < "setup.sql"


echo Checking if fts.sql exists...
if not exist fts.sql (
    echo 'fts.sql' file does not exist. Exiting...
    pause
    exit /b 1
)


echo Importing database...
sqlite3 %db_file% ".mode csv" ".import %dataset% books"


echo Initializing FTS5...
sqlite3 %db_file% < "fts.sql"


echo Database setup completed successfully.
pause
