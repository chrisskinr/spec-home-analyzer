# Spec Home Analyzer - Project Brief

## Purpose
Help Ethos identify and analyze spec home opportunities in Oak Brook by:
1. Finding teardown candidates (older homes on valuable lots)
2. Calculating fair land value using comparable sales
3. Determining realistic new build size and price using recent new construction comps

## Users
- Chris Skinner
- Ethos Founder 1
- Ethos Founder 2

Desktop-only, analysis session tool. No mobile needed.

---

## Application Flow

### Screen 1: Property Search
**Input:** Oak Brook MLS listings
**Display:**
- Visual list/grid of properties for sale
- For each: Address, Price, Lot Size, Year Built, Photo
- Filter: Max price (default $1M)
- Sort: By price, lot size, age

**User Action:** Select properties to analyze → adds to sidebar

**Sidebar:** Shows selected properties, persists across screens

### Screen 2: Land Value Analysis
**For each selected property:**
- Pull comparable SALES (not listings) from last 2 years
- Same subdivision OR same school district within radius
- Calculate fair market land value

**Display:**
- Selected property details
- Comparable sales table
- Estimated land value (our calculation)

### Screen 3: New Construction Comps
**For each selected property:**
- Pull SOLD new construction (year built last 10 years)
- Same subdivision OR same school district within radius
- Calculate "middle of distribution" for:
  - House size (sq ft)
  - Sale price
  - Price per sq ft

**Display:**
- New construction comp table
- Target build size range
- Target sale price range
- Target $/sq ft range

### Screen 4: (Future) Deal Calculator
- Variable sliders for construction costs
- Profit/margin calculations
- Go/no-go decision support

---

## Data Source: MRED (Midwest Real Estate Data)

### Access Type
- [x] Have MLS login
- [ ] Confirmed API access level
- [ ] API credentials obtained

### MRED API Info
- **System:** connectMLS
- **API Standard:** RESO Web API (Gold Certified)
- **Auth:** OpenID Connect
- **Query:** OData protocol

### Key Fields Needed (RESO Standard)
| Field | Purpose |
|-------|---------|
| ListPrice | Current asking price |
| ClosePrice | Sold price (for comps) |
| OriginalListPrice | Original ask |
| LotSizeSquareFeet | Lot size |
| LivingArea | House sq ft |
| YearBuilt | Age of home |
| SubdivisionName | For comp matching |
| ElementarySchool / HighSchool | School district matching |
| City | Oak Brook filter |
| StandardStatus | Active, Closed, etc. |
| CloseDate | For filtering recent sales |
| Latitude / Longitude | Radius-based comp search |
| Media | Property photos |
| StreetNumber, StreetName, etc. | Address display |

### To Confirm with MLS Provider
1. Does our login include API access, or just web portal?
2. If API access: What are our credentials?
3. If no API: What does upgrade cost?
4. Alternative: Can we use a data aggregator (MLS Grid, etc.)?

### MRED Contact
- Help Desk: help.desk@mredllc.com
- Phone: 630-955-2755
- Portal: https://connectmls.mredllc.com/

---

## Tech Stack (Proposed)

### Option A: Python Desktop App
- **Framework:** PyQt or Tkinter for UI
- **Data:** Python requests + pandas for API/analysis
- **Pros:** Fast to build, good for data analysis
- **Cons:** Less polished UI

### Option B: Web App (Local)
- **Framework:** Flask/FastAPI backend + simple HTML/JS frontend
- **Data:** Python backend handles API + analysis
- **Pros:** Better UI flexibility, runs in browser
- **Cons:** Slightly more setup

### Option C: Electron App
- **Framework:** Electron (JavaScript)
- **Pros:** Native-feeling desktop app
- **Cons:** Heavier, JS ecosystem

**Recommendation:** Option B (local web app). Clean UI, easy to iterate, Python handles the data work well.

---

## Open Questions

1. **API Access:** What level of access does current MLS login provide?
2. **Radius:** What geographic radius for "adjacent" comps? 0.5 mile? 1 mile?
3. **School District:** Use elementary school or high school for matching?
4. **New Construction Definition:** Year built >= 2015? Or last 10 years rolling?
5. **Land Value Calculation:** Simple average of comps, or weighted by proximity/recency?
6. **Photos:** Do we need multiple photos or just one thumbnail?

---

## Next Steps

1. [ ] Confirm API access level with MLS provider
2. [ ] If API available: Get credentials, test basic query
3. [ ] If no API: Explore alternatives (MLS Grid, upgrade path)
4. [ ] Build basic prototype with mock data
5. [ ] Connect to real data once API confirmed

---

## Resources

- [MRED connectMLS Portal](https://connectmls.mredllc.com/)
- [MRED API Login](https://connectmls-api.mredllc.com/oid/login)
- [RESO Data Dictionary](https://www.reso.org/data-dictionary/)
- [SimplyRETS RESO Overview](https://simplyrets.com/blog/data-dictionary)
- [MLS Grid (Data Aggregator)](https://docs.mlsgrid.com/)

---

*Created: 2025-01-27*
*Status: Discovery*
