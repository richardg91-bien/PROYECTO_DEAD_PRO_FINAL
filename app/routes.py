from flask import Blueprint, render_template, request, redirect
import os
import uuid
import qrcode

from app.db import get_db, init_db
from app.supabase_client import supabase
from ia_service import generar_embedding

main = Blueprint("main", __name__)

@main.route("/")
def index():
    return render_template("index.html")