from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import re

app = Flask(__name__)

# Configure SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///funny.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Define the regex pattern for password validation
password_regex = re.compile(
    r"^(?=.*\d)"  # At least one digit
    r"(?=.*[a-z])"  # At least one lowercase letter
    r"(?=(?:.*Q){2,})"  # 'Q' at least twice
    r"(?=.*(\d)\1)"  # The same digit twice in a row
    r"(?=.*F)"  # Must include 'F'
    r"(?=.*[\u203C-\u3299\uD83C-\uDBFF\uDC00-\uDFFF])"  # An emoji
    r"(?=.*2024)"  # Must include the current year
    r"(?=.*→)"  # Right-pointing emoji
    r"(?=.*[Α-Ωα-ω])"  # Ancient Greek numeral
    r".{1,13}$"  # Must be less than 14 characters
)


def validate_password(password):
    errors = []

    # 1. Must include a number
    if not re.search(r"\d", password):
        errors.append("Must include a number")

    # 2. Must include a lowercase letter
    if not re.search(r"[a-z]", password):
        errors.append("Must include a lowercase letter")

    # 3. Must include 'Q' at least twice
    if len(re.findall(r"Q", password)) < 2:
        errors.append("Must include 'Q' at least twice")

    # 4. Must use the same number twice in a row
    if not re.search(r"(\d)\1", password):
        errors.append("Must use the same number twice in a row")

    # 5. Must include the letter 'F'
    if not re.search(r"F", password):
        errors.append("Must include the letter 'F'")

    # 6. Must include an emoji
    if not re.search(r"[\u203C-\u3299\uD83C-\uDBFF\uDC00-\uDFFF]", password):
        errors.append("Must include an emoji")

    # 7. Must include the current year (2024)
    if not re.search(r"2024", password):
        errors.append("Must include the current year (2024)")

    # 8. Must be less than 14 characters long
    if len(password) >= 14:
        errors.append("Must be less than 14 characters long")

    # 9. Must include the right-pointing emoji (→)
    if not re.search(r"→", password):
        errors.append("Must include the right-pointing emoji (→)")

    # 10. Must include an ancient Greek numeral (Greek letter)
    if not re.search(r"[Α-Ωα-ω]", password):
        errors.append("Must include an ancient Greek numeral")

    return errors


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form["name"]
        password = request.form["password"]
        errors = validate_password(password)

        # Check if the name is already registered
        existing_user = User.query.filter_by(username=name).first()
        
        if existing_user:
            # Return an error message if the name is already registered
            return render_template("index.html", error="Name is already registered")
        
        new_user = User(username=name, password=password)
        db.session.add(new_user)
        db.session.commit()

        if errors:
            return render_template("index.html", errors=errors)

        # Handle successful sign-up
        return redirect(url_for("success"))

    return render_template("index.html")


@app.route("/success")
def success():
    return "Sign Up Successful!"


@app.route("/name/<username>")
def name(username):
    return render_template("greet.html", name=username)


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
