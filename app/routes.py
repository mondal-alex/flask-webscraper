from app import app
from flask import jsonify
from google.cloud import datastore
from models import store_time,fetch_times

datastore_client = datastore.Client()

@app.route('/')
@app.route('/index')
def index():
    # Store the current access time in Datastore.
    store_time(datetime.datetime.now())

    # Fetch the most recent 10 access times from Datastore.
    times = fetch_times(10)

    return render_template(
        'index.html', times=times)

@app.route('/hello', methods=["GET"])
def test():
    new_data = 'hello'
    print('hello')
    return jsonify(new_data)
