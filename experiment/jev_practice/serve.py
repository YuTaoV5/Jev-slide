"""Serve local slide/demo assets. No inference endpoint and no API keys."""
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import re


class MediaHandler(SimpleHTTPRequestHandler):
    """Support byte ranges so Chrome can seek local MP4 files over HTTP."""

    def send_head(self):
        self._remaining = None
        path = Path(self.translate_path(self.path))
        if not path.is_file():
            return super().send_head()
        try:
            stream = path.open('rb')
        except OSError:
            self.send_error(404)
            return None
        size = path.stat().st_size
        start, end, status = 0, size - 1, 200
        value = self.headers.get('Range', '')
        match = re.fullmatch(r'bytes=(\d*)-(\d*)', value)
        if match and any(match.groups()):
            first, last = match.groups()
            if first:
                start = int(first)
                end = min(int(last), end) if last else end
            else:
                start = max(0, size - int(last))
            if start > end or start >= size:
                stream.close()
                self.send_response(416)
                self.send_header('Content-Range', f'bytes */{size}')
                self.send_header('Content-Length', '0')
                self.end_headers()
                return None
            status = 206
        self.send_response(status)
        self.send_header('Content-Type', self.guess_type(str(path)))
        self.send_header('Accept-Ranges', 'bytes')
        self.send_header('Content-Length', str(max(0, end - start + 1)))
        self.send_header('Last-Modified', self.date_time_string(path.stat().st_mtime))
        if status == 206:
            self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
        self.end_headers()
        stream.seek(start)
        self._remaining = max(0, end - start + 1)
        return stream

    def copyfile(self, source, outputfile):
        if self._remaining is None:
            return super().copyfile(source, outputfile)
        remaining = self._remaining
        while remaining:
            block = source.read(min(65536, remaining))
            if not block:
                break
            outputfile.write(block)
            remaining -= len(block)

if __name__ == '__main__':
    root = Path(__file__).resolve().parents[2]
    print('Offline demos: http://127.0.0.1:8766/experiment/jev_practice/demo.html', flush=True)
    server = ThreadingHTTPServer(('127.0.0.1',8766), partial(MediaHandler,directory=str(root)))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
