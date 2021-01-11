from app import app, socketio

if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.secret_key = '12345'
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)