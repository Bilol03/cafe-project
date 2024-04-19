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

SECRET_KEY = 'TopSecretKey'


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

@app.route('/add', methods=["POST"])
def add_cafe():
    
    if request.method == "POST":
        print(request.form.get('has_toilet'))
        new_cafe = Cafe(
            name = request.form.get('name'),
            map_url = request.form.get('map_url'),
            img_url = request.form.get('img_url'),
            location = request.form.get('location'),
            seats = request.form.get('seats'),
            has_toilet = bool(request.form.get('has_toilet')),
            has_wifi = bool(request.form.get('has_wifi')),
            has_sockets = bool(request.form.get('has_sockets')),
            can_take_calls = bool(request.form.get('can_take_calls')),
            coffee_price = request.form.get('coffee_price')
        )
        print(new_cafe)
        db.session.add(new_cafe)
        db.session.commit()
        return jsonify(responce = {
            "success": "Successfully added the new cafe"
        })
# HTTP PUT/PATCH - Update Record
@app.route('/update-price/<int:id>', methods=["PATCH"])
def update_price(id):
    if request.method == "PATCH":
        price = request.args.get('price')
        print(id, price)
        data = db.get_or_404(Cafe, id)
        if data:
            data.coffee_price = price 
            db.session.commit()
            return jsonify(responce = {
                "success": "Data successfully updated"
            })
    
@app.route("/report-closed/<int:id>", methods = ["DELETE"])
def delete_cafe(id):
    secret_key = request.args.get('api-key')
    if secret_key == SECRET_KEY:
        data = db.get_or_404(Cafe, id)
        if data:
            db.session.delete(data)
            db.session.commit()
            return jsonify(response = {
                "success": "Cafe successfully deleted"
            }), 200
    else:
        return jsonify(error = "Sorry, you are not allowed to delete"), 403
# HTTP DELETE - Delete Record


if __name__ == '__main__':
    app.run(debug=True, port=4200)
