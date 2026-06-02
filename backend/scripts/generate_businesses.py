"""
Generates 500 realistic local_businesses seed entries per venue city.
Run once: python scripts/generate_businesses.py
Output: backend/data/seed/businesses.json
"""
import json
import random
import math
from pathlib import Path

random.seed(42)

SEED_DIR = Path(__file__).resolve().parent.parent / "data" / "seed"

VENUES = [
    {
        "venue_id": "metlife_stadium",
        "city": "East Rutherford",
        "state": "NJ",
        "lat": 40.8135,
        "lng": -74.0745,
        "neighborhood": "Meadowlands",
    },
    {
        "venue_id": "att_stadium",
        "city": "Arlington",
        "state": "TX",
        "lat": 32.7480,
        "lng": -97.0929,
        "neighborhood": "Arlington Entertainment District",
    },
    {
        "venue_id": "sofi_stadium",
        "city": "Inglewood",
        "state": "CA",
        "lat": 33.9535,
        "lng": -118.3392,
        "neighborhood": "Hollywood Park",
    },
    {
        "venue_id": "mercedes_benz_stadium",
        "city": "Atlanta",
        "state": "GA",
        "lat": 33.7554,
        "lng": -84.4003,
        "neighborhood": "Downtown Atlanta",
    },
    {
        "venue_id": "hard_rock_stadium",
        "city": "Miami Gardens",
        "state": "FL",
        "lat": 25.9579,
        "lng": -80.2388,
        "neighborhood": "Miami Gardens",
    },
]

CUISINES = [
    "American", "Mexican", "Italian", "Japanese", "Chinese", "Indian",
    "Mediterranean", "Thai", "Korean", "Caribbean", "Brazilian", "Ethiopian",
    "Vietnamese", "Greek", "Spanish", "Peruvian", "Lebanese", "Turkish",
    "French", "Argentinian", "Moroccan", "Nigerian", "Jamaican",
]

HALAL_CUISINES = {"Indian", "Lebanese", "Turkish", "Moroccan", "Nigerian", "Ethiopian", "Mediterranean"}
VEGAN_FRIENDLY = {"Ethiopian", "Indian", "Mediterranean", "Thai", "Vietnamese", "Lebanese"}

CATEGORIES = ["restaurant", "bar", "sports_bar", "hotel", "cafe", "fast_food", "attraction"]

PRICE_RANGES = ["$", "$$", "$$$", "$$$$"]
PRICE_WEIGHTS = [0.2, 0.45, 0.25, 0.1]

RESTAURANT_TEMPLATES = [
    "{cuisine} Kitchen", "{cuisine} Grill", "The {cuisine} House", "{cuisine} Corner",
    "{city} {cuisine} Restaurant", "{cuisine} Street Food", "Casa {cuisine}",
    "{cuisine} Fusion", "The {cuisine} Table", "{cuisine} Bites",
    "Little {cuisine}", "Old Town {cuisine}", "{cuisine} Garden",
    "{cuisine} Spot", "{cuisine} Lounge", "The {city} Grill",
    "{cuisine} Palace", "Downtown {cuisine}", "{cuisine} & Co",
    "{city} Eats", "Stadium {cuisine}", "{cuisine} Hub",
]

BAR_NAMES = [
    "The Kick Off Bar", "Stadium Bar & Grill", "Fan Zone Pub",
    "The Touchline", "Corner Flag Sports Bar", "The Penalty Spot",
    "Half Time Bar", "The Goal Post", "Extra Time Sports Bar",
    "The Offside Trap", "Red Card Bar", "The Yellow Card",
    "Pitch Side Tavern", "The Box Seats", "Champions Sports Bar",
    "The Final Whistle", "Golden Boot Bar", "The Crossbar",
    "Draft House", "The Field Goal", "Sports Republic",
    "The Winning Goal", "Overtime Bar", "The Home End",
]

HOTEL_NAMES = [
    "Marriott {city}", "Hilton {city}", "Holiday Inn Express {city}",
    "Hampton Inn {city}", "Courtyard {city}", "Hyatt Place {city}",
    "Sheraton {city}", "Westin {city}", "Embassy Suites {city}",
    "Best Western {city}", "Comfort Inn {city}", "Residence Inn {city}",
    "Aloft {city}", "AC Hotel {city}", "Moxy {city}",
    "The {city} Grand", "Stadium Hotel {city}", "{city} Suites",
]

CAFE_NAMES = [
    "Morning Kick Off Cafe", "The Coffee Corner", "Stadium Brew",
    "Half Time Coffee", "Espresso Run", "The Daily Grind",
    "Kickoff Cafe", "Grounds Coffee Co", "The Match Day Roast",
    "Pitch Black Coffee", "Fan Fuel Cafe", "Pre-Match Coffee",
    "Corner Kick Cafe", "The Press Box Coffee", "Rooftop Roasters",
]

