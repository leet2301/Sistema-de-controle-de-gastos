from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Conexão com o MongoDB
client = MongoClient("mongodb+srv://leticia23205:controlegastos123@controlegastos.fpwju.mongodb.net/")
db = client['controle_gastos']
usuarios = db['usuarios']

# Função para cadastrar um novo usuário
@app.route('/usuarios/cadastrar', methods=['POST'])
def cadastrar_usuario():
    dados = request.json
    nome = dados.get('nome')
    email = dados.get('email')
    senha = dados.get('senha')

    if usuarios.find_one({"email": email}):
        return jsonify({"msg": "Email já cadastrado."}), 400
    else:
        usuario_id = usuarios.insert_one({
            "nome": nome,
            "email": email,
            "senha": senha
        }).inserted_id
        return jsonify({"msg": f"Usuário cadastrado com sucesso!", "id": str(usuario_id)}), 201

# Função para login
@app.route('/usuarios/login', methods=['POST'])
def login_usuario():
    dados = request.json
    email = dados.get('email')
    senha = dados.get('senha')

    usuario = usuarios.find_one({"email": email})
    if usuario and usuario["senha"] == senha:
        return jsonify({"msg": "Login realizado com sucesso!", "id": str(usuario["_id"])}), 200
    else:
        return jsonify({"msg": "Credenciais inválidas."}), 401

# Função para exibir detalhes da conta
@app.route('/usuarios/detalhes/<usuario_id>', methods=['GET'])
def detalhes_usuario(usuario_id):
    usuario = usuarios.find_one({"_id": ObjectId(usuario_id)})
    if usuario:
        return jsonify({
            "nome": usuario['nome'],
            "email": usuario['email']
        }), 200
    else:
        return jsonify({"msg": "Usuário não encontrado."}), 404

# Função para editar dados do usuário
@app.route('/usuarios/editar/<usuario_id>', methods=['PUT'])
def editar_usuario(usuario_id):
    dados = request.json
    novo_nome = dados.get('nome')
    novo_email = dados.get('email')
    nova_senha = dados.get('senha')

    update_data = {}
    if novo_nome:
        update_data['nome'] = novo_nome
    if novo_email:
        update_data['email'] = novo_email
    if nova_senha:
        update_data['senha'] = nova_senha

    if update_data:
        usuarios.update_one({"_id": ObjectId(usuario_id)}, {"$set": update_data})
        return jsonify({"msg": "Dados atualizados com sucesso!"}), 200
    else:
        return jsonify({"msg": "Nenhuma alteração feita."}), 400
    
# Função para deletar uma conta
@app.route('/usuarios/deletar/<usuario_id>', methods=['DELETE'])
def deletar_conta(usuario_id):
    resultado = usuarios.delete_one({"_id": ObjectId(usuario_id)})
    if resultado.deleted_count > 0:
        return jsonify({"msg": "Conta deletada com sucesso!"}), 200
    else:
        return jsonify({"msg": "Usuário não encontrado."}), 404

# Função para registrar despesas e transações
@app.route('/despesas/registrar', methods=['POST'])
def registrar_despesa():
    dados = request.json
    usuario_id = dados.get('usuario_id')
    valor = dados.get('valor')
    categoria = dados.get('categoria')
    descricao = dados.get('descricao')
    data = dados.get('data')

    despesa = {
        "usuario_id": ObjectId(usuario_id),
        "valor": valor,
        "categoria": categoria,
        "descricao": descricao,
        "data": data
    }

    db.despesas.insert_one(despesa)
    return jsonify({"msg": "Despesa registrada com sucesso!"}), 201


# Função para registrar entradas na conta
@app.route('/receitas/registrar', methods=['POST'])
def registrar_entrada():
    dados = request.json
    usuario_id = dados.get('usuario_id')
    valor = dados.get('valor')
    categoria = dados.get('categoria')
    descricao = dados.get('descricao')
    data = dados.get('data')

    receita = {
        "usuario_id": ObjectId(usuario_id),
        "valor": valor,
        "categoria": categoria,
        "descricao": descricao,
        "data": data
    }

    db.receitas.insert_one(receita)
    return jsonify({"msg": "Entrada registrada com sucesso!"}), 201


# Função para atualizar a categoria de uma despesa
@app.route('/despesas/atualizar_categoria/<despesa_id>', methods=['PUT'])
def atualizar_categoria_despesa(despesa_id):
    dados = request.json
    nova_categoria = dados.get('categoria')

    resultado = db.despesas.update_one(
        {"_id": ObjectId(despesa_id)},
        {"$set": {"categoria": nova_categoria}}
    )

    if resultado.modified_count > 0:
        return jsonify({"msg": "Categoria da despesa atualizada com sucesso!"}), 200
    else:
        return jsonify({"msg": "Despesa não encontrada."}), 404



# Rodar o servidor
if __name__ == '__main__':
    app.run(debug=True)
