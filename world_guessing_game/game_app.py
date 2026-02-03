import math
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

from api_service import ServicoAPI
from database import BancoDados


class JogoApp(tk.Tk):
    def __init__(self, api: ServicoAPI, db: BancoDados):
        super().__init__()
        self.api = api
        self.db = db

        self.title("World Guessing Game - Ranking Edition")
        self.geometry("720x420")
        self.resizable(False, False)

        self.pais_atual = None
        self.inicio_rodada = None

        self._criar_widgets()
        self._atualizar_treeview()
        self.nova_rodada()

    def _criar_widgets(self):
        frame_top = ttk.Frame(self, padding=12)
        frame_top.pack(fill="x")

        ttk.Label(frame_top, text="Dica (Capital):", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, sticky="w")
        self.lbl_dica = ttk.Label(frame_top, text="...", font=("Segoe UI", 12))
        self.lbl_dica.grid(row=0, column=1, sticky="w", padx=(8, 0))

        ttk.Label(frame_top, text="Seu nome:", font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", pady=(12, 0))
        self.ent_nome = ttk.Entry(frame_top, width=30)
        self.ent_nome.grid(row=1, column=1, sticky="w", padx=(8, 0), pady=(12, 0))

        ttk.Label(frame_top, text="Seu palpite:", font=("Segoe UI", 10)).grid(row=2, column=0, sticky="w", pady=(8, 0))
        self.ent_palpite = ttk.Entry(frame_top, width=30)
        self.ent_palpite.grid(row=2, column=1, sticky="w", padx=(8, 0), pady=(8, 0))
        self.ent_palpite.bind("<Return>", lambda _e: self.processar_palpite())

        self.btn_chutar = ttk.Button(frame_top, text="Chutar", command=self.processar_palpite)
        self.btn_chutar.grid(row=2, column=2, padx=10, pady=(8, 0))

        self.btn_nova = ttk.Button(frame_top, text="Nova rodada", command=self.nova_rodada)
        self.btn_nova.grid(row=0, column=2, padx=10)

        self.btn_sair = ttk.Button(frame_top, text="Sair", command=self.destroy)
        self.btn_sair.grid(row=1, column=2, padx=10, pady=(12, 0))

        frame_status = ttk.Frame(self, padding=(12, 0))
        frame_status.pack(fill="x")

        self.lbl_status = ttk.Label(frame_status, text="Boa sorte!", foreground="#333")
        self.lbl_status.pack(anchor="w", pady=8)

        frame_bottom = ttk.Frame(self, padding=12)
        frame_bottom.pack(fill="both", expand=True)

        ttk.Label(frame_bottom, text="Top 5 Ranking", font=("Segoe UI", 11, "bold")).pack(anchor="w")

        colunas = ("jogador", "pontuacao", "data_hora")
        self.tree = ttk.Treeview(frame_bottom, columns=colunas, show="headings", height=10)

        self.tree.heading("jogador", text="Jogador")
        self.tree.heading("pontuacao", text="Pontuação")
        self.tree.heading("data_hora", text="Data/Hora")

        self.tree.column("jogador", width=220)
        self.tree.column("pontuacao", width=120, anchor="center")
        self.tree.column("data_hora", width=200, anchor="center")

        self.tree.pack(fill="both", expand=True, pady=(8, 0))

    def nova_rodada(self):
        try:
            self.pais_atual = self.api.obter_pais_aleatorio()
            self.lbl_dica.config(text=self.pais_atual["capital"])
            self.inicio_rodada = datetime.now()

            self.ent_palpite.delete(0, tk.END)
            self.ent_palpite.focus()

            self.lbl_status.config(text="Rodada iniciada! Digite o país e clique em Chutar.")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao iniciar rodada:\n{e}")
            self.lbl_status.config(text="Erro ao carregar país. Tente novamente.")

    def _normalizar(self, texto: str) -> str:
        return (texto or "").strip().lower()

    def _calcular_pontuacao(self, segundos: float, populacao: int) -> int:
        segundos = max(segundos, 0.2)

        base = 1000 / segundos

        dificuldade = 1 / math.log10(populacao)
        multiplicador = 1 + (dificuldade * 2.5) 

        pontos = math.floor(base * multiplicador)
        return max(pontos, 0)

    def processar_palpite(self):
        if not self.pais_atual or not self.inicio_rodada:
            self.lbl_status.config(text="Clique em Nova rodada para começar.")
            return

        jogador = self.ent_nome.get().strip()
        if not jogador:
            messagebox.showwarning("Atenção", "Digite seu nome antes de chutar.")
            self.ent_nome.focus()
            return

        palpite = self.ent_palpite.get()
        if not palpite.strip():
            messagebox.showwarning("Atenção", "Digite um palpite.")
            self.ent_palpite.focus()
            return

        fim = datetime.now()
        tempo_gasto = (fim - self.inicio_rodada).total_seconds()

        resposta = self.pais_atual["nome"]
        if self._normalizar(palpite) == self._normalizar(resposta):
            pontos = self._calcular_pontuacao(tempo_gasto, self.pais_atual["populacao"])
            self.db.salvar_recorde(jogador, pontos)
            self._atualizar_treeview()

            messagebox.showinfo(
                "Acertou!",
                f"✅ País: {resposta}\n⏱ Tempo: {tempo_gasto:.2f}s\n⭐ Pontos: {pontos}"
            )

            self.lbl_status.config(text="Acertou! Nova rodada carregada.")
            self.nova_rodada()
        else:
            self.lbl_status.config(text=f"❌ Errou! Dica: capital = {self.pais_atual['capital']}. Tente novamente.")
            self.ent_palpite.select_range(0, tk.END)
            self.ent_palpite.focus()

    def _atualizar_treeview(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for jogador, pontuacao, data_hora in self.db.top_5():
            self.tree.insert("", tk.END, values=(jogador, pontuacao, data_hora))
