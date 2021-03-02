from http.server import BaseHTTPRequestHandler, HTTPServer

from threading import Thread
import os, traceback


class Server:
    rootDirectory = os.path.dirname(os.path.realpath(__file__)).replace(__file__, "")
    templatesDirectory = os.path.join(rootDirectory, "Templates")

    docTypeLocations = {
        ".html":"Templates",
        ".css":"CSS",
        ".js":"JS",
        ".jpg":"Images",
        ".png":"Images",
    }

    _routers = {}

    landingPage = ""

    def addRouter(route, router):
        Server._routers[route] = router

    class Server(BaseHTTPRequestHandler):
        def do_HEAD(self):
            return

        def do_POST(self):
            return

        def do_GET(self):
            self.respond()

        def handle_http(self, status, contentType):
            self.send_response(status)
            self.send_header('Content-type', contentType)
            self.end_headers()

            path = self.path.strip("/").strip("\\")
            if len(path) == 0: path = Server.landingPage
            if len(path) == 0: return bytes("Invalid path", "UTF-8")

            fileType = path[path.rfind("."):]
            docTypeLocation = os.path.join(Server.rootDirectory, Server.docTypeLocations.get(fileType, "Misc"))
            requestedDirectory = os.path.realpath(os.path.join(docTypeLocation, path))

            if docTypeLocation not in requestedDirectory: return bytes("Bad location", "UTF-8")

            try:
                with open(requestedDirectory, "r") as f:
                    fileContent = f.read()

            except FileNotFoundError:
                return bytes("404", "UTF-8")

            except UnicodeDecodeError:
                with open(requestedDirectory, "rb") as f:
                    return f.read()

            return bytes(Server._routers.get(path, lambda route, content: content)(path, fileContent), "UTF-8")
            
        def respond(self):
            content = self.handle_http(200, 'text/html')
            self.wfile.write(content)

    def __init__(self, port, host="localhost"):
        self._port = port
        self._host = host

        self._server = HTTPServer((self._host, self._port), self.Server)
        self._serverThread = None

    def start(self):
        self._serverThread = Thread(target=self._server.serve_forever)
        self._serverThread.start()

    def stop(self):
        self._server.shutdown()
        self._server.server_close()
        self._serverThread.join()

