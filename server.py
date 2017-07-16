import flask
from flask import request
from flask import jsonify

from flask_cors import CORS, cross_origin

from engines.curl import POW


app = flask.Flask(__name__)
CORS(app)
pow_engine = POW()

@app.route('/attach_to_tangle')
@cross_origin()
def attach_to_tangle():
    global pow_engine

    trunk = request.args.get('trunk')
    branch = request.args.get('branch')
    min_weight_magnitude = int(request.args.get('min_weight_magnitude'))
    tx_trytes = request.args.get('tx_trytes').split(',')

    response = jsonify(result=','.join(pow_engine.attach_to_tangle(trunk, branch, min_weight_magnitude, tx_trytes)))
    return response

if __name__ == '__main__':
    app.run(debug=True)
