
import html
import shutil
from pathlib import Path
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

page = Path('page.html').read_bytes()
thing = Path('thing.html').read_bytes()

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
        if self.path == '/':
            return self._serve_index()

        elif self.path.startswith('/things'):
            return self._serve_image()

    def _serve_image(self):
        self.send_response(200)
        #self.send_header("Content-Type", "text/html")

        # Tell the browser to cached the image
        self.send_header("Cache-Control", "max-age=31536000, immutable")

        self.end_headers()
        # Directory traversal vulnerability right here
        self.wfile.write(
            Path(self.path.lstrip('/')).read_bytes()
            )

    def _serve_index(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()

        images = tuple(
            image
            for image in Path('things').glob('*')
            if image.suffix != '.txt'
                and not image.name.startswith('.')
            )

        self.wfile.write(
            page.replace(
                b'__THINGS__',
                b''.join((
                    thing
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
                    for image in sorted(images, reverse=True)
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

        return self._serve_index()
    
    def _delete_thing(self):
        thing = self.path.lstrip('/delete').rstrip('/')
        try:
            for path in Path('things').glob(f'{thing}*'):
                shutil.move(
                    path,
                    Path('trash') / path.name
                    )
            return self._serve_index()
        except:
            self.send_response(400)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b'Error.')


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8085), Server)
    server.serve_forever()


