#Universidade Federal do Pará
#Aluno: Douglas Almeida Vidal
#Matrícula: 202300470005

import socket
import os

# Função que lida com comandos
def handle_command(client_socket, valid_users):
    dir_arq = 'pta-server/files'  
    seq_num = 0  

    while True:
        try:
            data = client_socket.recv(1024).decode()
            parts = data.split()

            if len(parts) < 2:
                client_socket.send(f"{seq_num} NOK".encode())
                break

            seq_num = int(parts[0])
            command = parts[1]

            # Autenticação de usuário
            if command == "CUMP":
                user = parts[2]
                if user in valid_users:
                    client_socket.send(f"{seq_num} OK".encode())
                else:
                    client_socket.send(f"{seq_num} NOK".encode())
                    print("Conexão encerrada, acesso de usuário não autorizado")
                    client_socket.close()
                    break

            # Listagem de arquivos
            elif command == "LIST":
                try:
                    files = os.listdir(dir_arq)
                    if len(files) == 0:
                        client_socket.send(f"{seq_num} NOK".encode())
                    else:
                        file_list = ','.join(files)
                        client_socket.send(f"{seq_num} ARQS {len(files)} {file_list}".encode())
                except Exception as e:
                    print(f"Erro enquanto listava os arquivos: {e}")
                    client_socket.send(f"{seq_num} NOK".encode())

            # Pegando arquivo
            elif command == "PEGA":
               filename = parts[2]
               file_path = os.path.join(dir_arq, filename)
               if os.path.exists(file_path):
                 try:
                    with open(file_path, 'rb') as f:  # Abre o arquivo em modo binário
                      file_content = f.read()
                    file_size = len(file_content)
                    client_socket.send(f"{seq_num} ARQ {file_size} ".encode())
                    client_socket.send(file_content)  # Envia o conteúdo binário
                 except Exception as e:
                    print(f"Erro ao ler o arquivo: {e}")
                    client_socket.send(f"{seq_num} NOK".encode())
               else:
                 client_socket.send(f"{seq_num} NOK".encode())

            # Terminando a conexão
            elif command == "TERM":
                client_socket.send(f"{seq_num} OK".encode())
                print("Conexão encerrada com comando TERM")
                client_socket.close()
                break

            # Comando inválido
            else:
                client_socket.send(f"{seq_num} NOK".encode())

        except Exception as e:
            print(f"Erro durante a comunicação do cliente: {e}")
            client_socket.send(f"{seq_num} NOK".encode())
            print("Conexão encerrada devido a erro")
            client_socket.close()
            break

# Função principal do servidor
def start_server():
    host = '0.0.0.0'
    port = 11550
    user = 'pta-server/users.txt'

    try:
        with open(user, 'r') as f:
            valid_users = [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        print("Arquivo de usuário não encontrado, desconectando")
        return

    # Iniciando o servidor
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Servidor iniciado escutando {host}:{port}")

    # Aceitando conexões de clientes
    while True:
        client_socket, addr = server_socket.accept()
        print(f"Conexão aceita de {addr}")
        handle_command(client_socket, valid_users)

if __name__ == "__main__":
    start_server()
