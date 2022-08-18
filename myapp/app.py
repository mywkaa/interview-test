import json

from flask import Flask, flash, jsonify, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///titles.sqlite3"
app.config["SONGS_RESULTS_PER_PAGE"] = 3

db = SQLAlchemy(app)


class titles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    artist = db.Column(db.String(200))
    title = db.Column(db.String(200))
    difficulty = db.Column(db.Float)
    level = db.Column(db.Integer)
    released = db.Column(db.String(200))
    rating = db.relationship("ratings", backref="titles", lazy=True)

    def as_dict(self):
        return {row.name: getattr(self, row.name) for row in self.__table__.columns}

    def as_dict_short_info(self):
        return {
            row.name: getattr(self, row.name)
            for row in self.__table__.columns
            if row.name in ["id", "artist", "title", "released"]
        }

    def __repr__(self):
        return f"{self.id} - {self.artist} - {self.title}"


class ratings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer)
    title_id = db.Column(db.Integer, db.ForeignKey("titles.id"))


db.create_all()


@app.route("/songs")
def show_all():
    page = request.args.get("page", type=int)
    per_page = app.config["SONGS_RESULTS_PER_PAGE"]
    if page:
        paginated = titles.query.paginate(page, per_page, False)
        results = {
            "results": [result.as_dict_short_info() for result in paginated.items],
            "pagination": {
                "count": paginated.total,
                "page": page,
                "per_page": per_page,
                "pages": paginated.pages,
            },
        }
        return jsonify(results)

    all_titles = titles.query.all()
    results = [result.as_dict_short_info() for result in all_titles]
    return jsonify(results)


@app.route("/songs/avg/difficulty")
def songs_avg_difficulty():
    level = request.args.get("level", type=int)
    if level:
        titles_by_specific_level = titles.query.filter_by(level=level).all()
        results = [result.as_dict_short_info() for result in titles_by_specific_level]
        return jsonify(results)
    average_difficulty = db.session.query(db.func.avg(titles.difficulty))
    results = {"average_difficulty": average_difficulty.one()[0]}
    return jsonify(results)


@app.route("/songs/search")
def songs_search():
    message = request.args.get("message", type=str)
    if message:
        search_query = titles.query.filter(
            db.or_(
                titles.artist.ilike(f"%{message}%"), titles.title.ilike(f"%{message}%")
            )
        )
        results = [result.as_dict_short_info() for result in search_query.all()]
        return jsonify(results)
    return {"error": "Get parameter 'message' is not set"}, 404


@app.route("/songs/rating", methods=["GET", "POST"])
def songs_rating_add():
    title = titles.query.get_or_404(request.args.get("song_id", type=int))
    rating = request.args.get("rating", type=int)
    if rating < 1 or rating > 5:
        return jsonify({"error": "rating should be >= 1 and less or equal than 5"})
    record = ratings(rating=rating, title_id=title.id)
    db.session.add(record)
    db.session.commit()
    return jsonify({"status": "ok"})


@app.route("/songs/rating/<int:song_id>/")
def songs_rating(song_id):
    title = titles.query.get_or_404(song_id)
    average_rating = db.session.query(db.func.avg(ratings.rating)).filter(
        ratings.title_id == title.id
    )
    min_rating = db.session.query(db.func.min(ratings.rating)).filter(
        ratings.title_id == title.id
    )
    max_rating = db.session.query(db.func.max(ratings.rating)).filter(
        ratings.title_id == title.id
    )
    results = {
        "song_id": title.id,
        "average_rating": average_rating.one()[0],
        "lowest_rating": min_rating.one()[0],
        "highest_rating": max_rating.one()[0],
    }
    return jsonify(results)


if __name__ == "__main__":
    # db.create_all()
    app.run()
