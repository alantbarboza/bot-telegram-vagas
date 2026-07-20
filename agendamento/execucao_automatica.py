from asyncio import sleep, create_task
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from logging import info
from vagas.envio import enviar_vagas
from vagas.filtros import carregar_usuarios, obter_proxima_execucao, salvar_proxima_execucao
import bot.comandos as comandos

TZ = ZoneInfo("America/Sao_Paulo")

proximas_execucoes = {}

async def agendar_usuario(chat_id):

    global proximas_execucoes

    while True:

        agora = datetime.now(TZ)

        data_salva = obter_proxima_execucao(chat_id)

        if data_salva:
            proxima_execucao = datetime.fromisoformat(data_salva)

            if proxima_execucao <= agora:

                proxima_execucao = agora.replace(
                    hour=proxima_execucao.hour,
                    minute=proxima_execucao.minute,
                    second=0,
                    microsecond=0
                )

                if proxima_execucao <= agora:
                    proxima_execucao += timedelta(days=1)

                salvar_proxima_execucao(chat_id, proxima_execucao)

        else:
            info(f"{chat_id} não possui próxima execução cadastrada.")
            return

        proximas_execucoes[str(chat_id)] = proxima_execucao

        segundos = max((proxima_execucao - agora).total_seconds(), 0)

        info(f"Próxima execução de {chat_id}: {proxima_execucao}")

        await sleep(segundos)

        chave = (0, "/vagas")

        busca_em_andamento = False

        for _, comando in comandos.comandos_em_andamento:

            if comando == "/vagas":
                busca_em_andamento = True
                break

        if busca_em_andamento:
            info(f"Execução automática de {chat_id} ignorada porque já existe uma busca em andamento.")
            continue

        try:

            info(f"Iniciando execução automática para {chat_id}.")

            comandos.comandos_em_andamento.add(chave)

            await enviar_vagas(chat_id)

            info(f"Execução automática para {chat_id} finalizada.")

            proxima_execucao += timedelta(days=2)

            proximas_execucoes[str(chat_id)] = proxima_execucao

            salvar_proxima_execucao(chat_id, proxima_execucao)

        finally:
            comandos.comandos_em_andamento.discard(chave)

async def iniciar_agendador():

    usuarios = carregar_usuarios()

    for chat_id in usuarios:
        create_task(agendar_usuario(int(chat_id)))

    info("Agendador iniciado.")

    while True:
        await sleep(3600)