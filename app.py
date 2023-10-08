from flask import Flask, render_template, url_for, request, redirect
from logic import *
from config import path_all_video


""" переменные """
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = path_all_video
app.secret_key = "ASfLlfjsdfdS(*f98sd7fs98FSDFysodfas8df6ysadfiuoGFSDUfy"

from view import *

