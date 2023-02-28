# flask_application
Module represents the map of top song and its countries.


## Instalation
```bash
pip install pandas
pip install folium
pip install flask
```

## Libraries to import
```bash
from flask import Flask, render_template, request

import folium
from dotenv import load_dotenv
import os
import base64
import requests
import json
import pandas as pd
```

## Flask part
```bash
app = Flask(__name__)
@app.route("/")
@app.route("/home")
def home():
    return render_template('input_page.html')

@app.route("/search_countries", methods = ['POST'])
def search():
    artist = request.form['artist']
    return create_map(artist)
app.run(debug=True)
```
