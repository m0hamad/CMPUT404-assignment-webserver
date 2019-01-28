import os # For dealing with root ./www and /deep directories
import socketserver
from pathlib import Path

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved


# https://docs.python.org/3/library/socketserver.html
class MyWebServer(socketserver.BaseRequestHandler):

    def find_content_in_directory(self, content):

        path_ = os.path.abspath(os.getcwd() + "/www" + content)

        return path_

    #As per assignment requirements, only text/html and text/css are supported
    def get_mime_type(self, content):

        #https://www.tutorialspoint.com/python/string_endswith.htm
        if content.endswith(".css"):

            return "Content-Type: text/css\r\n"
        
        elif content.endswith(".html"):
            
            return "Content-Type: text/html\r\n"   
        else:
            return "Content-Type: text/html\r\n"
    
    # Response body resembles request body that server gets from the client.
    def respond_200(self, in_directory_content, content, data):

        new_content = open(in_directory_content).read()
        status_code = "HTTP/1.1 200 OK\r\n"
        mime_type = self.get_mime_type(content)
        connection = data[-1] + "\r\n\r\n"
        
        self.request.send((status_code + mime_type + connection + new_content).encode("utf-8"))

    def respond_301(self):
        status_code = "HTTP/1.1 301 Moved Permanently\r\n"
        content_type = "Content-Type: text/html\r\n"
        connection = "Connection: close \r\n\r\n"
        content = ("<html>\n<body> Error 301. Content Moved Permanently. </body>\n</html>")

        self.request.send((status_code + content_type + connection + content).encode("utf-8"))

    def respond_404(self, content):

        status_code = "HTTP/1.1 404 Not Found\r\n"
        connection = "Connection: close\r\n\r\n"
        content = ("<html>\n<body>Error 404. Sorry, content not found. </body>\n</html>")

        self.request.send((status_code + connection + content).encode("utf-8"))

    def respond_405(self, content, data):
        
        status_code = "HTTP/1.1 405 Method Not Allowed\r\n"
        connection = data[-1] + "\r\n\r\n"
        content = ("<html>\n<body> Error 405. The requested content does not support http method 'GET'. </body>\n</html>")

        self.request.send((status_code + connection + content).encode("utf-8"))
    
    def handle(self):

        # https://stackoverflow.com/questions/606191/convert-bytes-to-a-string
        # split using \r\n to get appropriate headers
        self.data = self.request.recv(1024).strip().decode("utf-8").split("\r\n")
        print ("Got a request of: %s\n" % self.data)

        # Get resource type
        first_header = self.data[0].split(" ")
        status_code = first_header[0]
        content = first_header[1]

        in_directory_content = self.find_content_in_directory(content)

        if content.endswith("/"):
            in_directory_content += "/index.html"

        try:
            if status_code != "GET":
                self.respond_405(content, self.data)

            if Path(in_directory_content).exists() and "www" in in_directory_content:

                if Path(in_directory_content).is_file():
                    self.respond_200(in_directory_content, content, self.data)
                    
                else:
                    self.respond_301()

            else:
                self.respond_404(content)
        
        except:
            self.respond_404(content)

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    print("Starting server...")
    server.serve_forever()