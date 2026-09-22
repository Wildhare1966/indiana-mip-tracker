"""MRD local server — same as `python -m http.server`, but HTML is never cached.

WHY THIS EXISTS (2026-09-22)
----------------------------
Stock `http.server` sends `Last-Modified` and **no `Cache-Control` and no
`ETag`**. With no explicit directive a browser may apply heuristic freshness and
keep serving its stored copy for as long as it likes — so an edit to
`p168-ops.html` or `mrd-ad682070b7/index.html` can be live on disk, served
correctly by curl, and still invisible in Chrome.

That is not hypothetical. A P202 ops-console card was verified byte-identical on
disk, returned by curl, and rendering in a clean browser, while the operator's
Chrome showed the old page. The standing workaround was "open it with `?v=`",
which only works when you remember, and the person who most needs it is the one
who does not know the page changed.

HTML only. Static assets already carry their own cache-busters
(`styles.css?v=p202r1`) and re-fetching a megabyte of JS on every navigation
would be a real cost for no benefit — the stale-document problem is a document
problem.
"""
import functools
import http.server
import socketserver
import sys

PORT = 8778
BIND = "127.0.0.1"


class NoCacheHTMLHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        ctype = self.headers_buffer_content_type()
        if ctype.startswith("text/html"):
            # no-store: do not write it to disk at all. must-revalidate + max-age=0
            # cover proxies and older browsers that treat no-store loosely.
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
        super().end_headers()

    def headers_buffer_content_type(self):
        """Read the Content-Type this response is about to send.

        SimpleHTTPRequestHandler stashes pending headers in _headers_buffer as
        raw bytes; there is no public accessor, so parse it rather than guess
        from the path (a directory listing is html with no .html extension).
        """
        for raw in getattr(self, "_headers_buffer", []) or []:
            try:
                line = raw.decode("latin-1")
            except Exception:
                continue
            if line.lower().startswith("content-type:"):
                return line.split(":", 1)[1].strip().lower()
        return ""

    def log_message(self, fmt, *args):
        # Same quiet behaviour the hidden-window launcher relied on.
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def main():
    # Optional port override so the handler can be exercised without stopping
    # the one already holding 8778.
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    handler = functools.partial(NoCacheHTMLHandler, directory=None)
    with Server((BIND, port), handler) as httpd:
        sys.stderr.write("MRD server on http://%s:%d (HTML: no-store)\n" % (BIND, port))
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
