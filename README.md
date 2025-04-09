# Book Catalogue App
This is a web app that allows users to search for books from a [dataset](https://www.kaggle.com/datasets/pooriamst/best-books-ever-dataset) containing 52,478 of the best-ranked books of all time.

Developed in Python and Flask, using SQLite as the database.

# Features
1. Search by **Title**, **Author**, **ISBN**, or **Publisher**.
2. View **book information**, **descriptions**, **ratings**, and more.

# Todo
- [ ] Sanitize dataset (inconsistent date format, duplicate entries, etc.)
- [x] Add advanced search filtering (multiple search criterias, filter by genre or rating, etc.).
- [x] Add flexible sorting of search results, e.g. by rating, publication date, alphabetical, etc.
  - [ ] Sort by ascending or descending order.
- [ ] Implement search keyword autocomplete.
- [ ] Improve web design. Least priority.

# Installation
The process below are specifically for Windows only, but with a few tweaks to the commands they also apply to Unix/macOS or other operating system.

## Prerequisites
- [git](https://git-scm.com/)
- [Python](https://www.python.org/) 3.13.2
- [SQLite](https://www.sqlite.org/) version 3.49.0

## Steps
Follow the steps below to set up your local development environment:

1. Clone the repository then go to the project directory.
```
> git clone https://github.com/pyquint/bookie.git
> cd bookie
```

> The prompt should then look something like this:
> ```
> bookie>
> ```

2. Set up a virtual environment.

```
bookie> python -m venv .venv
```

3. Activate the virtual environment.
```
bookie> .venv\Scripts\activate
```

> The prompt should then look something like this:
> ```
> (.venv) bookie>
> ```

4. Install the required dependencies listed in `requirements.txt`.

```
(.venv) bookie> python -m pip install -r requirements.txt
```

5. Run the setup script.

```
(.venv) bookie> cd data
(.venv) bookie\data> setup.bat
```
or

```
(.venv) bookie> data\setup.bat
```

6. Run the application.
```
(.venv) bookie> flask run
```

7. Open the development server URL (http://127.0.0.1:5000/) on your preferred browser.

8. Enjoy!

# Contribution
Any help to the project are welcome! Although, please follow and/or maintain the particular formatting done by the author. Thank you!
