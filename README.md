# Spec Home Analyzer

A tool to find teardown candidates and analyze spec home opportunities in the western Chicago suburbs.

## Features

- **Property Search**: Find properties for sale by city, filter by max price
- **Analysis**: View profit potential based on comparable new construction sales
- **Comps**: See recent sales in the same city to gauge market values

## Quick Start

1. Install Python 3.8+ if you don't have it
2. Install dependencies:
   ```
   pip install flask requests
   ```
3. Run the app:
   ```
   cd app
   python3 app.py
   ```
4. Open http://localhost:5050 in your browser

## How to Use

1. **Search tab**: Select a city (Oak Brook, Hinsdale, Downers Grove, etc.) and max price
2. Click **+ Select** on properties you want to analyze
3. Go to **Analyze tab** to see profit potential and comparable sales
4. Drag the divider to resize columns

## Cities Supported

Oak Brook, Hinsdale, Clarendon Hills, Downers Grove, Westmont, Western Springs, La Grange, Burr Ridge, Elmhurst, and more.

## Notes

- Data comes from Zillow via RapidAPI
- Analysis shows gross profit potential (before construction, closing, holding costs)
- Comparable sales are sorted by price to show market potential

---
Built for Ethos Operations
