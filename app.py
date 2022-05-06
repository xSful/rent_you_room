from flask import Flask, render_template, request, redirect
#from flask_image_alchemy.storages import S3Storage
from flask_sqlalchemy import SQLAlchemy
from cloudipsp import Api, Checkout
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
app.config['UPLOAD_FOLDER'] = 'F:\\programs\\python\\yandex\\flask\\usersImages'
db = SQLAlchemy(app)
#storage = S3Storage()
#storage.init_app(app)

@app.before_first_request
def create_tables():
    db.create_all()

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    isActive = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'Item: {self.title}'


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/main')
def main():
    items = Item.query.order_by(Item.price).all()
    return render_template('main.html', data=items)


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/buy/<int:id>')
def item_buy(id):
    item = Item.query.get(id)

    api = Api(merchant_id=1396424,
              secret_key='test')
    checkout = Checkout(api=api)
    data = {
        "currency": "Rub",
        "amount": str(item.price) + '00'
    }
    url = checkout.url(data).get('checkout_url')
    return redirect(url)

@app.route('/create', methods=['POST', 'GET'])
def create():
    if request.method == "POST":
        title = request.form['title']
        price = request.form['price']
        item = Item(title=title, price=price)
        f = request.files['image']
        f.save(f'{item.title}.jpg')
        os.replace(f'{item.title}.jpg', f'static/{item.title}.jpg')


        try:
            db.session.add(item)
            db.session.commit()
            return redirect('/main')
        except:
            return 'Ошибка при добавлении!'
    else:
        return render_template('create.html')

@app.route('/support')
def support():
    return render_template('support.html')

if __name__ == '__main__':
    app.run(debug=True)
