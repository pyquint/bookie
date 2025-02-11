# Book Catalogue App
This is a web app that allows users to search for books from a [dataset](https://www.kaggle.com/datasets/pooriamst/best-books-ever-dataset) containing 52,478 of the best-ranked books of all time.

Developed in Python and Flask, using SQLite as the database.

# Features
1. Search by **Title**, **Author**, **ISBN**, or **Publisher**.
2. View **book information**, **descriptions**, **ratings**, and more.

# Todo
- [ ] Add advanced search filtering (multiple search criterias, filter by genre or rating, etc.).
- [ ] Add flexible sorting of search results, e.g. by rating, publication date, alphabetical, etc.
- [ ] Implement search keyword autocomplete.
- [ ] Improve web design. Least priority.

# Development Setup
Controbutions to the project are welcome! The steps below are for Windows only, but with a few tweaks, they can apply to Unix/macOS.

Follow the steps below to set up your local development environment:

1. Create a prject directory and set up a virtual environment.

```
> cd path\to\bookie
> python -m venv .venv
```

2. Activate the virtual environment.
```
> .venv\Scripts\activate
```

3. Install required dependencies listed in `requirements.txt`.

```
> python -m pip install -r requirements.txt
```

4. Initialize the database. Navigate to the `data` folder and run the setup script.
5.
```
> cd path\to\bookie\data
> setup.bat
```

Any help is greatly appreciated!
