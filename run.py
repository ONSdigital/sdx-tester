from app import app, start

sdx_tester = """
  ____  ______  __   _____         _            
 / ___||  _ \ \/ /  |_   _|__  ___| |_ ___ _ __ 
 \___ \| | | \  /_____| |/ _ \/ __| __/ _ \ '__|
  ___) | |_| /  \_____| |  __/\__ \ ||  __/ |   
 |____/|____/_/\_\    |_|\___||___/\__\___|_|   
                                                
"""

if __name__ == '__main__':
    start()
    app.jinja_env.auto_reload = True
    app.secret_key = '12345'  # This is required for python flash cards
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    print(sdx_tester)
    app.run(host='0.0.0.0', port=5000)
