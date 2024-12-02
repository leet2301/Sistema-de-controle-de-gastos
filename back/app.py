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
receitas = db["receitas"]
despesas = db["despesas"]

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
    
from bson.objectid import ObjectId  # Certifique-se de importar ObjectId

# Função para deletar uma conta
@app.route('/usuarios/deletar/<usuario_id>', methods=['DELETE'])
def deletar_conta(usuario_id):
    try:
        # Converta o usuario_id para ObjectId
        usuario_object_id = ObjectId(usuario_id)

        # Deletar receitas associadas ao usuário
        receitas.delete_many({"usuario_id": usuario_object_id})

        # Deletar despesas associadas ao usuário
        despesas.delete_many({"usuario_id": usuario_object_id})

        # Deletar o usuário
        resultado = usuarios.delete_one({"_id": usuario_object_id})

        if resultado.deleted_count > 0:
            return jsonify({"msg": "Conta e todas as informações associadas foram deletadas com sucesso!"}), 200
        else:
            return jsonify({"msg": "Usuário não encontrado."}), 404
    except Exception as e:
        return jsonify({"msg": f"Erro ao deletar conta: {str(e)}"}), 500

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
        "valor": float(valor),
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
        "valor": float(valor),
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

from bson import ObjectId  # Para converter o id corretamente

# Função para buscar todas as despesas de um usuário
@app.route('/despesas/<usuario_id>', methods=['GET'])
def buscar_despesas(usuario_id):
    despesas = db.despesas.find({"usuario_id": ObjectId(usuario_id)})
    lista_despesas = []
    for despesa in despesas:
        lista_despesas.append({
            "valor": despesa["valor"],
            "categoria": despesa["categoria"],
            "descricao": despesa["descricao"],
            "data": despesa["data"]
        })
    print(lista_despesas)  # Verificar o que está sendo retornado
    return jsonify(lista_despesas), 200

# Função para buscar todas as entradas de um usuário
@app.route('/receitas/<usuario_id>', methods=['GET'])
def buscar_entradas(usuario_id):
    entradas = db.receitas.find({"usuario_id": ObjectId(usuario_id)})
    lista_entradas = []
    for entrada in entradas:
        lista_entradas.append({
            "valor": entrada["valor"],
            "categoria": entrada["categoria"],
            "descricao": entrada["descricao"],
            "data": entrada["data"]
        })
    print(lista_entradas)  # Verificar o que está sendo retornado
    return jsonify(lista_entradas), 200

from flask import request

# Editar uma despesa

@app.route("/despesas/editar/<id>", methods=["PUT"])
def editar_despesa(id):

    try:
        # Obtendo os dados que foram passados para editar
        dados = request.get_json()
        
        # Atualizando a despesa no banco de dados
        despesa = db.despesas.find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set": dados},
         #   return_document=ReturnDocument.AFTER
        )
        
        if despesa:
            return jsonify({"msg": "Despesa editada com sucesso!", "despesa": despesa}), 200
        else:
            return jsonify({"msg": "Despesa não encontrada!"}), 404
    except Exception as e:
        return jsonify({"msg": f"Erro ao editar despesa: {str(e)}"}), 500


# Excluir uma despesa
@app.route("/despesas/excluir/<id>", methods=["DELETE"])
def excluir_despesa(id):
    try:
        # Deletando a despesa do banco de dados
        resultado = db.despesas.delete_one({"_id": ObjectId(id)})
        
        if resultado.deleted_count > 0:
            return jsonify({"msg": "Despesa excluída com sucesso!"}), 200
        else:
            return jsonify({"msg": "Despesa não encontrada!"}), 404
    except Exception as e:
        return jsonify({"msg": f"Erro ao excluir despesa: {str(e)}"}), 500


# Editar uma receita
@app.route("/receitas/editar/<id>", methods=["PUT"])
def editar_receita(id):
    try:
        dados = request.get_json()
        
        # Atualizando a receita no banco de dados
        receita = db.receitas.find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set": dados},
          #  return_document=ReturnDocument.AFTER
        )
        
        if receita:
            return jsonify({"msg": "Receita editada com sucesso!", "receita": receita}), 200
        else:
            return jsonify({"msg": "Receita não encontrada!"}), 404
    except Exception as e:
        return jsonify({"msg": f"Erro ao editar receita: {str(e)}"}), 500