FAST_FOOD_NAMES = [
    "Burger Blitz", "Taco Sprint", "Pizza Rush", "The Quick Bite",
    "Speed Slice Pizza", "Fast Kick Burgers", "Goal Line Grill",
    "Match Day Wraps", "Rapid Noodles", "Quick Score Subs",
    "Stadium Smash Burgers", "Halftime Hotdogs", "Power Play Pizza",
]

ATTRACTION_NAMES = [
    "{city} Sports Museum", "World Cup Fan Zone", "Stadium Tour Experience",
    "The {city} Arcade", "VR Sports Arena", "Team Store & Merchandise",
    "Photo Wall — World Cup 2026", "Fan Experience Zone", "Interactive Soccer Exhibit",
    "The {city} Escape Room", "Mini Soccer Park", "World Cup Trophy Display",
    "Soccer Skills Challenge Zone", "Retro Football Gallery", "Live Music Fan Stage",
]

DESC_TEMPLATES = {
    "restaurant": [
        "Popular {cuisine} restaurant just {dist}m from {stadium}. Known for its {quality} food and lively atmosphere on match days. Great spot for pre- or post-game meals.",
        "Authentic {cuisine} dining {dist}m from the stadium. The menu features traditional dishes alongside local favourites. Busy on match days — book ahead.",
        "Casual {cuisine} eatery {dist}m from {stadium}. Quick service and generous portions make it a favourite with fans heading to and from games.",
        "Family-run {cuisine} restaurant serving hearty portions {dist}m from the stadium. One of the best-rated spots in the area for match day dining.",
        "Upscale {cuisine} restaurant {dist}m from {stadium}. Elevated dishes and a well-curated drinks list. Popular with groups celebrating after matches.",
    ],
    "bar": [
        "Lively sports bar {dist}m from {stadium} showing all World Cup matches on large screens. Craft beers on tap and a full food menu.",
        "Classic bar {dist}m from the stadium with a strong local following. Gets packed on match days. Good selection of beers and cocktails.",
        "Popular pre-match bar {dist}m from {stadium}. Multiple screens, happy hour deals from 4pm, and a buzzing atmosphere on game days.",
        "Neighbourhood bar {dist}m from the stadium. Known for its friendly staff, cold drinks, and big screens. Fills up fast on World Cup nights.",
    ],
    "sports_bar": [
        "Dedicated sports bar {dist}m from {stadium} with floor-to-ceiling screens. Serving American classics, cold beers, and watching parties for every World Cup match.",
        "The go-to sports bar for fans near {stadium}. {dist}m away, massive screen setups, full menu, and reserved seating for major matches.",
        "High-energy sports bar {dist}m from the stadium. Over 20 screens, craft beer selection, and a menu built for sports fans on game days.",
    ],
    "hotel": [
        "Well-located hotel {dist}m from {stadium}. Comfortable rooms, on-site restaurant, and shuttle service to the venue on match days.",
        "Modern hotel {dist}m from {stadium} offering World Cup packages including shuttle transfers and match day breakfast deals.",
        "Convenient hotel {dist}m from the stadium. Clean rooms, free WiFi, and easy access to public transport for match day travel.",
        "Popular hotel with fans {dist}m from {stadium}. Friendly staff, good amenities, and regular shuttle buses to the venue during the tournament.",
    ],
    "cafe": [
        "Cosy cafe {dist}m from {stadium}. Great coffee, pastries, and light meals. A calm spot to fuel up before the match-day crowds arrive.",
        "Specialty coffee shop {dist}m from the stadium. Excellent espresso and a selection of grab-and-go sandwiches for fans on the move.",
        "Busy cafe {dist}m from {stadium}. The flat whites are worth the queue. Popular breakfast destination for fans arriving early on match days.",
    ],
    "fast_food": [
        "Quick-service restaurant {dist}m from {stadium}. Fast, affordable meals that keep the queue moving on busy match days.",
        "Popular fast food spot {dist}m from the stadium. Good value and quick turnaround — perfect when you need to eat before kick-off.",
        "Reliable fast food option {dist}m from {stadium}. Extended hours on match days and a menu that covers most dietary needs.",
    ],
    "attraction": [
        "Fan-favourite attraction {dist}m from {stadium}. A great stop before or after the match — interactive exhibits and photo opportunities.",
        "Popular destination for visitors {dist}m from {stadium}. Especially busy during the World Cup with themed activities and events.",
        "Must-visit attraction {dist}m from the stadium. Memorable experience for football fans of all ages, open extended hours during the tournament.",
    ],
}

QUALITY_WORDS = ["excellent", "well-seasoned", "freshly prepared", "generous", "authentic", "crowd-pleasing"]


