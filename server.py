import asyncio
from quart import Quart
#from flask_cors import CORS
import glob
from types import ModuleType
from datetime import datetime


app = Quart(__name__, static_url_path='/public', static_folder='public', template_folder="templates")
#CORS(app)

import os


last_restart = str(datetime.now())
@app.route('/last_restart')
async def last_restart_handler():
    print("last restart")
    return last_restart


# asdf

# import all modules/
for t in glob.glob('modules/*.py'):
   __import__(t.replace('/','.')[0:-3])
modules = __import__('modules')

# register all module endpoints with flask
for k, m in modules.__dict__.items():
    if isinstance(m, ModuleType):
        m.register(app)

SSL_PROTOCOLS = (asyncio.sslproto.SSLProtocol,)
try:
    import uvloop.loop
except ImportError:
    pass
else:
    SSL_PROTOCOLS = (*SSL_PROTOCOLS, uvloop.loop.SSLProtocol)

def ignore_aiohttp_ssl_eror(loop):
    """Ignore aiohttp #3535 / cpython #13548 issue with SSL data after close

    There is an issue in Python 3.7 up to 3.7.3 that over-reports a
    ssl.SSLError fatal error (ssl.SSLError: [SSL: KRB5_S_INIT] application data
    after close notify (_ssl.c:2609)) after we are already done with the
    connection. See GitHub issues aio-libs/aiohttp#3535 and
    python/cpython#13548.

    Given a loop, this sets up an exception handler that ignores this specific
    exception, but passes everything else on to the previous exception handler
    this one replaces.

    Checks for fixed Python versions, disabling itself when running on 3.7.4+
    or 3.8.

    """

    orig_handler = loop.get_exception_handler()

    def ignore_ssl_error(loop, context):
        if context.get("message") == "Task exception was never retrieved":
            return
        if context.get("message") in {
            "SSL error in data received",
            "Fatal error on transport",
        }:
            # validate we have the right exception, transport and protocol
            exception = context.get('exception')
            protocol = context.get('protocol')
            if (
                isinstance(exception, ssl.SSLError)
                and exception.reason == 'APPLICATION_DATA_AFTER_CLOSE_NOTIFY'
                and isinstance(protocol, SSL_PROTOCOLS)
            ):
                if loop.get_debug():
                    asyncio.log.logger.debug('Ignoring asyncio SSL KRB5_S_INIT error')
                return
        if orig_handler is not None:
            orig_handler(loop, context)
        else:
            loop.default_exception_handler(context)

    loop.set_exception_handler(ignore_ssl_error)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    ignore_aiohttp_ssl_eror(loop)

    run_task = app.run_task(host='0.0.0.0', port=8081, certfile='bodygen_re.crt', keyfile='bodygen_re.key')

    loop.run_until_complete(asyncio.gather(
        run_task,
    ))

