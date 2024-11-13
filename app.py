import os
from os.path import join, dirname
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.utils import secure_filename

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME =  os.environ.get("DB_NAME")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

app = Flask(__name__)

UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


client = MongoClient("mongodb://test:sparta@cluster0-shard-00-00.czmlq.mongodb.net:27017,cluster0-shard-00-01.czmlq.mongodb.net:27017,cluster0-shard-00-02.czmlq.mongodb.net:27017/?ssl=true&replicaSet=atlas-2vaaub-shard-0&authSource=admin&retryWrites=true&w=majority&appName=Cluster0")
db = client["parfum_reviews_db"]
reviews_collection = db["reviews"]


@app.route('/')
def index():
    reviews = list(reviews_collection.find())
    return render_template('index.html', reviews=reviews)


@app.route('/add_review', methods=['GET', 'POST'])
def add_review():
    if request.method == 'POST':
        nama_parfum = request.form['nama_parfum']
        merek = request.form['merek']
        aroma = request.form['aroma']
        rating = int(request.form['rating'])
        deskripsi = request.form['deskripsi']
        gambar = request.files['gambar']
        if gambar and gambar.filename != '':
            filename = secure_filename(gambar.filename)
            gambar.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            gambar_url = filename 
        else:
            gambar_url = None

        reviews_collection.insert_one({
            'nama_parfum': nama_parfum,
            'merek': merek,
            'aroma': aroma,
            'rating': rating,
            'deskripsi': deskripsi,
            'gambar_url': gambar_url
        })
        return redirect(url_for('index'))

    return render_template('add_review.html')


@app.route('/edit_review/<id>', methods=['GET', 'POST'])
def edit_review(id):
    review = reviews_collection.find_one({'_id': ObjectId(id)})

    if request.method == 'POST':
        nama_parfum = request.form['nama_parfum']
        merek = request.form['merek']
        aroma = request.form['aroma']
        rating = int(request.form['rating'])
        deskripsi = request.form['deskripsi']
        gambar = request.files['gambar']
        if gambar and gambar.filename != '':
            filename = secure_filename(gambar.filename)
            gambar.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            gambar_url = filename
        else:
            gambar_url = review['gambar_url']  

        reviews_collection.update_one(
            {'_id': ObjectId(id)},
            {'$set': {
                'nama_parfum': nama_parfum,
                'merek': merek,
                'aroma': aroma,
                'rating': rating,
                'deskripsi': deskripsi,
                'gambar_url': gambar_url
            }}
        )
        return redirect(url_for('index'))

    return render_template('add_review.html', review=review)

@app.route('/delete_review/<id>')
def delete_review(id):
    reviews_collection.delete_one({'_id': ObjectId(id)})
    return redirect(url_for('index'))

if __name__ == '__main__': 
    app.run('0.0.0.0', port=5000, debug=True)