def rand_offset(max_m):
    """Return random lat/lng offset for a given max distance in metres."""
    angle = random.uniform(0, 2 * math.pi)
    dist_m = random.uniform(50, max_m)
    # 1 degree lat ≈ 111,000m; 1 degree lng ≈ 111,000m * cos(lat)
    dlat = (dist_m * math.cos(angle)) / 111000
    dlng = (dist_m * math.sin(angle)) / (111000 * math.cos(math.radians(40.0)))
    return dlat, dlng, int(dist_m)


def haversine(lat1, lng1, lat2, lng2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return int(R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))


def make_name(category, cuisine, city):
    if category == "restaurant":
        tpl = random.choice(RESTAURANT_TEMPLATES)
        return tpl.format(cuisine=cuisine, city=city)
    if category in ("bar", "sports_bar"):
        return random.choice(BAR_NAMES)
    if category == "hotel":
        return random.choice(HOTEL_NAMES).format(city=city)
    if category == "cafe":
        return random.choice(CAFE_NAMES)
    if category == "fast_food":
        return random.choice(FAST_FOOD_NAMES)
    if category == "attraction":
        return random.choice(ATTRACTION_NAMES).format(city=city)
    return f"{city} {category.title()}"


def make_description(category, cuisine, dist, stadium, city):
    tpls = DESC_TEMPLATES.get(category, DESC_TEMPLATES["restaurant"])
    tpl = random.choice(tpls)
    return tpl.format(
        cuisine=cuisine, dist=dist, stadium=stadium, city=city,
        quality=random.choice(QUALITY_WORDS)
    )


def make_address(city, state, i):
    streets = [
        "Main St", "Stadium Blvd", "Park Ave", "Oak St", "Cedar Rd",
        "Maple Dr", "Elm St", "Washington Ave", "Lincoln Blvd", "Victory Ln",
        "Sports Way", "Fan Plaza", "Match Day Dr", "Goal Line Rd", "Kick Off Ave",
    ]
    return f"{100 + i * 3} {random.choice(streets)}, {city}, {state}"


def generate_for_venue(venue, count=500):
    docs = []
    used_names = set()

    # Ensure category distribution
    cat_quotas = {
        "restaurant": 200,
        "bar": 60,
        "sports_bar": 40,
        "hotel": 50,
        "cafe": 60,
        "fast_food": 50,
        "attraction": 40,
    }
    category_pool = []
    for cat, n in cat_quotas.items():
        category_pool.extend([cat] * n)
    random.shuffle(category_pool)

    # Ensure halal/vegan distribution — at least 10% each
    halal_slots = set(random.sample(range(count), int(count * 0.12)))
    vegan_slots = set(random.sample(range(count), int(count * 0.12)))

    for i in range(count):
        category = category_pool[i % len(category_pool)]
        cuisine = random.choice(CUISINES)

        halal = (i in halal_slots) or (cuisine in HALAL_CUISINES and random.random() < 0.6)
        vegan = (i in vegan_slots) or (cuisine in VEGAN_FRIENDLY and random.random() < 0.4)

        dlat, dlng, dist_m = rand_offset(3000)
        lat = round(venue["lat"] + dlat, 6)
        lng = round(venue["lng"] + dlng, 6)
        actual_dist = haversine(venue["lat"], venue["lng"], lat, lng)
        actual_dist = max(50, min(actual_dist, 4999))

        name = make_name(category, cuisine, venue["city"])
        # deduplicate names
        base_name = name
        suffix = 1
        while name in used_names:
            name = f"{base_name} {suffix}"
            suffix += 1
        used_names.add(name)

        rating = round(random.uniform(3.0, 5.0), 1)
        price = random.choices(PRICE_RANGES, weights=PRICE_WEIGHTS)[0]
        desc = make_description(category, cuisine, actual_dist, venue["venue_id"].replace("_", " ").title(), venue["city"])

        docs.append({
            "name": name,
            "category": category,
            "cuisine": cuisine,
            "halal_flag": bool(halal),
            "vegan_flag": bool(vegan),
            "coords": {"lat": lat, "lng": lng},
            "distance_to_venue_m": actual_dist,
            "description": desc,
            "description_embedding": [],
            "address": make_address(venue["city"], venue["state"], i),
            "price_range": price,
            "rating": rating,
            "venue_id": venue["venue_id"],
            "city": venue["city"],
        })

    return docs


def main():
    all_businesses = []
    for venue in VENUES:
        print(f"generating 500 businesses for {venue['city']}...")
        docs = generate_for_venue(venue, 500)
        all_businesses.extend(docs)
        print(f"  done — {len(docs)} docs")

    out = SEED_DIR / "businesses.json"
    out.write_text(json.dumps(all_businesses, indent=2), encoding="utf-8")
    print(f"\nwrote {len(all_businesses)} businesses to {out}")


if __name__ == "__main__":
    main()
