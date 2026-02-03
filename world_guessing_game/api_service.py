import random
import requests


class ServicoAPI:
    URL = "https://restcountries.com/v3.1/all?fields=name,capital,population"

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self._cache_paises = None

    def _baixar_lista_paises(self):
        headers = {"User-Agent": "WorldGuessingGame/1.0"}

        resp = requests.get(self.URL, timeout=self.timeout, headers=headers)
        resp.raise_for_status()
        dados = resp.json()

        paises_validos = []
        for item in dados:
            nome = (item.get("name") or {}).get("common")
            capitais = item.get("capital")
            populacao = item.get("population")

            if nome and capitais and isinstance(capitais, list) and populacao:
                paises_validos.append({
                    "nome": nome,
                    "capital": capitais[0],
                    "populacao": populacao
                })

        if not paises_validos:
            raise RuntimeError("Nenhum país válido encontrado.")

        return paises_validos

    def obter_pais_aleatorio(self):
        if self._cache_paises is None:
            self._cache_paises = self._baixar_lista_paises()

        return random.choice(self._cache_paises)
