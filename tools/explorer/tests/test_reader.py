"""Reader security and rendering checks using a small disposable checkout."""
import http.client
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from explorer import Explorer
import reader
from reader import IMAGE_TYPES, local_url, reader_page, reader_path, render_markdown
from server import ExplorerHTTPServer
from source import InvalidSelection


class ReaderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.explorer = Explorer(self.root)
        self.addCleanup(self.explorer.close)
        self.doc = 'recipes/demo/README.md'
        for name in ('README.md', 'CONTRIBFEST.md', 'CONTRIBUTING.md', 'WORKFLOW.md',
                     'tools/explorer/README.md', self.doc,
                     'recipes/demo/python/bare/main.py',
                     'contribfest/kubecon-na-2026/setup.md',
                     'contribfest/kubecon-na-2026/README.md',
                     'contribfest/kubecon-na-2026/images/banner.png',
                     'recipes/demo/docs/images/screen.png',
                     'recipes/demo/docs/images/screen.JPG',
                     'recipes/demo/docs/images/screen.svg',
                     'recipes/demo/private.txt', 'recipes/demo/docs/secret.md'):
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('# Hello\n')

    def render(self, source):
        return render_markdown(self.explorer, self.doc, source)

    def test_allow_list_and_traversal_symlink_rejections(self):
        for name in ('README.md', 'CONTRIBFEST.md', 'CONTRIBUTING.md', 'WORKFLOW.md',
                     'tools/explorer/README.md', self.doc,
                     'contribfest/kubecon-na-2026/setup.md'):
            self.assertEqual(reader_path(self.explorer, name), self.root / name)
        for name in ('recipes/demo/docs/images/screen.png',
                     'contribfest/kubecon-na-2026/images/banner.png'):
            self.assertEqual(reader_path(self.explorer, name, image=True), self.root / name)
        for name in ('../README.md', str(self.root / 'README.md'),
                     'recipes/demo/../../README.md', 'recipes/demo/private.txt',
                     'recipes/demo/docs/secret.md', 'recipes/demo/.hidden/README.md',
                     'recipes/demo/tests/README.md', 'recipes/demo/docs/images/screen.png',
                     'contribfest/other/setup.md', ''):
            with self.subTest(name=name), self.assertRaises(InvalidSelection):
                reader_path(self.explorer, name)
        for name in ('README.md', 'recipes/demo/private.txt', 'recipes/demo/docs/secret.md'):
            with self.assertRaises(InvalidSelection):
                reader_path(self.explorer, name, image=True)
        (self.root / 'recipes/demo/docs/images/link.png').symlink_to(self.root / 'README.md')
        with self.assertRaises(InvalidSelection):
            reader_path(self.explorer, 'recipes/demo/docs/images/link.png', image=True)
        (self.root / 'recipes/alias').symlink_to(self.root / 'recipes/demo', target_is_directory=True)
        with self.assertRaises(InvalidSelection):
            reader_path(self.explorer, 'recipes/alias/README.md')

    def test_renderer_blocks_and_source_html_are_escaped(self):
        result = self.render('# Heading\n\nA **bold** and `inline` paragraph.\n\n'
                             '| Col | Other |\n| --- | --- |\n| one | two |\n\n'
                             '- first\n- second\n\n1. ordered\n2. again\n\n'
                             '```html\n<script>alert(1)</script>\n```\n\n'
                             '<img src=x onerror=alert(1)>')
        for text in ('<h1 id="heading">', '<strong>bold</strong>', '<code>inline</code>',
                     '<table>', '<th>Col</th>', '<td>two</td>', '<ul>', '<ol>',
                     '&lt;script&gt;', '&lt;img src=x'):
            self.assertIn(text, result)
        self.assertNotIn('<script>', result)
        self.assertNotIn('<img src=x', result)

    def test_links_images_and_unsafe_schemes(self):
        result = self.render('[setup](../../contribfest/kubecon-na-2026/setup.md#before) '
                             '[code](python/bare/main.py) [web](https://example.com/?a=1&b=2) '
                             '![screen](docs/images/screen.png) '
                             '[bad](javascript:alert) ![remote](https://example.com/p.png) '
                             '[hidden](docs/secret.md) [scheme](//example.com)')
        self.assertIn('/doc?path=contribfest%2Fkubecon-na-2026%2Fsetup.md#before', result)
        self.assertIn('/source?path=recipes%2Fdemo%2Fpython%2Fbare%2Fmain.py', result)
        self.assertIn('target="_blank" rel="noopener noreferrer"', result)
        self.assertIn('src="/image?path=recipes%2Fdemo%2Fdocs%2Fimages%2Fscreen.png"', result)
        for unsafe in ('javascript:', 'src="https:', 'href="//'):
            self.assertNotIn(unsafe, result)
        self.assertIn('<code>recipes/demo/docs/secret.md</code>', result)
        self.assertNotIn('secret.md"', result)
        self.assertIsNone(local_url(self.explorer, self.doc, '../../../README.md'))
        self.assertIsNone(local_url(self.explorer, self.doc, '%2fetc/passwd'))
        self.assertIsNone(local_url(self.explorer, self.doc, 'README.md?download=1'))
        self.assertIn('href="#heading"', self.render('[jump](#heading)'))
        ordered = self.render('1. one\n wrapped\n2. two')
        self.assertEqual(ordered.count('<ol>'), 1)
        self.assertIn('<li>one\n wrapped</li>', ordered)
        self.assertIn('<li>two</li>', ordered)
        bullets = self.render('- item\n more\n- next')
        self.assertEqual(bullets.count('<ul>'), 1)
        self.assertIn('<li>item\n more</li>', bullets)
        local = self.render('See [Local\nservices](../../README.md).')
        self.assertIn('<a href="/doc?path=README.md">', local)
        self.assertIn('Local\nservices', local)
        external = self.render('See [Local\nservices](https://example.com/docs).')
        self.assertIn('href="https://example.com/docs"', external)
        self.assertIn('Local\nservices', external)
        hidden = self.render('See [the contract](../../AGENTS.md).')
        self.assertNotIn('<a ', hidden)
        self.assertIn('the contract <code>AGENTS.md</code>', hidden)
        hostile = self.render(
            '![x" onerror="alert(1)](docs/images/screen.png) '
            '[go](https://e.com/"onmouseover="alert(1)) '
            '[data](data:text/html,hi) [js](JaVaScRiPt:alert(1)) '
            '[ent](&#106;avascript:alert(1))')
        self.assertNotIn('onerror="', hostile)
        self.assertNotIn('onmouseover="', hostile)
        self.assertNotIn('javascript:', hostile.lower())
        self.assertIn('&quot;', hostile)

    def test_docs_images_resolve_when_docs_is_skipped(self):
        with patch('reader.SKIP', set(reader.SKIP) | {'docs'}):
            self.assertEqual(
                reader_path(self.explorer, 'recipes/demo/docs/images/screen.png', image=True),
                self.root / 'recipes/demo/docs/images/screen.png')

    def test_http_routes_and_image_content_types_keep_security_headers(self):
        server = ExplorerHTTPServer(('127.0.0.1', 0), self.explorer)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            for route, name, expected in (
                ('doc', self.doc, 'text/html; charset=utf-8'),
                ('source', self.doc, 'text/plain; charset=utf-8'),
                *(('image', 'recipes/demo/docs/images/screen' + ext, kind)
                  for ext, kind in (('.png', 'image/png'), ('.JPG', 'image/jpeg'), ('.svg', 'image/svg+xml'))),
            ):
                connection = http.client.HTTPConnection('127.0.0.1', server.server_port)
                connection.request('GET', '/' + route + '?path=' + quote(name, safe=''))
                response = connection.getresponse()
                body = response.read().decode()
                self.assertEqual(response.status, 200)
                self.assertEqual(response.getheader('Content-Type'), expected)
                self.assertEqual(response.getheader('X-Content-Type-Options'), 'nosniff')
                csp = response.getheader('Content-Security-Policy')
                self.assertIn("script-src 'self'", csp)
                if name.endswith('.svg'):
                    self.assertIn('; sandbox', csp)
                else:
                    self.assertNotIn('sandbox', csp)
                if route == 'doc':
                    self.assertIn('<h1 id="hello">Hello</h1>', body)
                    self.assertIn('/theme.js', body)
                connection.close()
            connection = http.client.HTTPConnection('127.0.0.1', server.server_port)
            for path in ('/doc?path=..%2FREADME.md', '/image?path=README.md',
                         '/image?path=..%2Fx.png'):
                connection = http.client.HTTPConnection('127.0.0.1', server.server_port)
                connection.request('GET', path)
                response = connection.getresponse()
                self.assertEqual(response.status, 422, path)
                response.read()
                connection.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


if __name__ == '__main__':
    unittest.main()
