This document defines the implementation of user accounts in the Bookie app.

# SQLite schema
```sql
CREATE TABLE IF NOT EXISTS users (
    uid INTEGER,
    username TEXT NOT NULL,
    email TEXT NOT NULL,
    date_created TEXT,
    password_hash TEXT,
    PRIMARY KEY (uid, username)
);
```
Sqlite3 does not have a native `DATIMETIME` data type. To circumvent, we store the `date_created` field as a `TEXT` compliant to [ISO 8901](https://en.wikipedia.org/wiki/ISO_8601).

Read also: [SQLite3 Date And Time Functions](https://sqlite.org/lang_datefunc.html)

# WTForms
\[code from: [Unique validator in WTForms with SQLAlchemy models](https://stackoverflow.com/questions/5685831/unique-validator-in-wtforms-with-sqlalchemy-models)]
```python
class Unique(object):
    def __init__(self, model, field, message=None):
        self.model = model
        self.field = field
        if not message:
            message = "This element already exists."
        self.message = message

    def __call__(self, form, field):
        check = self.model.query.filter(self.field == field.data).first()
        if check:
            raise ValidationError(self.message)
```
The `Unique` class is a custom validator to check the presence of a form field value in a specific database table field, and gives an error if so.


```python
class SignupForm(FlaskForm):
        "Username",
        validators=[DataRequired(), Length(min=1, max=16), Unique(User, User.username)],
    )
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Sign Up")
```
The `Unique` class is used here to check the availability of the username in the database.

```python
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    login_cache = BooleanField("Remember Me")
    submit = SubmitField("Login")
```

