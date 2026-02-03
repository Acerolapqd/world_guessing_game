from api_service import ServicoAPI
from database import BancoDados
from game_app import JogoApp


def main():
    api = ServicoAPI(timeout=10)
    db = BancoDados("ranking.db")
    app = JogoApp(api, db)
    app.mainloop()


if __name__ == "__main__":
    main()
