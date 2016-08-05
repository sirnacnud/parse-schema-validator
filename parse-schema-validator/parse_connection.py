import httplib


class ParseConnection:

    def __init__(self, host, port, app_id, master_key):
        self.host = host
        self.port = port
        self.app_id = app_id
        self.master_key = master_key
        self.connection = None

    def connect(self):
        if self.connection:
            self.connection.close()

        if self.port == 443:
            self.connection = httplib.HTTPSConnection(self.host, self.port)
        else:
            self.connection = httplib.HTTPConnection(self.host, self.port)

        self.connection.connect()

    def perform_request(self, method, path, body):
        response = None

        try:
            self.connection.request(method, path, body, {
                "X-Parse-Application-Id": self.app_id,
                "X-Parse-Master-Key": self.master_key,
                "Content-Type": "application/json"
            })
            response = self.connection.getresponse()
        except httplib.BadStatusLine:
            # Try reconnecting if server closed connection
            self.connect()

            self.connection.request(method, path, body, {
                "X-Parse-Application-Id": self.app_id,
                "X-Parse-Master-Key": self.master_key,
                "Content-Type": "application/json"
            })
            response = self.connection.getresponse()

        return response
