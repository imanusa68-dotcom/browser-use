"""Deterministic local fixture server for browser-use benchmarks.

Pages simulate real-world patterns: search, forms, tables/pagination,
dropdowns, modals/cookie banners, heavy DOM, slow-loading pages.
No external network => reproducible latency.
"""

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

PRODUCTS = [
	{'id': i, 'name': f'Product {i}', 'price': 10 + i * 3, 'category': ['Books', 'Tools', 'Toys'][i % 3]} for i in range(1, 61)
]

BASE_CSS = '<style>body{font-family:sans-serif;margin:20px}input,select,button{padding:6px;margin:4px}table{border-collapse:collapse}td,th{border:1px solid #ccc;padding:6px}.modal{position:fixed;top:20%;left:30%;background:#fff;border:2px solid #333;padding:20px;z-index:10}.overlay{position:fixed;inset:0;background:rgba(0,0,0,.4);z-index:9}</style>'


def page(title, body):
	return f'<!DOCTYPE html><html><head><title>{title}</title>{BASE_CSS}</head><body>{body}</body></html>'.encode()


class Handler(BaseHTTPRequestHandler):
	def log_message(self, *a):
		pass

	def _send(self, content: bytes, code=200, ctype='text/html'):
		self.send_response(code)
		self.send_header('Content-Type', ctype)
		self.send_header('Content-Length', str(len(content)))
		self.end_headers()
		self.wfile.write(content)

	def do_POST(self):
		length = int(self.headers.get('Content-Length', 0))
		body = self.rfile.read(length).decode()
		params = parse_qs(body)
		path = urlparse(self.path).path
		if path == '/form/submit':
			name = params.get('name', [''])[0]
			email = params.get('email', [''])[0]
			country = params.get('country', [''])[0]
			ok = bool(name and email and '@' in email and country)
			msg = f'SUCCESS: registered {name} ({email}) from {country}' if ok else 'ERROR: missing fields'
			self._send(page('Form Result', f'<h1 id="result">{msg}</h1>'))
		elif path == '/login/submit':
			u = params.get('username', [''])[0]
			p = params.get('password', [''])[0]
			if u == 'admin' and p == 'secret123':
				self._send(page('Dashboard', '<h1 id="welcome">Welcome, admin! Balance: $4521.77</h1>'))
			else:
				self._send(page('Login failed', '<h1 id="error">Invalid credentials</h1><a href="/login">Try again</a>'))
		else:
			self._send(page('404', 'not found'), 404)

	def do_GET(self):
		parsed = urlparse(self.path)
		path = parsed.path
		q = parse_qs(parsed.query)

		if path == '/':
			self._send(
				page(
					'Fixture Home',
					'<h1>Test Site</h1><ul>'
					'<li><a href="/search">Search</a></li>'
					'<li><a href="/form">Registration form</a></li>'
					'<li><a href="/table?page=1">Product table</a></li>'
					'<li><a href="/login">Login</a></li>'
					'<li><a href="/modal">Page with modal</a></li>'
					'<li><a href="/heavy">Heavy page</a></li>'
					'</ul>',
				)
			)
		elif path == '/search':
			query = q.get('q', [''])[0]
			results = ''
			if query:
				matches = [p for p in PRODUCTS if query.lower() in p['name'].lower() or query.lower() in p['category'].lower()]
				results = '<ul id="results">' + ''.join(f'<li>{p["name"]} — ${p["price"]} ({p["category"]})</li>' for p in matches[:10]) + '</ul>'
				results += f'<p id="count">{len(matches)} results found</p>'
			self._send(
				page(
					'Search',
					f'<h1>Product Search</h1><form action="/search" method="get">'
					f'<input type="text" name="q" placeholder="Search products" value="{query}">'
					f'<button type="submit">Search</button></form>{results}',
				)
			)
		elif path == '/form':
			self._send(
				page(
					'Registration',
					'<h1>Register</h1><form action="/form/submit" method="post">'
					'<label>Name: <input type="text" name="name"></label><br>'
					'<label>Email: <input type="email" name="email"></label><br>'
					'<label>Country: <select name="country"><option value="">--</option>'
					'<option>USA</option><option>Germany</option><option>Japan</option></select></label><br>'
					'<button type="submit">Register</button></form>',
				)
			)
		elif path == '/table':
			pg = int(q.get('page', ['1'])[0])
			per = 10
			chunk = PRODUCTS[(pg - 1) * per : pg * per]
			rows = ''.join(f'<tr><td>{p["id"]}</td><td>{p["name"]}</td><td>${p["price"]}</td><td>{p["category"]}</td></tr>' for p in chunk)
			nav = ''
			if pg > 1:
				nav += f'<a id="prev" href="/table?page={pg - 1}">Previous</a> '
			if pg * per < len(PRODUCTS):
				nav += f'<a id="next" href="/table?page={pg + 1}">Next</a>'
			self._send(
				page(
					'Products',
					f'<h1>Products (page {pg})</h1><table><tr><th>ID</th><th>Name</th><th>Price</th><th>Category</th></tr>{rows}</table>{nav}',
				)
			)
		elif path == '/login':
			self._send(
				page(
					'Login',
					'<h1>Login</h1><form action="/login/submit" method="post">'
					'<label>Username: <input type="text" name="username"></label><br>'
					'<label>Password: <input type="password" name="password"></label><br>'
					'<button type="submit">Sign in</button></form>',
				)
			)
		elif path == '/modal':
			self._send(
				page(
					'Modal page',
					'<div id="cookiebar" class="overlay"></div>'
					'<div id="cookiemodal" class="modal"><p>We use cookies!</p>'
					'<button onclick="document.getElementById(\'cookiebar\').remove();document.getElementById(\'cookiemodal\').remove()">Accept cookies</button></div>'
					'<h1>Article</h1><p id="secret">The launch code is FALCON-42.</p>',
				)
			)
		elif path == '/heavy':
			# 800 nodes, many interactive
			items = ''.join(
				f'<div><span>Row {i}</span><button onclick="this.textContent=\'clicked\'">Btn {i}</button>'
				f'<a href="/heavy#{i}">link{i}</a></div>'
				for i in range(400)
			)
			self._send(page('Heavy', f'<h1>Heavy page</h1><p id="target">Magic number: 7319</p>{items}'))
		elif path == '/slow':
			import time as _t

			_t.sleep(2.0)
			self._send(page('Slow', '<h1 id="loaded">Slow page loaded. Token: ZEBRA-9</h1>'))
		elif path == '/delayed_field':
			# Regression P4: field + submit appear 1.5s AFTER load (setTimeout render).
			# An agent that acts on the pre-render DOM must wait, not error.
			self._send(
				page(
					'Delayed field',
					'<h1>Delayed form</h1><div id="slot"><p id="loading">Loading form…</p></div>'
					'<div id="out"></div>'
					'<script>setTimeout(function(){'
					"document.getElementById('slot').innerHTML="
					'\'<input id="code" type="text" placeholder="enter code">\''
					'+\'<button id="go" onclick="document.getElementById(\\\'out\\\').textContent=\\\'CODE:\\\'+document.getElementById(\\\'code\\\').value">Submit code</button>\';'
					'}, 1500);</script>',
				)
			)
		elif path == '/masked_phone':
			# Regression P1: input formatter reformats digits as (XXX) XXX-XXXX on every
			# 'input' event. Raw insertText of digits => readback mismatch => per-char fallback.
			self._send(
				page(
					'Masked phone',
					'<h1>Phone form</h1>'
					'<input id="phone" type="text" inputmode="numeric" data-mask="(000) 000-0000" placeholder="phone">'
					'<button id="save" onclick="document.getElementById(\'res\').textContent=\'PHONE:\'+document.getElementById(\'phone\').value">Save</button>'
					'<div id="res"></div>'
					'<script>'
					"var p=document.getElementById('phone');"
					"p.addEventListener('input',function(){"
					"var d=p.value.replace(/\\D/g,'').slice(0,10);var o=d;"
					"if(d.length>6)o='('+d.slice(0,3)+') '+d.slice(3,6)+'-'+d.slice(6);"
					"else if(d.length>3)o='('+d.slice(0,3)+') '+d.slice(3);"
					"else if(d.length>0)o='('+d;"
					'if(p.value!==o)p.value=o;});'
					'</script>',
				)
			)
		elif path == '/shifting_button':
			# Regression P2: a lazy banner inserts itself ABOVE the target button ~300ms
			# after scroll starts, shifting the button down. A fixed 50ms post-scroll wait
			# mis-clicks; rect-stability waiting must catch the shift.
			filler = ''.join(f'<p>filler line {i}</p>' for i in range(80))
			self._send(
				page(
					'Shifting button',
					f'<h1>Scroll down</h1>{filler}'
					'<div id="bannerslot"></div>'
					'<button id="target" onclick="document.getElementById(\'clickres\').textContent=\'TARGET-HIT\'">Confirm order</button>'
					'<div id="clickres"></div>'
					'<script>'
					'var injected=false;'
					"window.addEventListener('scroll',function(){"
					'if(injected)return;injected=true;'
					'setTimeout(function(){'
					"var b=document.createElement('div');b.style.height='120px';b.style.background='#fc0';"
					"b.textContent='LAZY BANNER LOADED';document.getElementById('bannerslot').appendChild(b);"
					'},300);});'
					'</script>',
				)
			)
		elif path == '/react_input':
			# Regression P1: controlled-component pattern — keystrokes/inserts are reverted
			# unless a proper InputEvent reaches the framework's onInput handler, which
			# mirrors the value into internal state and re-renders from state.
			self._send(
				page(
					'React-like controlled input',
					'<h1>Controlled input</h1>'
					'<input id="ctl" type="text" placeholder="type here">'
					'<button id="show" onclick="document.getElementById(\'state\').textContent=\'STATE:\'+window.__state">Show state</button>'
					'<div id="state"></div>'
					'<script>'
					"window.__state='';"
					"var el=document.getElementById('ctl');"
					'function render(){if(el.value!==window.__state)el.value=window.__state;}'
					"el.addEventListener('input',function(e){window.__state=el.value;requestAnimationFrame(render);});"
					'setInterval(render,50);'
					'</script>',
				)
			)
		else:
			self._send(page('404', 'not found'), 404)


if __name__ == '__main__':
	ap = argparse.ArgumentParser()
	ap.add_argument('--port', type=int, default=8901)
	args = ap.parse_args()
	print(f'Fixture server on :{args.port}')
	ThreadingHTTPServer(('127.0.0.1', args.port), Handler).serve_forever()
