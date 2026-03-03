def make_counter(start=0):
    """
    Returns a dict of counter operations sharing the same internal state.

    Supported ops (to be extended):
      "inc": increment count by N, return new count
      "dec": decrement count by N, return new count  ← TODO: implement
    """
    count = start

    def increment(by=1):
        count += by  # something is off here
        return count

    def decrement(by=1):
        pass  # TODO: subtract by from count and return count

    return {"inc": increment, "dec": decrement}
