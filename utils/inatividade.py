from threading import Thread
from time import sleep
from logging import info, warning
import requests

def evitar_inatividade(url):

    while True:

        try:
            requests.get(url, timeout=20)

            info("Verificação de inatividade executada.")

        except Exception as e:
            warning(f"Erro na verificação de inatividade: {e}")

        sleep(300)

def iniciar_monitoramento_inatividade(url):
    
    Thread(
        target=evitar_inatividade,
        args=(url,),
        daemon=True
    ).start()