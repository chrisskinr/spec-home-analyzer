"""
Spec Home Analyzer - Flask Application
Helps identify spec home opportunities in Oak Brook area
"""

from flask import Flask, render_template, request, jsonify, session
from zillow_api import ZillowAPI
import json

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.secret_key = 'ethos-spec-home-analyzer-2025'

api = ZillowAPI()


@app.route('/')
def index():
    """Home page - property search"""
    return render_template('index.html')


@app.route('/api/search/teardowns')
def search_teardowns():
    """API: Search for teardown candidates"""
    max_price = request.args.get('max_price', 1000000, type=int)
    page = request.args.get('page', 1, type=int)
    city = request.args.get('city', type=str)

    results = api.get_teardown_candidates(max_price=max_price, page=page, city=city)
    return jsonify(results)


@app.route('/api/search/sold-comps')
def search_sold_comps():
    """API: Get sold properties for comps"""
    page = request.args.get('page', 1, type=int)
    results = api.get_sold_comps(page=page)
    return jsonify(results)


@app.route('/api/search/new-construction')
def search_new_construction():
    """API: Get new construction comps"""
    min_year = request.args.get('min_year', 2015, type=int)
    page = request.args.get('page', 1, type=int)
    results = api.get_new_construction_comps(min_year=min_year, page=page)
    return jsonify(results)


@app.route('/api/analyze', methods=['POST'])
def analyze_property():
    """API: Analyze a selected property"""
    data = request.json
    property_data = data.get('property')

    # Get comps for analysis
    sold_comps = api.get_sold_comps(page=1).get('results', [])[:20]
    nc_comps = api.get_new_construction_comps(page=1).get('results', [])[:20]

    analysis = api.analyze_property(property_data, sold_comps, nc_comps)
    return jsonify(analysis)


@app.route('/api/property/details')
def get_property_details():
    """API: Get detailed property info including schools"""
    zpid = request.args.get('zpid', type=str)

    if not zpid:
        return jsonify({'error': 'zpid required'}), 400

    details = api.get_property_details(zpid)
    school_info = api.extract_school_district(details)

    return jsonify({
        'success': True,
        'zpid': zpid,
        'schools': details.get('schools', []),
        'school_district': school_info
    })


@app.route('/api/comps/nearby')
def get_nearby_comps():
    """API: Get sales in the same city within radius"""
    lat = request.args.get('lat', type=float)
    lng = request.args.get('lng', type=float)
    city = request.args.get('city', type=str)
    radius = request.args.get('radius', 1.0, type=float)  # Default 1 mile

    if not lat or not lng:
        return jsonify({'error': 'lat and lng required'}), 400

    # Get sold properties from ALL pages, searching specifically in the city
    all_results = []
    for page in range(1, 40):  # Fetch up to 40 pages (~1600 results)
        sold = api.get_sold_comps(page=page, city=city)
        if sold.get('results'):
            all_results.extend(sold.get('results', []))
        if not sold.get('results') or len(sold.get('results', [])) < 40:
            break  # No more pages

    sold = {'success': True, 'results': all_results}

    # Calculate distance for all properties
    all_comps = []
    for prop in sold.get('results', []):
        # Filter by city
        prop_city = prop.get('address', {}).get('city', '').lower()
        if city and prop_city != city.lower():
            continue

        prop_lat = prop.get('latLong', {}).get('latitude')
        prop_lng = prop.get('latLong', {}).get('longitude')

        if not prop_lat or not prop_lng:
            continue

        # Simple distance calculation (approximate miles)
        lat_diff = abs(lat - prop_lat) * 69  # ~69 miles per degree lat
        lng_diff = abs(lng - prop_lng) * 55  # ~55 miles per degree lng at this latitude
        distance = (lat_diff**2 + lng_diff**2) ** 0.5

        prop['distance'] = round(distance, 2)
        all_comps.append(prop)

    # Sort by distance from property
    all_comps.sort(key=lambda x: x.get('distance', 999))

    # Filter by radius
    comps_in_radius = [c for c in all_comps if c['distance'] <= radius]

    # Count how many more are in the next mile
    next_mile_count = len([c for c in all_comps if c['distance'] <= radius + 1]) - len(comps_in_radius)

    return jsonify({
        'success': True,
        'results': comps_in_radius,
        'radius': radius,
        'total_in_city': len(all_comps),
        'more_in_next_mile': next_mile_count
    })


@app.route('/api/selected', methods=['GET', 'POST', 'DELETE'])
def manage_selected():
    """Manage selected properties in session"""
    if 'selected' not in session:
        session['selected'] = []

    if request.method == 'GET':
        return jsonify(session['selected'])

    elif request.method == 'POST':
        property_data = request.json
        # Avoid duplicates
        existing_ids = [p['id'] for p in session['selected']]
        if property_data['id'] not in existing_ids:
            session['selected'].append(property_data)
            session.modified = True
        return jsonify(session['selected'])

    elif request.method == 'DELETE':
        property_id = request.json.get('id')
        session['selected'] = [p for p in session['selected'] if p['id'] != property_id]
        session.modified = True
        return jsonify(session['selected'])


@app.route('/analyze')
def analyze_page():
    """Analysis page for selected properties"""
    return render_template('analyze.html')


@app.route('/comps')
def comps_page():
    """New construction comps page"""
    return render_template('comps.html')


if __name__ == '__main__':
    app.run(debug=True, port=5050)
