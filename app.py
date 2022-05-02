
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import datetime
import requests
from flask import Flask, redirect, render_template, request, flash, url_for


app = Flask(__name__)


cred = credentials.Certificate("key_api_todolist.json")
fire = firebase_admin.initialize_app(cred)

app.config["KEY"] = " "


db = firestore.client()
tasks_ref = db.collection("tasks")
users_ref = db.collection("users")


API_key = "#pendiente"

user_authentication = False

def login_firebas(mail, password):
    credentials = {"mail":mail,"password":password,"returnSecureToken":True}
    response = requests.post("https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={}".format(API_key),data=credentials)
    if response.status_code == 200:
       
       content = response.content
       data = response.json()
       print(data["localId"])
    
    elif response.status_code == 400:
        print(response.content)    
   
    return response.content
   
#READ

def read_tasks(ref):
   docs = ref.get() 
   all_tasks = []
   for doc in docs:
       task = doc.to_dict()
       task["id"] = doc.id
       all_tasks.append(task)
   return all_tasks

#CREATE

def create_task(ref, task):
    new_task = {"name": task,
                "check": False,
                "fecha": datetime.datetime.now()}
    ref.document().set(new_task)  

#DELETE
def delete_task(ref, id):
    respon = ref.document(id).delete()          

#UPDATE
def update_task(ref, id):
    ref.document(id).update({"check":True})




@app.route("/login", methods = ["GET", "POST"])
def login():
    global user_authentication
    if request.method == "GET":
       return render_template("login.html")
    else: 
    #POST
      mail = request.form["mail"]
      password = request.form["password"]
      print(f"{mail}:{password}")
      try:
         if mail == "gbsoloezano73@gmail.com" and password == "gbsn123":
            print("Acceso permitodo")
            user_authentication = True
            return redirect("/")
         else:
            print("Acceso denegado")
            flash("intente nuevamente")
      except:
            print("ERROR")
            flash("intente nuevamente")
            return redirect ("/")  



@app.route("/", methods = ["GET", "POST"])
def home():
   if request.method == "GET":
      if user_authentication:
         try:
            tasks = read_tasks(tasks_ref)
            incompleted = []
            completed = []
            
            for task in tasks:
               print(task["check"])
               if task["check"] == True:
                  completed.append(task)
               else:
                  incompleted.append(task)
         except:
            print("ERROR")
            tasks = []

         response = {"completed":completed, 
                        "incompleted":incompleted,
                        "counter1":len(completed),
                        "counter2":len(incompleted)}
         return render_template("Interfaz/index.html", response = response)
      else:
         return redirect(url_for("login"))
   else:
      #POST
      name = request.form["name"]
      print(f"\n {name}")
      try:
         create_task(tasks_ref, name)
         return redirect("/")
      except:
         return render_template("Interfaz/Error.html", response = "response")                                       

#UPDATE
@app.route("/update/<string:id>", methods = ["GET"])
def update(id):
   print(f"\n Actualizar Task: {id}")
   try:
      update_task(tasks_ref, id)
      print("Actualizacion completada")
      return redirect("/")
   except:
      return render_template("Interfaz/Error.html", response = "response")   


if __name__ == "__main__":
    app.run(debug=True)