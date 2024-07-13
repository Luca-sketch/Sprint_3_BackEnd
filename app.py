# A Api refere-se a um backend de um sistema ecommerce usada para manutenção de usuarios e gerenciamento de compras
#
# Importação das bibliotecas
from flask import request, redirect, jsonify, session as flask_session,send_file
from flask_openapi3 import OpenAPI, Info, Tag, SecurityScheme
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from flask_session import Session
import os
from models.usuario import Usuario  
from models.carrinho import Carrinho
from schemas.error import ErrorSchema
from schemas.cadastro import CadastroSchema, LoginSchema
from schemas.carrinho import CarrinhoSchema
from schemas.cadastro import CompraIdForm
from schemas.security import api_key_auth
from schemas.cadastro import AtualizarCEPSchema
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.graphics import barcode
from dotenv import load_dotenv

# Importação das funções de segurança (Middleware.py)
from middleware import login_required, require_api_key

# Carrega as variaveis de ambiente
dotenv_path = os.path.join(os.path.dirname(__file__), 'config.env')
load_dotenv(dotenv_path)

# Configuração do swagger
info = Info(title="API - Modern Click Store", version="1.0.0")
security_schemes = {"apiKeyAuth": SecurityScheme(type="apiKey", name="x-api-key", in_="header")}
app = OpenAPI(__name__, info=info, security_schemes= api_key_auth)

# Configuração do CORS para que um domínio diferente possa acessar a aplicação
CORS(app, supports_credentials=True)

# Configuração da sessão
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'mysecret')
Session(app)

# Criação das tags para o Swagger
cadastro_tag = Tag(name="Usuario", description="Operações relacionadas ao cadastro de um usuário")
carrinho_tag = Tag(name="Carrinho", description="Operações relacionadas à compra de um produto")

# Configurações do banco de dados
MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_DB = os.getenv('MYSQL_DB')
MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))

# Conexão com o banco de dados MySQL
engine = create_engine(f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}")
Session = sessionmaker(bind=engine)
session = Session()

"""
╔═══════════════════════════════════════════════════════════════════════════════════════════════════════════════╗                                                            
║                                                                                                               ║  
 ■  As cinco rotas abaixo são relativas a tabela (Usuario) 👤                                                  ║
║   Envolve as operações de cadastrar, login,  logout, atualizar cep, deletar um usuário,                                     ║                                                                    
║                                                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════════════════════════════════════╝  
"""

# Rota para cadastrar um novo usuário ao sistema
@app.post('/cadastro', tags=[cadastro_tag],
          responses={"200": CadastroSchema, "409": ErrorSchema, "400": ErrorSchema})
def add_cadastro(form: CadastroSchema):
    """Adiciona um novo usuário à base de dados. Não pode ser inserido um usuário com o mesmo email mais de uma vez"""
    try:
        # Verifica se o usuário já existe
        if session.query(Usuario).filter_by(Email=form.Email).first():
            error_msg = "Email já cadastrado. Digite um email diferente."
            return {"message": error_msg}, 409

        # Obtém a senha do usuário e gera um código de criptografia
        hashed_password = generate_password_hash(form.Senha)

        # Adiciona o novo usuário
        usuario = Usuario(Email=form.Email, Senha=hashed_password, CEP=form.CEP)
        session.add(usuario)
        session.commit()
        return {"id": usuario.id, "Email": usuario.Email, "Senha": "******", "CEP": usuario.CEP}, 200
    except Exception as e:
        session.rollback()
        error_msg = "Não foi possível salvar novo usuário :/"
        return {"message": error_msg}, 400

# Rota para realizar o login no sistema
@app.post('/login', tags=[cadastro_tag],
          responses={"200": LoginSchema, "409": ErrorSchema, "400": ErrorSchema})
def login_usuario(form: LoginSchema):
    """Verifica o login e retorna um JSON e o status indicando o sucesso ou falha da operação"""
    try:
        # Busca pelo usuário
        usuario = session.query(Usuario).filter_by(Email=form.Email).first()
        # Caso não encontre a senha
        if not check_password_hash(usuario.Senha, form.Senha):
            return {"message": "Senha incorreta. Tente novamente."}, 401
        # Atribui ao flask_session o usuario id      
        flask_session['user_id'] = usuario.id
        return jsonify({"id": usuario.id, "Email": usuario.Email, "CEP": usuario.CEP}), 200
    except Exception as e:
        session.rollback()
        return {"message": "Erro durante o login :/"}, 400
    finally:
        session.close()
        
