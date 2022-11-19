from flask import *
app = Flask(__name__)



@app.route('/',methods=['GET'])
def entry():
    return render_template('index.html')



@app.route('/index')
def home():
    return render_template('index.html')



@app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('register.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')



@app.route('/prediction', methods=['GET', 'POST'])
def prediction():
    return render_template('prediction.html')



@app.route('/logout')
def logout():
    return render_template('logout.html')

   


        





if __name__ == '__main__':
    app.run(debug=True)