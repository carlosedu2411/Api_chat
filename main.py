import os
from flask import Flask, render_template, request, redirect, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, and_
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = "segredo123"

# Configuração da URL do banco da Railway
DATABASE_URL = os.getenv("DATABASE_URL", "postgres-production-81533.up.railway.app")

# Correção essencial: SQLAlchemy exige "postgresql://" em vez de "postgres://"
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializa o ORM
db = SQLAlchemy(app)

# -----------------------
# MODELOS (Tabelas do Banco de Dados)
# -----------------------

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(100), nullable=False)

class Mensagem(db.Model):
    __tablename__ = 'mensagens'
    id = db.Column(db.Integer, primary_key=True)
    remetente_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    destinatario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    mensagem = db.Column(db.Text, nullable=False)

# Cria as tabelas na Railway caso elas ainda não existam
with app.app_context():
    db.create_all()


# -----------------------
# LOGIN
# -----------------------

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    nome = request.form["nome"]
    senha = request.form["senha"]

    # Busca o usuário pelo nome usando o ORM
    user = Usuario.query.filter_by(nome=nome).first()

    if user is None:
        # Se não existe, cria um novo
        user = Usuario(nome=nome, senha=senha)
        db.session.add(user)
        db.session.commit() # O ID é gerado automaticamente aqui
    else:
        if user.senha != senha:
            return "Senha incorreta"

    session["user_id"] = user.id
    session["nome"] = user.nome

    return redirect("/chat")

# -----------------------
# CHAT
# -----------------------

@app.route("/chat")
def chat():
    if "user_id" not in session:
        return redirect("/")

    return render_template(
        "chat.html",
        nome=session["nome"],
        usuario_id=session["user_id"]
    )

# -----------------------
# LISTAR USUARIOS
# -----------------------

@app.route("/usuarios")
def usuarios():
    if "user_id" not in session:
        return jsonify([])

    # Retorna todos os usuários exceto o logado
    lista_usuarios = Usuario.query.filter(Usuario.id != session["user_id"]).all()
    
    # Mantém o formato original de lista de tuplas [id, nome] que o fetchall retornava
    dados = [[u.id, u.nome] for u in lista_usuarios]
    return jsonify(dados)

# -----------------------
# ENVIAR MENSAGEM
# -----------------------

@app.route("/enviar", methods=["POST"])
def enviar():
    if "user_id" not in session:
        return jsonify({"status": "erro"})

    data = request.get_json()
    destinatario = data["destinatario"]
    texto = data["texto"]

    # Cria e salva a nova mensagem no banco
    nova_mensagem = Mensagem(
        remetente_id=session["user_id"],
        destinatario_id=destinatario,
        mensagem=texto
    )
    db.session.add(nova_mensagem)
    db.session.commit()

    return jsonify({"status": "ok"})

# ----------------
if __name__ == "__main__":
    # O Gunicorn vai ignorar essa parte, mas é bom deixar assim:
    app.run()