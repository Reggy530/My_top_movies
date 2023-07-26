from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
db = SQLAlchemy()
db.init_app(app)

## url for downloading list of movies, it incluses api key etc.
url_moviewebs = "https://api.themoviedb.org/3/search/movie?query="
headers_moviewebs = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI5OTVkNDNjZjdlNTBlYTZkNDI3YzEwNmYxMzljMTQ1MyIsInN1YiI6IjY0YzBmYWM2MDk3YzQ5MDBlM2YzMjljNSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.YgrNpDiXf5i9OeTC8rZrQHsCblMwRDGwWImdALr_tzA"

}
# problem = "Harry Potter i Kamień"
# response = requests.get(url_moviewebs+problem, headers=headers_moviewebs)
#
# print(response.text)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, unique=True)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(4195), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    ranking = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String(255), nullable=False)
    img_url = db.Column(db.String(255), nullable=False)

with app.app_context():
    db.create_all()


class RateMovieForm(FlaskForm):
    rating = StringField("Your Rating Out of 10 e.g. 7.5")
    review = StringField("Your Review")
    submit = SubmitField("Done")


class AddMovieForm(FlaskForm):
    movietitle = StringField("Movie Title")
    submit = SubmitField("Add Movie")

# new_movie = Movie(
#     title="Avatar The Way of Water",
#     year=2022,
#     description="Set more than a decade after the events of the first film, learn the story of the Sully family (Jake, Neytiri, and their kids), the trouble that follows them, the lengths they go to keep each other safe, the battles they fight to stay alive, and the tragedies they endure.",
#     rating=7.3,
#     ranking=9,
#     review="I liked the water.",
#     img_url="https://image.tmdb.org/t/p/w500/t6HIqrRAclMCA60NsSmeqe9RmNV.jpg"
# )
#
# with app.app_context():
#     db.session.add(new_movie)
#     db.session.commit()

@app.route("/",  methods=['GET', 'POST'])
def home():
    if request.method == "POST":
        pass

    movies = Movie.query.order_by(Movie.rating).all()
    pozycja = len(movies)
    for movie in movies:
        movie.ranking = pozycja
        pozycja -= 1

    return render_template("index.html", movies=movies)

@app.route("/edit/<int:id>", methods=['GET', 'POST'])
def edit(id):
    movies = Movie.query.all()
    form = RateMovieForm()
    if request.method == "POST":
        newrating = request.form.get("rating")
        newrev = request.form.get("review")
        movie = Movie.query.get(id)
        movie.rating = newrating
        movie.review = newrev
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("edit.html", movies=movies, id=id, form=form)

@app.route("/edit/new/<title>/<img_url>/<year>/<description>", methods=['GET', 'POST'])
def add_new(title, img_url, year, description):
    print(title, img_url, year, description)

    new_movie = Movie(
        title=title,
        year=year[:4],
        description=description,
        rating=0,
        ranking="None",
        review="",
        img_url="https://image.tmdb.org/t/p/w500/"+img_url
    )

    with app.app_context():
        db.session.add(new_movie)
        db.session.commit()
        redirect(url_for("edit", id=new_movie.id))

    return redirect(url_for("edit", id=new_movie.id))



@app.route("/delete/<int:id>", methods=['GET', 'POST'])
def delete(id):
    movie = Movie.query.get(id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/add", methods=['GET', 'POST'])
def add():
    form = AddMovieForm()
    if request.method == "POST":
        title = request.form.get("movietitle")
        response = requests.get(url_moviewebs + title, headers=headers_moviewebs).text
        response = json.loads(response)
        response = response["results"]
        return render_template("select.html", title=response)
    form = AddMovieForm()
    movies = Movie.query.all()
    return render_template("add.html", movies=movies, form=form)

@app.route("/select", methods=['GET', 'POST'])
def select():
    print('')
    return render_template("select.html")


if __name__ == '__main__':
    app.run(debug=True)
