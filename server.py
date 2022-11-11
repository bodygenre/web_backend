from flask import Flask
from flask_cors import CORS
import glob
from types import ModuleType



app = Flask(__name__, static_url_path='/public', static_folder='public', template_folder="templates")
CORS(app)

app.last_query = "shrek 2"



# import all modules/
for t in glob.glob('modules/*.py'):
   __import__(t.replace('/','.')[0:-3])
modules = __import__('modules')



# register all module endpoints with flask
for k, m in modules.__dict__.items():
    if isinstance(m, ModuleType):
        m.register(app)



if __name__ == "__main__":
    #app.run(host='0.0.0.0', port=8081)
    app.run(host='0.0.0.0', port=8081, ssl_context=('bodygen_re.crt', 'bodygen_re.key'))


