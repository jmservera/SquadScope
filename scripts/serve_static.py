#!/usr/bin/env python3
"""Static file server that compresses text responses.

The production site is hosted on GitHub Pages, which serves text assets with
gzip/brotli compression. A plain ``python -m http.server`` sends everything
uncompressed, so Lighthouse's ``uses-text-compression`` audit penalises pages
for transfer weight that never reaches real users. Serving compressed responses
here makes the local quality gate measure the same conditions as production.
"""

from __future__ import annotations

import argparse
import gzip
import os
from functools import partial
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import quote, urlsplit, urlunsplit

import brotli

# Content types GitHub Pages compresses. Binary assets (images, fonts) are left
# untouched because they are already compressed.
COMPRESSIBLE_TYPES = frozenset(
    {
        "text/html",
        "text/css",
        "text/plain",
        "text/xml",
        "text/javascript",
        "application/javascript",
        "application/json",
        "application/xml",
        "application/manifest+json",
        "application/rss+xml",
        "image/svg+xml",
    }
)


def accepted_encodings(value: str) -> dict[str, float]:
    """Parse Accept-Encoding values into normalized quality weights."""
    encodings: dict[str, float] = {}
    for item in value.split(","):
        parts = [part.strip() for part in item.split(";")]
        encoding = parts[0].lower()
        if not encoding:
            continue
        quality = 1.0
        for parameter in parts[1:]:
            if parameter.lower().startswith("q="):
                try:
                    quality = max(0.0, min(1.0, float(parameter[2:])))
                except ValueError:
                    quality = 0.0
        encodings[encoding] = quality
    return encodings


def select_encoding(value: str) -> str | None:
    """Prefer Brotli, then gzip, when the client assigns a positive quality."""
    encodings = accepted_encodings(value)
    wildcard = encodings.get("*", 0.0)
    for encoding in ("br", "gzip"):
        if encodings.get(encoding, wildcard) > 0:
            return encoding
    return None


class CompressionHandler(SimpleHTTPRequestHandler):
    """Serve files with negotiated compression for eligible text responses."""

    def do_HEAD(self) -> None:  # noqa: N802 - http.server naming
        self._serve(include_body=False)

    def do_GET(self) -> None:  # noqa: N802 - http.server naming
        self._serve(include_body=True)

    def _serve(self, *, include_body: bool) -> None:
        path = self.translate_path(self.path)

        if os.path.isdir(path):
            if not self.path.endswith("/"):
                # Sanitise the request path before echoing it into the Location
                # header to avoid HTTP response splitting.
                split = urlsplit(self.path)
                location = urlunsplit(("", "", quote(split.path) + "/", split.query, ""))
                self.send_response(HTTPStatus.MOVED_PERMANENTLY)
                self.send_header("Location", location)
                self.end_headers()
                return
            index = os.path.join(path, "index.html")
            if os.path.isfile(index):
                path = index
            else:
                self.send_error(HTTPStatus.NOT_FOUND, "Directory listing disabled")
                return

        if not os.path.isfile(path):
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return

        try:
            with open(path, "rb") as handle:
                body = handle.read()
        except OSError:
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return

        content_type = self.guess_type(path)
        base_type = content_type.split(";", 1)[0].strip()
        encoding = select_encoding(self.headers.get("Accept-Encoding", ""))
        if base_type not in COMPRESSIBLE_TYPES:
            encoding = None

        if encoding == "br":
            body = brotli.compress(body, quality=5)
        elif encoding == "gzip":
            body = gzip.compress(body, compresslevel=6)

        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        if encoding:
            self.send_header("Content-Encoding", encoding)
        if base_type in COMPRESSIBLE_TYPES:
            self.send_header("Vary", "Accept-Encoding")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()

        if include_body:
            self.wfile.write(body)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", default="public", help="Directory to serve")
    parser.add_argument("--bind", default="127.0.0.1", help="Address to bind")
    parser.add_argument("--port", type=int, default=1313, help="Port to listen on")
    args = parser.parse_args()

    handler = partial(CompressionHandler, directory=args.directory)
    with ThreadingHTTPServer((args.bind, args.port), handler) as server:
        server.serve_forever()


if __name__ == "__main__":
    main()
