from flask import Flask, send_from_directory
import os

from msgUnit.devcontrolpanelapi import main as controlpanelAPI
from msgUnit.appcenterapi import manageApps
from msgUnit.deviceagentapi import main as deviceAgent
from msgUnit.realtimeinfoapi import main as realtimeInfo
from msgUnit.devtimeinfoapi import main as timeInfo
from msgUnit.imageapi import imageApi as imgAPI

from config.normal import toolsDefine

import logging
logging.basicConfig(level=logging.ERROR,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    handlers = [logging.FileHandler('my.log', 'w', 'utf-8'),])

toolsDef=toolsDefine()

app = Flask(__name__)
timeInfo(app)
realtimeInfo(app)
imgAPI(app)
manageApps(app)
controlpanelAPI(app)
deviceAgent(app)

# point to public folder
root = toolsDef.public

# open other file permission to outsie
@app.route('/<path:path>', methods=['GET'])
def static_proxy(path):
    return send_from_directory(root, path)

@app.route('/')
def redirect_to_index():
    return send_from_directory(root, 'index.html')
