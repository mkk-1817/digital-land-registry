def predict_optimal_bid(auction, property_obj, user_bid_history):
    """
    Uses dynamic programming to predict the optimal bid amount for an auction.
    
    Args:
        auction: Current auction data
        property_obj: Property being auctioned
        user_bid_history: User's bidding history
        
    Returns:
        Optimal bid amount
    """
    current_highest_bid = auction['currentHighestBid']
    property_value = property_obj['value']
    
    # Extract bidding patterns from history
    bid_ratios = []  # Ratio of bid to property value
    for history_item in user_bid_history:
        for bid in history_item.get('bids', []):
            # Find the property value
            prop_id = history_item.get('propertyId')
            if prop_id:
                prop = property_obj  # This would be a DB lookup in a real implementation
                if prop:
                    bid_ratios.append(bid['amount'] / prop['value'])
    
    # If no history, use default strategy
    if not bid_ratios:
        # Default strategy: bid 5% above current highest bid, but not more than property value
        return min(current_highest_bid * 1.05, property_value)
    
    # Calculate average bid ratio from history
    avg_bid_ratio = sum(bid_ratios) / len(bid_ratios)
    
    # Dynamic programming approach to find optimal bid
    # We'll use a table to store the expected value for different bid amounts
    
    # Define possible bid increments (e.g., 1%, 2%, 5%, 10% above current highest bid)
    increments = [1.01, 1.02, 1.05, 1.10]
    
    # Calculate possible bid amounts
    possible_bids = [min(current_highest_bid * inc, property_value) for inc in increments]
    
    # Add historical average bid
    historical_bid = property_value * avg_bid_ratio
    if historical_bid > current_highest_bid:
        possible_bids.append(historical_bid)
    
    # Calculate win probability and expected value for each bid
    max_expected_value = 0
    optimal_bid = current_highest_bid * 1.05  # Default
    
    for bid in possible_bids:
        # Simple win probability model: higher bid = higher probability
        win_prob = min(1.0, (bid - current_highest_bid) / (property_value * 0.1))
        
        # Expected value = win_prob * (property_value - bid)
        expected_value = win_prob * (property_value - bid)
        
        if expected_value > max_expected_value:
            max_expected_value = expected_value
            optimal_bid = bid
    
    return optimal_bid
