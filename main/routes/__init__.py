from flask import render_template, redirect, request, url_for, session
import bcrypt

from main.app import app, mysql

from main.templates.login import login

from main.templates.register import register

from main.templates.calendario import calendario



    
@app.route('/cerrar')
def cerrar():
    session.clear()
    return redirect(url_for('login'))

url_inicio='/inicio'
    
@app.route('/inicio')
def inicio():
    if not 'login' in session:
        return redirect('/login')
    return render_template('sitio/index.html')

@app.route('/Noticias')

def noticias():
    if not 'login' in session:
        return redirect('/login')
    return render_template('sitio/Noticias.html')

@app.route('/proyectos')
def programacion():
    if not 'login' in session:
        return redirect('/login')
    return render_template('sitio/proyectos.html')

@app.route('/base')
def base():
    return render_template('sitio/base.html')
