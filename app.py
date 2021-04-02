from flask import Flask, render_template, jsonify, request
import requests
from flask_sqlalchemy import SQLAlchemy
import csv

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///AR.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)


class independence(db.Model):
    Rank = db.Column(db.Integer, primary_key=True)
    Restaurant = db.Column(db.String(200))
    Sales = db.Column(db.Integer)
    AverageCheck = db.Column(db.Integer)
    City = db.Column(db.String(200))
    State = db.Column(db.String(200))
    MealsServed = db.Column(db.Integer)

    def __repr__(self)->str:
        return f"{self.Rank}-{self.Restaurant}"


@app.route('/get_cities_data/')
def get_cities_data():
    if not request.args.get('state') == "" or not request.args.get('state') == None:
        state = request.args.get('state')
        print("ss", state)
        _li = independence_city_state_list(state=state)
    else:
        _li = independence_city_state_list()

    return jsonify(_li['_li_city'])


@app.route('/get_rest_data/')
def get_rest_data():
    if not request.args.get('city') == "" or not request.args.get('city') == None:
        city = request.args.get('city')
        _li = independence_list(city=city)
    else:
        _li = independence_list()

    return jsonify(_li['_li_rest'])


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == "POST":
        if request.form['second_rest'] == "":
            rest_2 = None
        else:
            rest_2 = request.form['second_rest']
        if request.form['first_rest'] == "":
            rest_1 = None
        else:
            rest_1 = request.form['first_rest']

    if request.method == "POST":
        print("Post")
        _li = independence_list(rest_1=rest_1, rest_2=rest_2)
        _li1 = _li['_li1']
        _li_rest = _li['_li_rest']
        _li_rest_dropdown = _li['_li_rest_dropdown']
        _li_sales = _li['_li_sales']
        _li_mealserved = _li['_li_mealserved']
    else:
        _li = independence_list()
        _li1 = _li['_li1']
        _li_rest = _li['_li_rest']
        _li_rest_dropdown = _li['_li_rest_dropdown']
        _li_sales = _li['_li_sales']
        _li_mealserved = _li['_li_mealserved']

    list = independence_city_state_list()
    _coordinates_city_list = []
    for obj in _li1:
        if not obj['City'] in _coordinates_city_list:
            _coordinates_city_list.append(obj['City'])
    _li_coordinates = get_coordinates_cities(_coordinates_city_list)

    return render_template('home.html', _li_coordinates=_li_coordinates, _li_city=list['_li_city'],
                           _li_state=list['_li_state'], _li_rest=_li_rest, _li_rest_dropdown=_li_rest_dropdown,
                           _li_mealserved=_li_mealserved, _li_sales=_li_sales, _li1=_li1)


@app.route('/get_state_cities/')
def get_state_cities():
    if not request.args.get('state') == "" or not request.args.get('state') == None:
        state = request.args.get('state')
        print("ss", state)
        _li = states_and_cities(state=state)

    return jsonify(_li['_li_cities'])


@app.route('/yelp_restaurant', methods=['GET', 'POST'])
def yelp_restaurants():
    city = "NYC"

    if request.method == "POST":
        if request.form['city'] == "":
            city = None
        else:
            city = request.form['city']
        if request.form['state'] == "":
            state = None
        else:
            state = request.form['state']
    import requests as rr
    headers = {"Authorization": "Bearer {}".format(
        "1dOK2QsD7sVyIUW47a22y2REDdNPOS-qc_fYmEbx2tKq6a-Wn1C90-BmjpoJrvo9khG94CKtvWiKiU0ERpnCab6ixQIiL5_YJBzkF1lLDIT76_OnHJx1JRIAZCddYHYx")}
    urlpath = 'https://api.yelp.com/v3/businesses/search?location="{}"'.format(city)
    yelp_list = rr.get(url=urlpath, headers=headers)
    yelp_list = yelp_list.json()
    _li_state = states_and_cities()

    return render_template('main_page.html', city=city, _list=yelp_list["businesses"], _li_state=_li_state["_li_state"],
                           _lat=yelp_list["businesses"][0]['coordinates']['latitude'], _lon=yelp_list["businesses"][0]['coordinates']['longitude'])


