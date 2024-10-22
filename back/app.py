from pymongo import MongoClient
from bson.objectid import ObjectId

# Conexão com o MongoDB
client = MongoClient("mongodb+srv://leticia23205:controlegastos123@controlegastos.fpwju.mongodb.net/")
db = client['controle_gastos']
usuarios = db['usuarios']

# Função para cadastrar um novo usuário
def cadastrar_usuario():
    nome = input("Digite o nome: ")
    email = input("Digite o email: ")
    senha = input("Digite a senha: ")

    if usuarios.find_one({"email": email}):
        print("Email já cadastrado.")
    else:
        usuario_id = usuarios.insert_one({
            "nome": nome,
            "email": email,
            "senha": senha
        }).inserted_id
        print(f"Usuário cadastrado com sucesso! ID: {usuario_id}")

# Função para login
def login_usuario():
    email = input("Digite o email: ")
    senha = input("Digite a senha: ")

    usuario = usuarios.find_one({"email": email})
    if usuario and usuario["senha"] == senha:
        print("Login realizado com sucesso!")
        return usuario["_id"]
    else:
        print("Credenciais inválidas.")
        return None

# Função para exibir detalhes da conta
def detalhes_usuario(usuario_id):
    usuario = usuarios.find_one({"_id": ObjectId(usuario_id)})
    if usuario:
        print(f"Nome: {usuario['nome']}")
        print(f"Email: {usuario['email']}")
    else:
        print("Usuário não encontrado.")

# Função para editar dados do usuário
def editar_usuario(usuario_id):
    novo_nome = input("Digite o novo nome (ou pressione Enter para manter): ")
    novo_email = input("Digite o novo email (ou pressione Enter para manter): ")
    nova_senha = input("Digite a nova senha (ou pressione Enter para manter): ")

    update_data = {}
    if novo_nome:
        update_data['nome'] = novo_nome
    if novo_email:
        update_data['email'] = novo_email
    if nova_senha:
        update_data['senha'] = nova_senha

    if update_data:
        usuarios.update_one({"_id": ObjectId(usuario_id)}, {"$set": update_data})
        print("Dados atualizados com sucesso!")
    else:
        print("Nenhuma alteração feita.")

# Menu principal
def menu():
    while True:
        print("\n--- MENU ---")
        print("1. Cadastrar Usuário")
        print("2. Login")
        print("3. Sair da aplicação")

        escolha = input("Escolha uma opção: ")

        if escolha == "1":
            cadastrar_usuario()
        elif escolha == "2":
            usuario_id = login_usuario()
            if usuario_id:
                while True:
                    print("\n1. Exibir Detalhes da Conta")
                    print("2. Editar Dados")
                    print("3. Logout")
                    sub_escolha = input("Escolha uma opção: ")

                    if sub_escolha == "1":
                        detalhes_usuario(usuario_id)
                    elif sub_escolha == "2":
                        editar_usuario(usuario_id)
                    elif sub_escolha == "3":
                        print("Logout realizado.")
                        break
        elif escolha == "3":
            print("Saindo...")
            break
        else:
            print("Opção inválida.")

if __name__ == "__main__":
    menu()
