from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
from random import choice



app = Flask(__name__)

# CREATE DB
class Base(DeclarativeBase):
    pass
# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)
    
    
    def to_dict(self):
        dictionary = {}
        for data in self.__table__.columns:
            dictionary[data.name] = getattr(self, data.name)
        return dictionary
   


with app.app_context():
    db.create_all()

     


@app.route("/")
def home():
    return render_template("index.html")

@app.route('/random')
def random_route():
    all_data = db.session.execute(db.select(Cafe))
    all_data = all_data.scalars().all()
    data = choice(all_data)
    print(data.to_dict())
    return jsonify(cafe=data.to_dict())

@app.route('/all')
def all_cafes():
    all_data = db.session.execute(db.select(Cafe))
    all_data = all_data.scalars().all()
    res = []
    for data in all_data:
        res.append(data.to_dict())
    print(res)
    return jsonify(res)


@app.route("/search")
def search_loc():
    loc = request.args.get('loc')
    datas = db.session.execute(db.select(Cafe).where(Cafe.location==loc)).scalars().all()
    res = []
    if len(datas) == 0:
        return jsonify(error = {
            "Not found error": "Sorry we don't have a cafe at this location"
        })
    for data in datas:
        res.append(data.to_dict())
    return jsonify(res)
# HTTP POST - Create Record

# HTTP PUT/PATCH - Update Record

# HTTP DELETE - Delete Record


if __name__ == '__main__':
    app.run(debug=True, port=4200)
