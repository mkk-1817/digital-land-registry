def find_optimal_properties(properties, preferences):
    """
    Uses a greedy algorithm to find optimal properties based on user preferences.
    
    Args:
        properties: List of available properties
        preferences: Dictionary containing user preferences with weights
        
    Returns:
        List of properties sorted by their match score
    """
    # Extract preference weights
    location_weight = preferences.get('locationWeight', 1)
    price_weight = preferences.get('priceWeight', 1)
    area_weight = preferences.get('areaWeight', 1)
    
    # Preferred values
    preferred_location = preferences.get('location', '').lower()
    preferred_price = preferences.get('price', 0)
    preferred_area = preferences.get('area', 0)
    
    # Calculate score for each property
    scored_properties = []
    for prop in properties:
        # Skip properties with missing data
        if not prop.get('location') or not prop.get('area'):
            continue
            
        # Location score (exact match or partial match)
        location = prop['location'].lower()
        if preferred_location:
            if preferred_location == location:
                location_score = 1.0  # Exact match
            elif preferred_location in location:
                location_score = 0.7  # Partial match
            else:
                location_score = 0.0  # No match
        else:
            location_score = 0.5  # No preference specified
        
        # Price score (closer to preferred price is better)
        property_price = prop.get('askingPrice', prop.get('value', 0))
        if preferred_price > 0:
            # Calculate price difference as a percentage
            price_diff = abs(property_price - preferred_price) / max(preferred_price, 1)
            price_score = max(0, 1 - min(price_diff, 1))  # Cap at 0-1 range
        else:
            price_score = 0.5  # No preference specified
        
        # Area score (closer to preferred area is better)
        if preferred_area > 0:
            # Calculate area difference as a percentage
            area_diff = abs(prop['area'] - preferred_area) / max(preferred_area, 1)
            area_score = max(0, 1 - min(area_diff, 1))  # Cap at 0-1 range
        else:
            area_score = 0.5  # No preference specified
        
        # Calculate weighted score
        total_weight = location_weight + price_weight + area_weight
        if total_weight > 0:
            total_score = (
                location_weight * location_score +
                price_weight * price_score +
                area_weight * area_score
            ) / total_weight
        else:
            total_score = (location_score + price_score + area_score) / 3
        
        # Add debugging information
        prop_with_score = prop.copy()
        prop_with_score['score'] = total_score
        prop_with_score['_debug'] = {
            'location_score': location_score,
            'price_score': price_score,
            'area_score': area_score
        }
        
        scored_properties.append(prop_with_score)
    
    # Sort properties by score in descending order (greedy approach)
    return sorted(scored_properties, key=lambda x: x['score'], reverse=True)
