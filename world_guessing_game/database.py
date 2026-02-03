import sqlite3
from datetime import datetime


class BancoDados:
    def __init__(self, caminho_db: str = "ranking.db"):
        self.caminho_db = caminho_db
        self._criar_tabela()

    def _conectar(self):
        return sqlite3.connect(self.caminho_db)

    def _criar_tabela(self):
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ranking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    jogador TEXT NOT NULL,
                    pontuacao INTEGER NOT NULL,
                    data_hora TEXT NOT NULL
                )
            """)
            conn.commit()

    def salvar_recorde(self, jogador: str, pontuacao: int):
        data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO ranking (jogador, pontuacao, data_hora) VALUES (?, ?, ?)",
                (jogador.strip(), int(pontuacao), data_hora)
            )
            conn.commit()

    def top_5(self):
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT jogador, pontuacao, data_hora
                FROM ranking
                ORDER BY pontuacao DESC, id ASC
                LIMIT 5
            """)
            return cursor.fetchall()
