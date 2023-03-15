from main.app import app, request,bcrypt,mysql,redirect, render_template, url_for,session

@app.route('/calendario')
def calendario():
    if not 'login' in session:
        return redirect('/')
    return render_template('templates/light/app-calendar.html')