"""
Configuration constants and coordinate reference tables for Nassau Candy Distributor.
Derived directly from project specifications in UM.docx.
"""

FACTORY_COORDS = {
    "Lot's O' Nuts": (32.881893, -111.768036),       # Casa Grande, AZ
    "Wicked Choccy's": (32.076176, -81.088371),     # Savannah, GA
    "Sugar Shack": (48.119140, -96.181150),         # Thief River Falls, MN
    "Secret Factory": (41.446333, -90.565487),      # Rock Island / Moline, IL
    "The Other Factory": (35.117500, -89.971107),   # Memphis, TN
}

FACTORY_DETAILS = {
    "Lot's O' Nuts": {"city": "Casa Grande", "state": "Arizona", "region": "Pacific / West", "capacity_units_yr": 120000},
    "Wicked Choccy's": {"city": "Savannah", "state": "Georgia", "region": "Atlantic / Southeast", "capacity_units_yr": 150000},
    "Sugar Shack": {"city": "Thief River Falls", "state": "Minnesota", "region": "Interior / North", "capacity_units_yr": 90000},
    "Secret Factory": {"city": "Rock Island", "state": "Illinois", "region": "Interior / Midwest", "capacity_units_yr": 110000},
    "The Other Factory": {"city": "Memphis", "state": "Tennessee", "region": "Gulf / Mid-South", "capacity_units_yr": 100000},
}

PRODUCT_FACTORY = {
    "Wonka Bar - Nutty Crunch Surprise": "Lot's O' Nuts",
    "Wonka Bar - Fudge Mallows": "Lot's O' Nuts",
    "Wonka Bar -Scrumdiddlyumptious": "Lot's O' Nuts",
    "Wonka Bar - Milk Chocolate": "Wicked Choccy's",
    "Wonka Bar - Triple Dazzle Caramel": "Wicked Choccy's",
    "Laffy Taffy": "Sugar Shack",
    "SweeTARTS": "Sugar Shack",
    "Nerds": "Sugar Shack",
    "Fun Dip": "Sugar Shack",
    "Fizzy Lifting Drinks": "Sugar Shack",
    "Everlasting Gobstopper": "Secret Factory",
    "Hair Toffee": "The Other Factory",
    "Lickable Wallpaper": "Secret Factory",
    "Wonka Gum": "Secret Factory",
    "Kazookles": "The Other Factory",
}

PRODUCT_DIVISION = {
    "Wonka Bar - Nutty Crunch Surprise": "Chocolate",
    "Wonka Bar - Fudge Mallows": "Chocolate",
    "Wonka Bar -Scrumdiddlyumptious": "Chocolate",
    "Wonka Bar - Milk Chocolate": "Chocolate",
    "Wonka Bar - Triple Dazzle Caramel": "Chocolate",
    "Laffy Taffy": "Sugar",
    "SweeTARTS": "Sugar",
    "Nerds": "Sugar",
    "Fun Dip": "Sugar",
    "Fizzy Lifting Drinks": "Other",
    "Everlasting Gobstopper": "Sugar",
    "Hair Toffee": "Sugar",
    "Lickable Wallpaper": "Other",
    "Wonka Gum": "Other",
    "Kazookles": "Other",
}

REGION_COORDS = {
    "Atlantic": (38.8951, -77.0364),
    "Gulf": (29.9511, -90.0715),
    "Interior": (41.8781, -87.6298),
    "Pacific": (34.0522, -118.2437),
}

STATE_COORDS = {
    "Alabama": (32.806671, -86.791130),
    "Alaska": (61.370716, -152.404419),
    "Arizona": (33.729759, -111.431221),
    "Arkansas": (34.969704, -92.373123),
    "California": (36.116203, -119.681564),
    "Colorado": (39.059811, -105.311104),
    "Connecticut": (41.597782, -72.755371),
    "Delaware": (39.318523, -75.507141),
    "District of Columbia": (38.897438, -77.026817),
    "Florida": (27.766279, -81.686783),
    "Georgia": (33.040619, -83.643074),
    "Hawaii": (21.094318, -157.498337),
    "Idaho": (44.240459, -114.478828),
    "Illinois": (40.349457, -88.986137),
    "Indiana": (39.849426, -86.258278),
    "Iowa": (42.011539, -93.210526),
    "Kansas": (38.526600, -96.726486),
    "Kentucky": (37.668140, -84.670067),
    "Louisiana": (31.169546, -91.867805),
    "Maine": (44.693947, -69.381927),
    "Maryland": (39.063946, -76.802101),
    "Massachusetts": (42.230171, -71.530106),
    "Michigan": (43.326618, -84.536095),
    "Minnesota": (45.694454, -93.900192),
    "Mississippi": (32.741646, -89.678696),
    "Missouri": (38.456085, -92.288368),
    "Montana": (46.921925, -110.454353),
    "Nebraska": (41.125370, -98.268082),
    "Nevada": (38.313515, -117.055374),
    "New Hampshire": (43.452492, -71.563896),
    "New Jersey": (40.298904, -74.521011),
    "New Mexico": (34.840515, -106.248482),
    "New York": (42.165726, -74.948051),
    "North Carolina": (35.630066, -79.806419),
    "North Dakota": (47.528912, -99.784012),
    "Ohio": (40.388783, -82.764915),
    "Oklahoma": (35.565342, -96.928917),
    "Oregon": (44.572021, -122.070938),
    "Pennsylvania": (40.590752, -77.209755),
    "Rhode Island": (41.680893, -71.511780),
    "South Carolina": (33.856892, -80.945007),
    "South Dakota": (44.299782, -99.438828),
    "Tennessee": (35.747845, -86.692345),
    "Texas": (31.054487, -97.563461),
    "Utah": (40.150032, -111.862434),
    "Vermont": (44.045876, -72.710686),
    "Virginia": (37.769337, -78.169968),
    "Washington": (47.400902, -121.490494),
    "West Virginia": (38.491226, -80.954453),
    "Wisconsin": (44.268543, -89.616508),
    "Wyoming": (42.755966, -107.302490),
    "Ontario": (51.253775, -85.323214),
    "Quebec": (52.939916, -73.549136),
    "British Columbia": (53.726668, -127.647621),
    "Alberta": (53.933271, -116.576504),
}

SHIP_MODE_MULTIPLIERS = {
    "Same Day": {"speed_factor": 0.40, "cost_multiplier": 2.20},
    "First Class": {"speed_factor": 0.70, "cost_multiplier": 1.60},
    "Second Class": {"speed_factor": 0.90, "cost_multiplier": 1.25},
    "Standard Class": {"speed_factor": 1.00, "cost_multiplier": 1.00},
}