# Excluir uma receita
@app.route("/receitas/excluir/<id>", methods=["DELETE"])
def excluir_receita(id):
    try:
        # Deletando a receita do banco de dados
        resultado = db.receitas.delete_one({"_id": ObjectId(id)})
        
        if resultado.deleted_count > 0:
            return jsonify({"msg": "Receita excluída com sucesso!"}), 200
        else:
            return jsonify({"msg": "Receita não encontrada!"}), 404
    except Exception as e:
        return jsonify({"msg": f"Erro ao excluir receita: {str(e)}"}), 500
    
@app.route('/usuarios/saldo/<usuario_id>', methods=['GET'])
def saldo_usuario(usuario_id):
    try:
        # Somando as receitas
        receitas_total = list(db.receitas.aggregate([
            {"$match": {"usuario_id": ObjectId(usuario_id)}},  # Filtro para o usuário correto
            {"$group": {"_id": None, "total": {"$sum": "$valor"}}}  # Somando os valores das receitas
        ]))

        # Somando as despesas
        despesas_total = list(db.despesas.aggregate([
            {"$match": {"usuario_id": ObjectId(usuario_id)}},  # Filtro para o usuário correto
            {"$group": {"_id": None, "total": {"$sum": "$valor"}}}  # Somando os valores das despesas
        ]))

        # Verificando se as agregações retornaram resultados
        receitas = receitas_total[0]["total"] if receitas_total else 0
        despesas = despesas_total[0]["total"] if despesas_total else 0

        saldo = receitas - despesas  # Calculando o saldo

        return jsonify({"saldo": saldo}), 200

    except Exception as e:
        print(f"Erro ao calcular saldo: {e}")
        return jsonify({"error": "Erro ao calcular saldo"}), 500


@app.route('/usuarios/alerta/<usuario_id>', methods=['GET'])
def alerta_usuario(usuario_id):
    receitas_total = db.receitas.aggregate([
        {"$match": {"usuario_id": ObjectId(usuario_id)}},
        {"$group": {"_id": None, "total": {"$sum": "$valor"}}}
    ])
    despesas_total = db.despesas.aggregate([
        {"$match": {"usuario_id": ObjectId(usuario_id)}},
        {"$group": {"_id": None, "total": {"$sum": "$valor"}}}
    ])

    receitas = next(receitas_total, {"total": 0})["total"]
    despesas = next(despesas_total, {"total": 0})["total"]
    saldo = receitas - despesas

    if saldo <= 0:
        return jsonify({"alerta": "Saldo negativo! Controle seus gastos."}), 200
    elif saldo < 100:  # Alterar para o valor desejado
        return jsonify({"alerta": "Atenção! Seu saldo está baixo."}), 200

    return jsonify({"alerta": None}), 200


@app.route('/dicas', methods=['GET'])
def dicas_financeiras():
    dicas = db.dicas_financeiras.find()
    lista_dicas = [{"dica": dica["dica"]} for dica in dicas]
    return jsonify(lista_dicas), 200

@app.route('/metas/criar', methods=['POST'])
def criar_meta():
    dados = request.json
    usuario_id = dados.get("usuario_id")
    meta = dados.get("meta")
    valor = dados.get("valor")
    prazo = dados.get("prazo")

    nova_meta = {
        "usuario_id": ObjectId(usuario_id),
        "meta": meta,
        "valor": valor,
        "prazo": prazo,
        "progresso": 0.0
    }

    db.metas_financeiras.insert_one(nova_meta)
    return jsonify({"msg": "Meta criada com sucesso!"}), 201

@app.route('/metas_financeiras/<usuario_id>', methods=['GET'])
def listar_metas(usuario_id):
    try:
        metas = list(db.metas_financeiras.find({"usuario_id": ObjectId(usuario_id)}))
        metas_lista = []

        for meta in metas:
            metas_lista.append({
                "meta": meta["meta"],
                "valor": meta["valor"],
                "progresso": meta.get("progresso", 0.0),  # Progresso (opcional)
                "prazo": meta.get("prazo", "Sem prazo definido")  # Prazo (opcional)
            })

        return jsonify(metas_lista), 200
    except Exception as e:
        print(f"Erro ao listar metas: {e}")
        return jsonify({"error": "Erro ao listar metas"}), 500



# Rodar o servidor
if __name__ == '__main__':
    app.run(debug=True)