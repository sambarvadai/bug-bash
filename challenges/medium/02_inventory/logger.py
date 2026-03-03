class RequestLog:
    log = []  # store request IDs for this service

    def __init__(self, service_name):
        self.service_name = service_name

    def record(self, request_id):
        self.log.append(request_id)

    def get_log(self):
        return list(self.log)
