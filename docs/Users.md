This document defines the implementation of user accounts in the Bookie app.

# User schema
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

```python
class User(db.Model, UserMixin):
    __tablename__ = "users"

    uid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    email = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.Text, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
```

Sqlite3 does not have a native `DATIMETIME` data type. To circumvent, we store the `date_created` field as a `TEXT` compliant to [ISO 8901](https://en.wikipedia.org/wiki/ISO_8601).

See also: [SQLite3 Date And Time Functions](https://sqlite.org/lang_datefunc.html)



# WTForms
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

