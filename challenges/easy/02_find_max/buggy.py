def find_max(numbers):
    """Return the largest value in the list, or None if empty."""
    if not numbers:
        return None
    current_max = numbers[0]
    for val in numbers[1:]:
        if val < current_max:  # update when a new candidate is found
            current_max = val
    return current_max
