@echo off

set script_dir=%~dp0
set root_dir=%script_dir%..\
set db_file=%root_dir%bookie.db

set dataset_name=best_books_dataset.csv
set dataset_path=%script_dir%%dataset_name%

set database_name=bookie.db
set database_path=%root_dir%%database_name%

echo Script directory: %script_dir%
echo Root directory: %root_dir%
echo Dataset path: %dataset_path%& echo.

echo Checking if %dataset_name% exists in the script directory...
if not exist %dataset_path% (
    echo  %dataset_name% not found. Exiting...
    pause
    exit /b 1
)
echo %dataset_name% exists.& echo.

echo Checking if %database_name% exists in the root directory...
if not exist %database_path% (
    echo %database_name% not found. Creating one...
    sqlite3 %database_name% ""
    echo %database_name% created.& echo.
    pause
)
echo %database_name% exists.& echo.

echo Dropping `books` table...
sqlite3 %db_file% "DROP TABLE IF EXISTS books;"
echo `books` table deleted.& echo.

echo Creating `books` table...
sqlite3 %db_file% < %script_dir%setup.sql
echo Done creating `books` table.& echo.

echo Syncing database with Flask-Migrate...
echo flask db upgrade.& echo.
flask db upgrade
echo Done.& echo.

echo Importing into the database...
sqlite3 %db_file% ".mode csv" ".import %dataset_path% books"
echo Done importing %dataset_name%.& echo.

echo Database setup + sync completed successfully.
pause
