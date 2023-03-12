API="3c8d2ac588340d64abe350b385582417"
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///my_top_movies.db"
db = SQLAlchemy(app)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable=False)
    def __init__(self, title, year, description, rating, ranking, review, img_url):
        self.title=title
        self.year=year
        self.description=description
        self.rating=rating
        self.ranking=ranking
        self.review=review
        self.img_url=img_url

with app.app_context():
    db.create_all()

class RateMovieForm(FlaskForm):
    rating = StringField(label='Your Rating Out of 10 e.g.7.5', validators=[DataRequired()])
    review = StringField(label='Your Review', validators=[DataRequired()])
    submit = SubmitField(label="Done")

class AddMovie(FlaskForm):
    title = StringField(label='Movie Title', validators=[DataRequired()])
    submit = SubmitField(label="Add Movie")

@app.route("/")
def home():
    all_movies = Movie.query.order_by(Movie.rating.asc()).all()

    total_movies = len(all_movies)
    for num in range(total_movies):
        all_movies[num].ranking = total_movies
        total_movies -= 1
    db.session.commit()
    return render_template("index.html", movies=all_movies)

@app.route("/edit", methods=["GET", "POST"])
def edit():
    edit_rating=RateMovieForm()
    if edit_rating.validate_on_submit():
        movie_id = request.args.get("id")
        movie_to_update = Movie.query.get(movie_id)
        movie_to_update.rating = float(edit_rating.rating.data)
        movie_to_update.review = edit_rating.review.data
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("edit.html", form=edit_rating)
@app.route("/delete")
def delete():
    movie_id = request.args.get("id")
    movie_to_delete = Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/add", methods=["GET", "POST"])
def add():
    add_movie=AddMovie()

    if add_movie.validate_on_submit():
        movie_title=add_movie.title.data
        parameters = {
            "api_key": API,
            "query": movie_title
        }
        response = requests.get(url="https://api.themoviedb.org/3/search/movie", params=parameters)
        data = response.json()["results"]
        return render_template("select.html", options=data)

    return render_template("add.html", form=add_movie)
@app.route("/find")
def find_movie():
    movie_api_id = request.args.get("id")
    if movie_api_id:
        parameters={
            "api_key": API,
            "language": "en-US",
        }
        response_find_movie=requests.get(url=f"https://api.themoviedb.org/3/movie/{movie_api_id}", params=parameters)
        movie_data=response_find_movie.json()
        new_movie=Movie(
            title=movie_data["title"],
            img_url=f"https://image.tmdb.org/t/p/w500/{movie_data['poster_path']}",
            year=movie_data["release_date"].split("-")[0],
            description=movie_data["overview"],
            ranking="9",
            rating="6",
            review="good"
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for("edit", id=new_movie.id))

if __name__ == '__main__':
    app.run(debug=True)
