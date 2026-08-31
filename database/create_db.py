import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Conecta ao banco padrão 'postgres' para criar o novo banco
try:
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="SUA_SENHA_AQUI", # Substitua pela sua senha
        host="localhost",
        port="5432"
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    cursor.execute("CREATE DATABASE torres_motors_db;")
    print("✓ Banco 'torres_motors_db' criado com sucesso!")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Erro ao criar banco (pode ser que já exista): {e}")