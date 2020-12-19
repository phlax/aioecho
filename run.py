
import asyncio
import socket
import ssl

from aiohttp import web

runners = []

async def start_site(app, address='0.0.0.0', port=9100, tls=False):
    runner = web.AppRunner(app)
    runners.append(runner)
    await runner.setup()

    if tls:
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.load_cert_chain('/certs/servercert.pem', '/certs/serverkey.pem')
        site = web.TCPSite(runner, address, port, ssl_context=ssl_context)
    else:
        site = web.TCPSite(runner, address, port)
    await site.start()

loop = asyncio.get_event_loop()


async def _response(protocol, request):
    content = await request.text()
    return web.json_response(
        dict(protocol=request.scheme,
             http=(f'{request.version.major}/'
                   f'{request.version.minor}'),
             method=request.method,
             remote=request.remote,
             path=request.path,
             keep_alive=request.keep_alive,
             headers=dict(request.headers),
             content=content,
             cookies=dict(request.cookies),
             query=dict(request.query),
             os=dict(
                 hostname=socket.gethostname())))


async def http_handler(request):
    return await _response('http', request)


async def https_handler(request):
    return await _response('https', request)


app1 = web.Application()
app1.router.add_route('*', '/', http_handler)
app2 = web.Application()
app2.router.add_route('*', '/', https_handler)

loop.create_task(start_site(app1))
loop.create_task(start_site(app2, port=9101, tls=True))

try:
    loop.run_forever()
except:
    pass
finally:
    for runner in runners:
        loop.run_until_complete(runner.cleanup())
