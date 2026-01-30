"""
Zillow API wrapper for spec home analyzer
Uses RapidAPI Real Estate 101 scraper
"""

import requests
import urllib.parse
import json

class ZillowAPI:
    def __init__(self):
        self.base_url = "https://real-estate101.p.rapidapi.com"
        self.headers = {
            "x-rapidapi-host": "real-estate101.p.rapidapi.com",
            "x-rapidapi-key": "299527d0efmsh972ff518e6e32e7p175d57jsn776e63c20830"
        }

        # Western suburbs bounds (expanded to include more cities)
        self.oak_brook_bounds = {
            "north": 41.92,
            "south": 41.72,
            "east": -87.80,
            "west": -88.15
        }

    def _build_search_url(self, location="Oak Brook, IL", bounds=None,
                          max_price=None, min_year_built=None,
                          sold_only=False, for_sale_only=True, sold_in_last=None,
                          city=None):
        """Build a Zillow search URL with filters"""

        if bounds is None:
            bounds = self.oak_brook_bounds

        filter_state = {
            "sort": {"value": "days"}
        }

        # For sale vs sold
        if sold_only:
            filter_state["rs"] = {"value": True}  # Recently sold
            filter_state["fsba"] = {"value": False}
            filter_state["fsbo"] = {"value": False}
            filter_state["nc"] = {"value": False}
            filter_state["cmsn"] = {"value": False}
            filter_state["auc"] = {"value": False}
            filter_state["fore"] = {"value": False}
            # Extend sold lookback period (36m = 3 years)
            if sold_in_last:
                filter_state["doz"] = {"value": sold_in_last}

        # Price filter
        if max_price:
            filter_state["price"] = {"max": max_price}

        # Year built filter (for new construction)
        if min_year_built:
            filter_state["built"] = {"min": min_year_built}

        # Use city-specific search if provided
        if city:
            city_slug = city.lower().replace(' ', '-')
            location = f"{city}, IL"
            base = f"https://www.zillow.com/{city_slug}-il/"
            # Use tighter bounds centered on the specific city
            city_bounds = {
                "downers grove": {"north": 41.83, "south": 41.74, "east": -87.94, "west": -88.09},
                "oak brook": {"north": 41.87, "south": 41.81, "east": -87.90, "west": -87.98},
                "hinsdale": {"north": 41.82, "south": 41.78, "east": -87.90, "west": -87.96},
                "westmont": {"north": 41.81, "south": 41.77, "east": -87.94, "west": -88.00},
                "clarendon hills": {"north": 41.81, "south": 41.78, "east": -87.93, "west": -87.97},
            }
            bounds = city_bounds.get(city.lower(), bounds)
        else:
            base = "https://www.zillow.com/oak-brook-il/"

        search_state = {
            "isMapVisible": True,
            "mapBounds": bounds,
            "filterState": filter_state,
            "isListVisible": True,
            "usersSearchTerm": location
        }

        # Build URL
        if sold_only:
            base += "sold/"

        url = f"{base}?searchQueryState={json.dumps(search_state)}"
        return url

    def search(self, max_price=None, min_year_built=None,
               sold_only=False, page=1, sold_in_last=None, city=None):
        """
        Search for properties

        Args:
            max_price: Maximum price filter (e.g., 1000000)
            min_year_built: Minimum year built (e.g., 2015 for new construction)
            sold_only: If True, only return sold properties
            page: Page number for pagination
            sold_in_last: Time period for sold (e.g., "36m" for 3 years)
            city: Specific city to search (e.g., "Downers Grove")

        Returns:
            dict with results
        """

        search_url = self._build_search_url(
            max_price=max_price,
            min_year_built=min_year_built,
            sold_only=sold_only,
            sold_in_last=sold_in_last,
            city=city
        )

        encoded_url = urllib.parse.quote(search_url, safe='')
        api_url = f"{self.base_url}/api/search/byurl?url={encoded_url}&page={page}"

        response = requests.get(api_url, headers=self.headers)
        return response.json()

    def get_teardown_candidates(self, max_price=1000000, page=1, city=None):
        """Get properties for sale under max_price (potential teardowns)"""
        return self.search(max_price=max_price, sold_only=False, page=page, city=city)

    def get_sold_comps(self, page=1, city=None):
        """Get sold properties (last 5 years) for comps"""
        return self.search(sold_only=True, page=page, sold_in_last="60m", city=city)

    def get_new_construction_comps(self, min_year=2015, page=1):
        """Get sold new construction for target build analysis"""
        return self.search(sold_only=True, min_year_built=min_year, page=page)

    def get_property_details(self, zpid):
        """Get detailed property info including schools"""
        api_url = f"{self.base_url}/api/property?zpid={zpid}"
        try:
            response = requests.get(api_url, headers=self.headers)
            return response.json()
        except Exception as e:
            return {'error': str(e)}

    def extract_school_district(self, property_details):
        """Extract school district from property details"""
        schools = property_details.get('schools', [])

        # Look for elementary school district (most specific)
        for school in schools:
            if school.get('level') == 'Elementary':
                # District name is often in the school name or separate field
                district = school.get('district') or school.get('name', '')
                return {
                    'district_name': district,
                    'elementary': school.get('name'),
                    'rating': school.get('rating')
                }

        # Fallback to any school's district
        if schools:
            first_school = schools[0]
            return {
                'district_name': first_school.get('district') or first_school.get('name', ''),
                'elementary': None,
                'rating': first_school.get('rating')
            }

        return {'district_name': 'Unknown', 'elementary': None, 'rating': None}

    def analyze_property(self, property_data, sold_comps, new_construction_comps):
        """
        Analyze a property for spec home potential

        Returns analysis with:
        - Estimated land value
        - Target build size
        - Target sale price
        - Estimated profit potential
        """

        # Get lot size in sqft
        lot_size = property_data.get('lotAreaValue', 0)
        lot_unit = property_data.get('lotAreaUnit', 'sqft')
        if lot_unit == 'acres':
            lot_size_sqft = lot_size * 43560
        else:
            lot_size_sqft = lot_size

        # Calculate average $/sqft for new construction
        nc_prices_per_sqft = []
        for nc in new_construction_comps:
            if nc.get('livingArea', 0) > 0 and nc.get('unformattedPrice', 0) > 0:
                price_per_sqft = nc['unformattedPrice'] / nc['livingArea']
                nc_prices_per_sqft.append(price_per_sqft)

        avg_price_per_sqft = sum(nc_prices_per_sqft) / len(nc_prices_per_sqft) if nc_prices_per_sqft else 0

        # Calculate average new construction size
        nc_sizes = [nc.get('livingArea', 0) for nc in new_construction_comps if nc.get('livingArea', 0) > 0]
        avg_nc_size = sum(nc_sizes) / len(nc_sizes) if nc_sizes else 0

        # Estimate land value (property price - no structure value for teardown)
        asking_price = property_data.get('unformattedPrice', 0)

        # Target build price
        target_build_size = avg_nc_size
        target_sale_price = target_build_size * avg_price_per_sqft

        return {
            'property': property_data,
            'lot_size_sqft': lot_size_sqft,
            'asking_price': asking_price,
            'avg_nc_price_per_sqft': round(avg_price_per_sqft, 2),
            'avg_nc_size': round(avg_nc_size, 0),
            'target_build_size': round(target_build_size, 0),
            'target_sale_price': round(target_sale_price, 0),
            'estimated_land_cost': asking_price,
            'gross_profit_potential': round(target_sale_price - asking_price, 0)
        }


# Quick test
if __name__ == "__main__":
    api = ZillowAPI()

    print("Testing teardown candidates...")
    results = api.get_teardown_candidates(max_price=800000, page=1)
    print(f"Found {results.get('totalCount', 0)} properties")

    if results.get('results'):
        print(f"\nFirst property: {results['results'][0].get('address', {})}")
