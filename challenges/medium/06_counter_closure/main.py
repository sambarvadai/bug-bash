from counter import make_counter


def run_operations(operations, start=0):
    """
    operations: list of [op_name, amount]
        op_name is a key in the dict returned by make_counter.
        amount   is the numeric argument passed to that operation.

    start: initial counter value (default 0)

    Returns a list of counter values, one per operation, in order.

    Example:
        run_operations([["inc", 1], ["inc", 2], ["dec", 1]], 0)
        → [1, 3, 2]
    """
    ops = make_counter(start)
    results = []
    for op, amount in operations:
        results.append(ops[op](amount))
    return results
