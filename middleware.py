#Esta seção é destinada a proteção das rotas e chamadas da api
#
#Importações das bilbiotecas
from flask import request, redirect, jsonify, session as flask_session
from functools import wraps
import os
import threading

#Criação da variavel API_KEY que obtém o valor do config.env (Utilizado nas requisões)
API_KEY = os.getenv('API_KEY', 'mysecretapikey')

# Contador de tentativas de login simultâneas
login_attempts = {}
lock = threading.Lock()

# Criação do decorator para proteger as rotas da api, caso o usuário não esteja autenticado é redirecionado para o login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        #Verifica se o ID está dentro da flask session
        if 'user_id' not in flask_session:
            #Caso não esteja redireciona para o login
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

# Criação do decorator para proteger os requests da api, sendo que a chave deve ser enviada no header
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('x-api-key')
        if api_key and api_key == API_KEY:
            return f(*args, **kwargs)
        else:
            return jsonify({"message": "API Key is missing or wrong"}), 403
    return decorated_function

