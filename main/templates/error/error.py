from main.routes import request, app,mysql,bcrypt,session,redirect,render_template,url_for
import json
from main.routes import request, app, mysql, bcrypt, session, redirect, render_template, url_for
from main.app import app, request, bcrypt, mysql, redirect, render_template, url_for, session, jsonify, flash

@app.errorhandler(404)
def error_404(error):
    return render_template('error/error-404.html')


@app.errorhandler(400)
def error_400(error):
    return render_template('error/error-400.html')


@app.errorhandler(401)
def error_401(error):
    return render_template('error/error-401.html')


@app.errorhandler(403)
def error_403(error):
    return render_template('error/error-403.html')
