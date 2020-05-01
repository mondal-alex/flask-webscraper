from app import app
from flask import jsonify

@app.route('/')
def index():
    return ''

@app.route('/test', methods=["GET"])
def test():
    test = 'test succeeded!'
    print(test)
    return jsonify(new_data)
