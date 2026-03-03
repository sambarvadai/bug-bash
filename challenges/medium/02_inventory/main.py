from logger import RequestLog


def collect_logs(service_requests):
    """
    service_requests: list of {"service": str, "ids": [str, ...]}

    Creates a fresh RequestLog for each service, records its request IDs,
    and returns a dict of {service_name: [request_ids]}.

    Each service's log must contain only its own request IDs.
    """
    results = {}
    for entry in service_requests:
        logger = RequestLog(entry["service"])
        for req_id in entry["ids"]:
            logger.record(req_id)
        results[entry["service"]] = logger.get_log()
    return results
