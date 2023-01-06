from modules.downloaders.tidal import STATICTIDAL

from sanic import Sanic
from sanic.response import json

app = Sanic()

@app.route("/tidal/search/<query:str>")
async def test(request, query: str):
  # Get parameter type from body
  querytype: str|None = request.args.get("type", None)
  
  q = STATICTIDAL.query(query, querytype.split(",") if querytype else [])
  
  return json({"hello": "world"})

def run(host: str="0.0.0.0", port: int=8000):
  app.run(host=host, port=port)