# Rota para realizar o logout no sistema
@app.get('/logout', tags=[cadastro_tag],
          responses={"200": {"description": "Logout realizado com sucesso."}})
def logout_usuario():
    """Realiza o logout do usuário"""
    # Remove a chave user id
    flask_session.pop('user_id', None)
    return {"message": "Logout realizado com sucesso."}, 200

# Rota para deletar um usuário (Rota protegida deve estar logado e usar a chave de api)
@app.delete('/deletar_usuario', tags=[cadastro_tag],
          responses={"200": {"description": "Usuário deletado com sucesso."}, "404": ErrorSchema},
          security=[{"apiKeyAuth": []}])
@login_required
@require_api_key
def deletar_usuario():
    """Deleta o usuário logado"""
    try:
        # Procura o usuário
        usuario = session.query(Usuario).get(flask_session['user_id'])
        if not usuario:
            return {"message": "Usuário não encontrado."}, 404
        # Delete o usuário
        session.delete(usuario)
        session.commit()
        flask_session.pop('user_id', None)
        return {"message": "Usuário deletado com sucesso."}, 200
    except Exception as e:
        session.rollback()
        return {"message": "Erro ao deletar usuário :/"}, 400  

# Rota para atualizar o CEP (Rota protegida deve estar logado e usar a chave de api)
@app.put('/atualizar_cep', tags=[cadastro_tag],
          responses={"200": {"description": "CEP atualizado com sucesso."}, "404": ErrorSchema, "400": ErrorSchema},
          security=[{"apiKeyAuth": []}])
@login_required
@require_api_key
def atualizar_cep(form: AtualizarCEPSchema):
    """Atualiza o CEP do usuário logado"""
    try:
        # Procura o usuário logado
        usuario = session.query(Usuario).get(flask_session['user_id'])
        if not usuario:
            return {"message": "Usuário não encontrado."}, 404

        # Atualiza o CEP do usuário
        usuario.CEP = form.CEP
        session.commit()

        return {"message": "CEP atualizado com sucesso."}, 200
    except Exception as e:
        session.rollback()
        error_msg = "Não foi possível atualizar o CEP."
        return {"message": error_msg}, 400

# Rota de verificação se o usuario está logado, muito utilizado no front-end para limitar o acesso a algumas páginas
@app.get('/check_login', tags=[cadastro_tag],
          responses={"200": {"description": "Usuário está logado."}, "401": {"description": "Usuário não está logado."}})
def check_login_status():
    """Verifica se o usuário está logado"""
    if 'user_id' in flask_session:
        return {"message": "Usuário está logado."}, 200
    else:
        return {"message": "Usuário não está logado."}, 401
    
"""
╔═══════════════════════════════════════════════════════════════════════════════════════════════════════════════╗                                                            
║                                                                                                               ║  
 ■    As quatro rotas abaixo são relativos a tabela (Carrinho)  🛒                                              ║             
║     As operação são adicionar um novo item, ver as compras, deletar uma compra, e gerar um pdf (boleto)        ║                                                                                                 ║                    
║                                                                                                               ║ 
╚═══════════════════════════════════════════════════════════════════════════════════════════════════════════════╝  
"""

# Rota para adicionar um novo item no carrinho (Rota protegida deve estar logado e usar a chave de api)    
@app.post('/carrinho', tags=[carrinho_tag],
          responses={"200": CarrinhoSchema, "400": ErrorSchema},
          security=[{"apiKeyAuth": []}])
@login_required
@require_api_key
def add_carrinho(form: CarrinhoSchema):
    """Adiciona um novo item ao carrinho"""
    try:
        # Procura pelo usuário
        usuario = session.query(Usuario).get(flask_session['user_id'])
        if not usuario:
            return {"message": "Usuário não encontrado."}, 404
        
        # Atribui ao token o email concatenado com a senha do usuário logado
        token = f"{usuario.Email}{usuario.Senha}"
        item_carrinho = Carrinho(Produto=form.Produto, Valor=form.Valor, Onda=form.Onda, Token=token)
        # Adiciona um novo item
        session.add(item_carrinho)
        session.commit()
        return {"id": item_carrinho.id, "Produto": item_carrinho.Produto, "Valor": item_carrinho.Valor, "Onda": item_carrinho.Onda, "Token": item_carrinho.Token}, 200
    except Exception as e:
        error_msg = "Não foi possível adicionar o item ao carrinho :/"
        return {"message": error_msg}, 400
    
