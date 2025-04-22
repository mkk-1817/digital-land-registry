# Dynamic Programming for Optimal Bidding
def explain_dynamic_programming():
    print("Dynamic Programming for Optimal Bidding")
    print("--------------------------------------")
    print("1. We analyze the user's bidding history to find patterns")
    print("2. We calculate the average bid ratio (bid amount / property value)")
    print("3. We define possible bid increments above the current highest bid")
    print("4. For each possible bid amount, we calculate:")
    print("   - Win probability: Higher bid = higher probability")
    print("   - Expected value = win_probability * (property_value - bid)")
    print("5. We select the bid amount with the highest expected value")
    
    # Example
    print("\nExample:")
    current_highest_bid = 5000000
    property_value = 6000000
    
    # Historical bid ratios (bid amount / property value)
    bid_ratios = [0.85, 0.82, 0.88, 0.90]
    avg_bid_ratio = sum(bid_ratios) / len(bid_ratios)
    
    print(f"Current highest bid: ₹{current_highest_bid}")
    print(f"Property value: ₹{property_value}")
    print(f"Historical bid ratios: {bid_ratios}")
    print(f"Average bid ratio: {avg_bid_ratio:.2f}")
    
    # Define possible bid increments
    increments = [1.01, 1.02, 1.05, 1.10]
    possible_bids = [min(current_highest_bid * inc, property_value) for inc in increments]
    
    # Add historical average bid
    historical_bid = property_value * avg_bid_ratio
    if historical_bid > current_highest_bid:
        possible_bids.append(historical_bid)
    
    print(f"\nPossible bid amounts: {[f'₹{bid:.0f}' for bid in possible_bids]}")
    
    # Calculate expected value for each bid
    max_expected_value = 0
    optimal_bid = current_highest_bid * 1.05  # Default
    
    print("\nExpected value calculation:")
    for bid in possible_bids:
        # Simple win probability model
        win_prob = min(1.0, (bid - current_highest_bid) / (property_value * 0.1))
        expected_value = win_prob * (property_value - bid)
        
        print(f"Bid: ₹{bid:.0f}")
        print(f"  Win probability: {win_prob:.2f}")
        print(f"  Expected value: ₹{expected_value:.0f}")
        
        if expected_value > max_expected_value:
            max_expected_value = expected_value
            optimal_bid = bid
    
    print(f"\nOptimal bid: ₹{optimal_bid:.0f}")
    print(f"Expected value: ₹{max_expected_value:.0f}")

explain_dynamic_programming()
