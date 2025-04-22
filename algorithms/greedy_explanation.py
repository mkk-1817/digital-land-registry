# Greedy Algorithm for Property Recommendation
def explain_greedy_algorithm():
    print("Greedy Algorithm for Property Recommendation")
    print("-------------------------------------------")
    print("1. Each property is assigned a score based on how well it matches user preferences")
    print("2. Preferences include location, price, and area with different weights")
    print("3. For each property, we calculate individual scores:")
    print("   - Location score: 1.0 if location matches, 0.0 otherwise")
    print("   - Price score: Higher when closer to preferred price")
    print("   - Area score: Higher when closer to preferred area")
    print("4. We calculate a weighted total score for each property")
    print("5. Properties are sorted by score in descending order")
    print("6. The top N properties are recommended to the user")
    
    # Example
    print("\nExample:")
    properties = [
        {"location": "Mumbai", "askingPrice": 5000000, "area": 1200},
        {"location": "Delhi", "askingPrice": 4500000, "area": 1000},
        {"location": "Mumbai", "askingPrice": 6000000, "area": 1500}
    ]
    
    preferences = {
        "location": "Mumbai",
        "price": 5500000,
        "area": 1300,
        "locationWeight": 2,
        "priceWeight": 1,
        "areaWeight": 1
    }
    
    print(f"\nProperties: {properties}")
    print(f"Preferences: {preferences}")
    
    # Calculate scores
    scored_properties = []
    for i, prop in enumerate(properties):
        location_score = 1.0 if preferences["location"].lower() in prop["location"].lower() else 0.0
        
        price_diff = abs(prop["askingPrice"] - preferences["price"]) / preferences["price"]
        price_score = max(0, 1 - price_diff)
        
        area_diff = abs(prop["area"] - preferences["area"]) / preferences["area"]
        area_score = max(0, 1 - area_diff)
        
        total_score = (
            preferences["locationWeight"] * location_score +
            preferences["priceWeight"] * price_score +
            preferences["areaWeight"] * area_score
        ) / (preferences["locationWeight"] + preferences["priceWeight"] + preferences["areaWeight"])
        
        scored_properties.append({
            **prop,
            "score": total_score
        })
        
        print(f"\nProperty {i+1}:")
        print(f"  Location score: {location_score:.2f}")
        print(f"  Price score: {price_score:.2f}")
        print(f"  Area score: {area_score:.2f}")
        print(f"  Total score: {total_score:.2f}")
    
    # Sort by score
    sorted_properties = sorted(scored_properties, key=lambda x: x["score"], reverse=True)
    print("\nSorted properties by score:")
    for i, prop in enumerate(sorted_properties):
        print(f"{i+1}. {prop['location']} - Score: {prop['score']:.2f}")

explain_greedy_algorithm()
