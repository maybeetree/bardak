import re
import html
import shutil
from pathlib import Path
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

if Path('banner.html').exists():
    banner = Path('banner.html').read_bytes()
else:
    banner = Path('banner.sample.html').read_bytes()
html_page = Path('page.html').read_bytes()
html_page_full = html_page.replace(b'__BANNER__', banner)
html_thing = Path('thing.html').read_bytes()

def extract_filename(part):
    # Extract the filename from the part
    headers, _, _ = part.partition(b'\r\n\r\n')
    headers = headers.decode()
    for line in headers.splitlines():
        if 'filename="' in line:
            return line.split('filename="')[1].split('"')[0]
    return None

def extract_file_content(part):
    # Extract the file content from the part
    _, content = part.split(b'\r\n\r\n', 1)
    return content.rstrip(b'\r\n--')

class Server(BaseHTTPRequestHandler):
    def do_GET(self):
        print(self.path)

        if len(self.path) > 100:
            self._response(400, "Error.")

        if self.path.startswith('/things'):
            return self._serve_image()

        elif self.path.startswith('/'):
            return self._serve_index()

    def _serve_image(self):
        self.send_response(200)
        #self.send_header("Content-Type", "text/html")

        # Tell the browser to cached the image
        self.send_header("Cache-Control", "max-age=31536000, immutable")

        self.end_headers()

        # Directory traversal vulnerability right here
        # UPDATE actually maybe not
        # try it:
        # `curl 'localhost:8085/things/../../../../../../../../etc/man.conf'`
        # Seems like BaseHTTPRequestHandler has something builtin for this?
        # Or is it Curl that's programmed to be non-hostile?

        self.wfile.write(
            Path(self.path.lstrip('/')).read_bytes()
            )

    def _serve_index(self):

        ## Get page ##

        page_match = re.findall(r"\?page=(\d+)", self.path)
        if len(page_match) == 0:
            page = 1
        elif len(page_match) > 1:
            self._response(400, 'Error.')
            return
        elif len(page_match) == 1:
            page_str = page_match[0]
            if len(page_str) > 10:
                self._response(400, 'Error.')
                return
            try:
                page = int(page_str)
            except:
                self._response(400, 'Error.')
                return
            if page > 100000:
                self._response(400, 'Error.')
                return
            elif page < 0:
                self._response(400, 'Error.')
                return
        else:
            assert False


        PER_PAGE = 100

        if page == 0:
            window_start = 0
            window_end = 99999999999
        else:
            window_start = (page - 1) * PER_PAGE
            window_end = page * PER_PAGE

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()

        images = tuple(
            sorted(
                filter(
                    lambda x:
                        x.stem.isnumeric()
                        and x.suffix != '.txt'
                        and not x.name.startswith('.'),
                    Path('things').glob('*')
                    ),
                key=lambda x: int(x.stem),
                reverse=True
                )
            )[window_start:window_end]

        self.wfile.write(
            html_page_full.replace(
                b'__THINGS__',
                b''.join((
                    html_thing
                        .replace(b'__IMAGE__', str(image).encode('ascii'))
                        .replace(
                            b'__COMMENT__',
                            html.escape(
                                image.with_suffix('.txt').read_text()
                                ).encode('utf-8')
                            )
                        .replace(
                            b'__ID__',
                            image.stem.encode('ascii')
                            )
                    for image in images
                    ))
                )
            )

    def do_POST(self):
        if self.path == '/':
            return self._add_thing()

        elif self.path.startswith('/update'):
            return self._update_thing()

        elif self.path.startswith('/delete'):
            return self._delete_thing()

    def _add_thing(self):
        now = int(time.time())

        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)

        # Parse the data manually
        boundary = self.headers['Content-Type'].split('=')[1].encode()
        parts = post_data.split(boundary)
        
        for part in parts:
            if b'name="comment"' in part:
                Path(f"things/{now}.txt").write_bytes(
                    extract_file_content(part)
                    .replace(b'\r\n', b'\n')
                    )

            elif b'filename' in part:

                filename = extract_filename(part)

                if not filename:
                    continue

                path = Path(f"things/{now}").with_suffix(Path(filename).suffix)
                path.write_bytes(
                    extract_file_content(part)
                    )
            
        #self.send_response(200)
        #self.end_headers()
        #self.wfile.write(b'file uploaded.')
        return self._serve_index()
    
    def _update_thing(self):

        thing = self.path.lstrip('/update').rstrip('/')

        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)

        # Parse the data manually
        boundary = self.headers['Content-Type'].split('=')[1].encode()
        parts = post_data.split(boundary)
        
        for part in parts:
            if b'name="comment"' in part:
                Path(f"things/{thing}.txt").write_bytes(
                    extract_file_content(part)
                    .replace(b'\r\n', b'\n')
                    )
                break

        #return self._serve_index()
        self._response(200, "Updated successfully.")
    
    def _delete_thing(self):
        thing = self.path.lstrip('/delete').rstrip('/')
        try:
            for path in Path('things').glob(f'{thing}*'):
                shutil.move(
                    path,
                    Path('trash') / path.name
                    )
            #return self._serve_index()
            self._response(200, "Deleted successfully.")
        except:
            self._response(400, "Error.")

    def _response(self, code: int, message: str):
        self.send_response(code)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(message.encode('utf8'))

    def _303(self, url):
        self.send_response(303)
        self.send_header('Location', url)
        self.end_headers()


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8085), Server)
    server.serve_forever()


