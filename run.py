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
    print(sdx_tester)
    # TODO when this line is uncommented, every other file submission times out
    # app.debug = True;
    app.run(host='0.0.0.0', port=5000)
