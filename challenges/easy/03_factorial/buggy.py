def factorial(n):
    """Return n! for any non-negative integer n."""
    if n == 0 or n == 1:
        return 1
    n * factorial(n - 1)  # recursive case