# Rota para ver as compras do usuario logado (Rota protegida deve estar logado e usar a chave de api)
@app.get('/ver_compras', tags=[carrinho_tag],
          responses={"200": CarrinhoSchema, "400": ErrorSchema},
          security=[{"apiKeyAuth": []}])
@login_required
@require_api_key
def ver_compras():
    """Retorna todas as compras do usuário logado"""
    try:
        # busca pelo usuário
        usuario = session.query(Usuario).get(flask_session['user_id'])
        if not usuario:
            return {"message": "Usuário não encontrado."}, 404
        # cria o token de email concatenado com a senha
        token = f"{usuario.Email}{usuario.Senha}"
        # busca a compra pelo token
        compras = session.query(Carrinho).filter_by(Token=token).all()
        # Traz todas as compras do usuário logado
        lista_compras = [
            {
                'id': compra.id,
                'Produto': compra.Produto,
                'Valor': compra.Valor,
                'Onda': compra.Onda,
                'Token': compra.Token
            }
            for compra in compras
        ]
        return jsonify(lista_compras), 200
    except Exception as e:
        return {"message": "Erro ao buscar compras :/"}, 400

# Rota para deletar uma compra com base no id da compra (Rota protegida deve estar logado e usar a chave de api)
@app.delete('/deletar_compra', tags=[carrinho_tag],
          responses={"200": {"description": "Compra deletada com sucesso."}, "404": ErrorSchema, "400": ErrorSchema},
          security=[{"apiKeyAuth": []}])
@login_required
@require_api_key
def deletar_compra_por_id(form: CompraIdForm):
    """Deleta uma compra baseada no ID"""
    try:
        compra_id = form.compra_id
        # Obtem o usuario
        usuario = session.query(Usuario).get(flask_session['user_id'])
        if not usuario:
            return {"message": "Usuário não encontrado."}, 404
        # Gera o token
        token = f"{usuario.Email}{usuario.Senha}"
        # Busca conforme o token
        compra = session.query(Carrinho).filter_by(id=compra_id, Token=token).first()
        if not compra:
            return {"message": "Compra não encontrada."}, 404
        # Deleta a compra
        session.delete(compra)
        session.commit()
        return {"message": "Compra deletada com sucesso."}, 200
    except Exception as e:
        session.rollback()
        return {"message": "Erro ao deletar compra :/"}, 400

# Rota para gerar um pdf da compra realizada (Rota protegida deve estar logado e usar a chave de api)
@app.post('/gerar_pdf', tags=[carrinho_tag],
          responses={"200": {"description": "PDF gerado com sucesso."}, "404": ErrorSchema, "400": ErrorSchema},
          security=[{"apiKeyAuth": []}])
@login_required
@require_api_key
def gerar_pdf(form: CompraIdForm):
    """Gera um PDF com os detalhes da compra baseada no ID"""
    try:
        compra_id = form.compra_id
        # Busca o usuário
        usuario = session.query(Usuario).get(flask_session['user_id'])
        if not usuario:
            return {"message": "Usuário não encontrado."}, 404
        # Gera o token
        token = f"{usuario.Email}{usuario.Senha}"
        compra = session.query(Carrinho).filter_by(id=compra_id, Token=token).first()
        if not compra:
            return {"message": "Compra não encontrada."}, 404
        # Caminho do pdf
        pdf_path = os.path.join(os.path.expanduser("~"), "Downloads", f"compra_{compra_id}.pdf")

        # Criar o PDF usando reportlab
        c = canvas.Canvas(pdf_path, pagesize=letter)
        c.setFont("Helvetica", 12)
        
        # Adicionar detalhes da compra
        c.drawString(100, 750, "Detalhes da Compra")
        c.drawString(100, 730, f"Produto: {compra.Produto}")
        c.drawString(100, 710, f"Valor: {compra.Valor}")
        c.drawString(100, 690, f"Onda: {compra.Onda}")
        
        # Gerar código de barras
        barcode_code = f"COMPRA{compra_id}"  
        barcode_value = barcode.createBarcodeDrawing('Code128', value=barcode_code, format='png')
        barcode_value.drawOn(c, 100, 650)  
        
        c.save()
        
        # Enviar o arquivo como resposta para download
        return send_file(pdf_path, as_attachment=True)
    except Exception as e:
        return {"message": f"Erro ao gerar PDF :/ {str(e)}"}, 400

# Redireciona a rota raiz / para o swagger
@app.route('/')
def redirect_to_swagger():
    return redirect('/openapi')

# Inicia o servidor
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