def states_and_cities(state=None):
    _li_cities = []
    _li_state = []
    headers = {"Authorization": "Bearer {}".format(
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjp7InVzZXJfZW1haWwiOiJmYXNpaDAzMDJAZ21haWwuY29tIiwiYXBpX3Rva2VuIjoicGxNdUd2am9mUFhiVmk3M2k1dFVIWTJjZ21hYTY0M1o5U0tXY1RVMnFfdmNDOVUwUm9MdnZYLVlzdWlHbFpvRG9RZyJ9LCJleHAiOjE2MTc0MjQ2Njh9.8zLEqtKZulitaENr63dst5XEmJXoj-5Csy694v8h8xA"),
        "Accept": "application/json"
    }

    if state:
        citypath = 'https://www.universal-tutorial.com/api/cities/{}'.format(state)
        list_cities = requests.get(url=citypath, headers=headers)
        list_cities =list_cities.json()
        for obj in list_cities:
            _li_cities.append(obj['city_name'])
    else:
        statepath = 'https://www.universal-tutorial.com/api/states/United States'
        list = requests.get(url=statepath, headers=headers)
        list =list.json()
        for obj in list:
            _li_state.append(obj['state_name'])

    return {'_li_state': _li_state, '_li_cities':_li_cities}


def get_coordinates_cities(_li_city):
    _li_cordinates = []
    for city in _li_city:
        url_path = 'http://api.positionstack.com/v1/forward?access_key=0ef7b12f74d53249fdce67d7588c476e&query={}'.format(
            city)
        res = requests.get(url_path).json()
        print("--------------------------")
        print(city)
        try:
            _li_cordinates.append(
                {'city': city, 'latitude': res["data"][0]['latitude'], 'longitude': res["data"][0]['longitude']})
        except:
            pass

    return _li_cordinates


def independence_city_state_list(state=None):
    reader1 = independence.query.all()
    _li_city = []
    _li_state = []
    for row in reader1:
        if state:
            if not row.City in _li_city and row.State == state:
                _li_city.append(row.City)
        else:
            if not row.City in _li_city:
                _li_city.append(row.City)
        if not row.State in _li_state:
            _li_state.append(row.State)

    return {'_li_city': _li_city, '_li_state': _li_state}


def independence_list(rest_1=None, rest_2=None, city=None, state=None):
    reader1 = independence.query.all()
    _li_rest =[]
    if state:
        print("In State")
        for row in reader1:
            if state == row.State:
                _li_rest.append(row.Restaurant)
        return {'_li_rest': _li_rest}

    if city or (city and state):
        print("In city")
        for row in reader1:
            if city == row.City:
                _li_rest.append(row.Restaurant)
        return {'_li_rest': _li_rest}

    _li_rest_dropdown =[]
    _li_sales =[]
    _li_mealserved =[]
    _li1 =[]
    if not rest_1 == None or not rest_2 == None:
        print("Match")
        for row in reader1:
            _li_rest_dropdown.append(row.Restaurant)
            if rest_1 == row.Restaurant or rest_2 == row.Restaurant:
                _li_rest.append(row.Restaurant)
                _li_sales.append(row.Sales)
                _li_mealserved.append(row.MealsServed)
                _li1.append({'Rank': row.Rank, 'Restaurant': row.Restaurant, 'Sales': row.Sales, 'Average Check': row.AverageCheck, 'City': row.City,
                             'State': row.State, 'MealsServed': row.MealsServed})
    else:
        for row in reader1:
            _li_rest.append(row.Restaurant)
            _li_rest_dropdown.append(row.Restaurant)
            _li_sales.append(row.Sales)
            _li_mealserved.append(row.MealsServed)
            _li1.append({'Rank': row.Rank, 'Restaurant': row.Restaurant, 'Sales': row.Sales, 'Average Check': row.AverageCheck, 'City': row.City,
                     'State': row.Sales, 'MealsServed': row.MealsServed})
    return {'_li_rest': _li_rest, '_li_rest_dropdown': _li_rest_dropdown,
            '_li_mealserved': _li_mealserved, '_li_sales': _li_sales, '_li1': _li1}


# import csv
# from app import db, independence
# path1 = 'Independence100.csv'
# reader1 = csv.reader(open(path1, 'rU'))
# for row in reader1:
#     url_path = 'http://api.positionstack.com/v1/forward?access_key=0ef7b12f74d53249fdce67d7588c476e&query={}'.format(
#     res = requests.get(url_path).json()
#     obj = independence(Rank=row[0], Restaurant=row[1], Sales=row[2], AverageCheck=row[3], City=row[4], State=row[5], MealsServed =row[6], Latitude=res["data"][0]['latitude'], Longitude=res["data"][0]['longitude'])
#     db.session.add(obj)
#     db.session.commit()
#    independence.query.all()

if __name__ == '__main__':
    app.run(debug=True)
