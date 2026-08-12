from __future__ import annotations

import gzip
import http.client
import threading
from collections.abc import Iterator
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path

import brotli
import pytest

from scripts.serve_static import CompressionHandler


@pytest.fixture
def static_server(tmp_path: Path) -> Iterator[tuple[str, int]]:
    (tmp_path / "index.html").write_text("<h1>Claracle</h1>" * 100, encoding="utf-8")
    (tmp_path / "repo").mkdir()
    (tmp_path / "repo" / "index.html").write_text("<h1>Repositories</h1>", encoding="utf-8")
    (tmp_path / "image.png").write_bytes(b"\x89PNG\r\n\x1a\n" + bytes(range(64)))
    handler = partial(CompressionHandler, directory=str(tmp_path))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server.server_address
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def request(
    server: tuple[str, int],
    path: str,
    *,
    accept_encoding: str = "",
    method: str = "GET",
) -> tuple[http.client.HTTPResponse, bytes]:
    connection = http.client.HTTPConnection(*server)
    connection.request(method, path, headers={"Accept-Encoding": accept_encoding})
    response = connection.getresponse()
    body = response.read()
    connection.close()
    return response, body


def test_prefers_brotli_and_preserves_response_metadata(
    static_server: tuple[str, int],
) -> None:
    response, body = request(static_server, "/", accept_encoding="gzip, br")

    assert response.status == 200
    assert response.getheader("Content-Encoding") == "br"
    assert response.getheader("Vary") == "Accept-Encoding"
    assert int(response.getheader("Content-Length", "0")) == len(body)
    assert brotli.decompress(body) == b"<h1>Claracle</h1>" * 100


def test_falls_back_to_gzip_when_brotli_is_rejected(
    static_server: tuple[str, int],
) -> None:
    response, body = request(static_server, "/", accept_encoding="br;q=0, gzip;q=0.5")

    assert response.getheader("Content-Encoding") == "gzip"
    assert gzip.decompress(body) == b"<h1>Claracle</h1>" * 100


@pytest.mark.parametrize("accept_encoding", ["identity", "br;q=0, gzip;q=0", ""])
def test_leaves_text_uncompressed_when_encoding_is_not_accepted(
    static_server: tuple[str, int], accept_encoding: str
) -> None:
    response, body = request(static_server, "/", accept_encoding=accept_encoding)

    assert response.getheader("Content-Encoding") is None
    assert response.getheader("Vary") == "Accept-Encoding"
    assert body == b"<h1>Claracle</h1>" * 100


def test_leaves_binary_content_uncompressed(static_server: tuple[str, int]) -> None:
    response, body = request(static_server, "/image.png", accept_encoding="br, gzip")

    assert response.getheader("Content-Encoding") is None
    assert response.getheader("Vary") is None
    assert body == b"\x89PNG\r\n\x1a\n" + bytes(range(64))


def test_head_matches_encoded_get_headers_without_a_body(
    static_server: tuple[str, int],
) -> None:
    get_response, get_body = request(static_server, "/", accept_encoding="br")
    head_response, head_body = request(static_server, "/", accept_encoding="br", method="HEAD")

    assert head_response.status == get_response.status
    assert head_response.getheader("Content-Encoding") == "br"
    assert head_response.getheader("Vary") == "Accept-Encoding"
    assert head_response.getheader("Content-Length") == str(len(get_body))
    assert head_body == b""


def test_directory_query_does_not_trigger_redirect_loop(
    static_server: tuple[str, int],
) -> None:
    response, body = request(static_server, "/repo/?topic=ai-skills")

    assert response.status == 200
    assert body == b"<h1>Repositories</h1>"
