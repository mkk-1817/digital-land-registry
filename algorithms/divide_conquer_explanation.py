# Divide and Conquer for Property Searching
def explain_divide_and_conquer():
    print("Divide and Conquer for Property Searching")
    print("----------------------------------------")
    print("1. We start with a large dataset of properties")
    print("2. If the result set is too large (e.g., > 1000 properties):")
    print("   a. Divide: Split the dataset into two halves")
    print("   b. Conquer: Recursively process each half")
    print("   c. Combine: Merge the results")
    print("3. This approach is more efficient for large datasets")
    
    # Example
    print("\nExample:")
    properties = [f"Property {i}" for i in range(1, 17)]
    print(f"Initial properties: {properties}")
    
    def divide_and_process(props):
        print(f"Processing: {props}")
        
        if len(props) <= 2:
            print(f"Base case reached for: {props}")
            return props
        
        # Divide
        mid = len(props) // 2
        left = props[:mid]
        right = props[mid:]
        
        print(f"Dividing into: {left} and {right}")
        
        # Conquer (recursively process each half)
        left_processed = divide_and_process(left)
        right_processed = divide_and_process(right)
        
        # Combine
        result = left_processed + right_processed
        print(f"Merging: {left_processed} and {right_processed} -> {result}")
        return result
    
    result = divide_and_process(properties[:8])  # Using a smaller subset for clarity
    print(f"\nFinal result: {result}")

explain_divide_and_conquer()
