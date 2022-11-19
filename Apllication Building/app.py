from cloudant.client import Cloudant
client = Cloudant.iam('14f4d73b-0587-43e7-a135-8f0b1ee838e6-bluemix', '_w4Lugdv8gtUI45fihmyuboqra99qGXGD9Ey1hrr6Grz', connect=True)
my_database = client.create_database('my_database')
from flask import *
import os
app = Flask(__name__)



@app.route('/')
def entry():
    return render_template('index.html')



@app.route('/index')
def home():
    return render_template('index.html')



@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/afterreg',methods=['POST'])
def afterreg():
    x = [x for x in request.form.values()]
    print[x]
    data = {
        '_id': x[1], #setting id is optional
        'name': x[0],
        'psw': x[2]
    }
    print(data)
    query = { '_id': {'$eq': data['id']}}

    docs = my_database.get_query_result(query)
    print(docs)

    print(len(docs.all()))

    if(len(docs.all()) ==0):
        url = my_database.create_document(data)
        #response = requests.get(url)
        return render_template('register.html',pred="Registration successful, Please login using your details")
    else:
        return render_template('register.html',pred="You are already a member , please login using your deatils")
    

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/afterlogin')
def afterlogin():
    return render_template('l')

@app.route('/prediction')
def prediction():
    return render_template('prediction.html')

@app.route('/result1')
def result():
    return render_template('result1.html')


@app.route('/logout')
def logout():
    return render_template('logout.html')

@app.route('/resultsf',methods=["GET","POST"])
def res():
    if request.method=="POST":
        f=request.files['image']
        basepath = os.path.dirname(__file__)
        filepath = os.path.join(basepath,'uploads',f.filename)


        





if __name__ == '__main__':
    app.run(debug=True)