from flask import Flask, request, jsonify
from database import db
from models.user import User
from flask_login import LoginManager, login_required, login_user, logout_user,current_user
import bcrypt

app = Flask(__name__)
login_manager = LoginManager()

app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:admin123@127.0.0.1:3306/flask-crud'

db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

def get_session():
  with app.app_context():
    return db.session

@login_manager.user_loader
def load_user(user_id):
  session = get_session()
  return session.get(User, user_id)

@app.route('/login', methods=["POST"])
def login():
  data = request.get_json()
  username = data.get("username")
  password = data.get("password")
  
  if username and password:
    session = get_session()
    user = session.query(User).filter_by(username=username).first()
    if user and bcrypt.checkpw(str.encode(password), str.encode(user.password)):
      login_user(user)
      print(current_user.is_authenticated)
      return jsonify({"message":  "Autenticação realizada com sucesso"})

  return jsonify({"message": "Credenciais inválidas"}), 400

@app.route('/logout', methods=['GET'])
@login_required
def logout():
  logout_user()
  return jsonify({"message": "Logout realizado com sucesso"})
  
@app.route("/user", methods=['POST'])
def create_user():
  data = request.get_json()
  username = data['username']
  password = data['password']
  
  if username and password:
    hashed_password = bcrypt.hashpw(str.encode(password), bcrypt.gensalt())
    user = User(username=username, password=hashed_password, role="user")
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "Usuário cadastrado com sucesso"})
    
  return jsonify({"message": "Dados inválidos"}), 400

@app.route('/user/<int:user_id>', methods=['GET'])
@login_required
def get_user(user_id):
  session = get_session()
  user = session.query(User).get(user_id)
  if user:
    return jsonify({"username": user.username})

  return jsonify({"message": "Usuário não encontrado"}), 404

@app.route('/user/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
  data = request.get_json()
  session = get_session()
  user = session.query(User).get(user_id)
  
  if user_id != current_user.id and current_user.role =='user':
    return jsonify({"message": "Operação não permitida"}), 403
  
  if user and data.get("password"):
    user.password = data.get("password")
    db.session.commit()
    return jsonify({"message": f"Usuário {user_id} atualizado com sucesso"})
  
  return jsonify({"message": "Usuário não encontrado"}), 404
    
@app.route('/user/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
  session = get_session()
  user = session.query(User).get(user_id)
  
  if current_user.role !='admin':
    return jsonify({"message": "Operação não permitida"}), 403
  
  if user_id == current_user.id:
    return jsonify({"message": "Deleção não permitida"}), 403
  if user:
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": f"Usuário {user_id} deletado com sucesso"})
  return jsonify({"message": "Usuário não encontrado"}), 404
  
if __name__ == "__main__":
  app.run(debug=True)