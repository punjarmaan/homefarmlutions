from flask import Flask, render_template, request
from model import main

app = Flask(__name__)


@app.route('/')
@app.route('/index')
def index():
  return render_template('index.html')


@app.route("/templates/cropoptions.html")
def crops():
  return render_template('cropoptions.html')


@app.route('/mothcalc', methods=["POST"])
def mothcalc():
  user_address = request.form["user_address"]
  print(user_address)
  user_choice = request.form["user_choice"]

  returned_dict = main(user_address, user_choice)

  return render_template("results.html",
                         returned_day=returned_dict['plant_days'], returned_value=returned_dict['success_rate'])


app.run(host='0.0.0.0', port=81)
