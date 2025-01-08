from flask import Flask, request, jsonify
from database import db
from models.user import User
from flask_login import LoginManager, login_user, current_user, logout_user, login_required

app = Flask(__name__)
login_manager = LoginManager()

app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
  return User.query.get(user_id)

@app.route('/login', methods=["POST"])
def login():
  data = request.get_json()
  username = data.get("username")
  password = data.get("password")
  
  if username and password:
    user = User.query.filter_by(username=username).first()
    if user and user.password == password:
      login_user(user)
      print(current_user.is_authenticated)
      return jsonify({"message":  "Autenticação realizada com sucesso"})

  return jsonify({"message": "Credenciais inválidas"}), 400

@app.route('/logout', methods=['GET'])
@login_required
def logout():
  logout_user()
  return jsonify({"message": "Logout realizado com sucesso"})
  
@app.route("/", methods=['GET'])
def hello_word():
  return "Hello World"

if __name__ == "__main__":
  app.run(debug=True)