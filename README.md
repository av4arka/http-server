## Purpose:
The console HTTP-server receives a request from the client and gives it an HTTP response. Only responds to GET- requests. With each request, in the console displays a numeric response code and URL, works on the client-server principle

## Get started:
- Download the .zip file or clone the repository.
- Open your console and go to the folder with the source code of the program
- Run file http_server.py:

      $ python3.6 http_server.py
- Use the server by entering a request and receiving a response.
## Usage example:
- Open new console and use telnet:

      $ telnet localhost 8081
### Request:
The query string looks like this:

    GET / HTTP/1.0
That is:

    Method URI HTTP/version 
### Response:
The response consists of the headers and body of the message(in HTTP / 0.9, only the message body is displayed).

    Host: localhost
    HTTP/1.0 200 OK
    Connection: close
    Content-Length: 119
    Content-Type: text/html
    Date: Wed, 06 Mar 2019 16:21:17 GMT

    <html>
    <head>
      <title>Home page of the site</title>
    </head>

    <body>

    Home page of the site

    </body>
    </html>
### Sample console output:
    200 /index.html
## Requirements:
- python3.6
- install module magic(using pip)
