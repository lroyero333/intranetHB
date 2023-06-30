from main.routes import request, app, mysql, bcrypt, session, redirect, render_template, url_for
import json
from main.routes import request, app, mysql, bcrypt, session, redirect, render_template, url_for
from main.run import app, request, bcrypt, mysql, redirect, render_template, url_for, session, jsonify, flash


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


@app.errorhandler(413)
def request_entity_too_large(error):
    return render_template('error/error-413.html'), 413


@app.errorhandler(FileNotFoundError)
def handle_file_not_found_error(e):
    flash("Lo sentimos, no se puede encontrar la imagen solicitada en este momento. Por favor, intenta de nuevo más tarde o asegúrate de que el archivo de imagen existe correctamente.",'error')
    return render_template('error/error-404NoFile.html'), 404
