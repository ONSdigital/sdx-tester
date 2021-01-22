from app import app, socketio

if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.secret_key = '12345'  # This is required for python flash cards
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    socketio.run(app, host='0.0.0.0', port=5000, use_reloader=False)
