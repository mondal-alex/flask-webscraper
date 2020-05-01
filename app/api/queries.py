from app.api import bp
from app.models import Query
from app.api.auth import basic_auth
from flask import jsonify
from flask import request

# http POST https://localhost5000/api/queries link1=...,link2=...,
@bp.route('/queries/', methods=["POST"])
def get_JSON():

    # the client will send a dict of format {"link1": link1,...}
    data = request.get_json() or {}

    new_data = {}

    for link_name, link in data.items():

        current_query = Query(link)

        query_dict = current_query.generate_dict()

        new_data[link_name] = query_dict
        
    # return a JSON of format {"link1": query_dict, ...}
    return jsonify(new_data)
