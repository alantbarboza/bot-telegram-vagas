from playwright.sync_api import sync_playwright
from logging import info, warning
from vagas.filtros import validar_periodo, remover_duplicadas
from utils.navegador import criar_navegador, criar_pagina
from vagas.extratores.linkedin import extrair_linkedin
from vagas.extratores.nerdin import extrair_nerdin
from vagas.extratores.solides import extrair_solides
from vagas.extratores.empregos import extrair_empregos
from vagas.extratores.infojobs import extrair_infojobs
from vagas.extratores.jobs99 import extrair_99jobs


from gc import collect
from psutil import Process
from os import getpid
process = Process(getpid())

def buscar_vagas(termos_busca):
    with sync_playwright() as p:
        vagas = []

        extratores = [
            ("LinkedIn", extrair_linkedin),
            #("Nerdin", extrair_nerdin),
            ("Solides", extrair_solides),
            ("Empregos", extrair_empregos),
            ("InfoJobs", extrair_infojobs),
            ("99Jobs", extrair_99jobs),
        ] 

        for site, extrator in extratores:
            browser = None
            context = None
            page = None

            try:
                browser, context = criar_navegador(p)
                page = criar_pagina(context)
                
                vagas += extrator(page, termos_busca)

            except Exception as e:
                warning(f"Erro fatal {site}: {e}")

            finally:
                try:
                    if page and not page.is_closed():
                        page.close()
                except:
                    pass

                try:
                    if context:
                        context.close()
                except:
                    pass

                try:
                    if browser:
                        browser.close()
                except:
                    pass

                del page
                del context
                del browser
                collect()

                info(f"{site} | Memória: {process.memory_info().rss / 1024 / 1024:.1f} MB")

    info("Busca de vagas concluída. Validando conteúdo e removendo duplicadas...")
    vagas = remover_duplicadas(vagas)
    vagas = validar_periodo(vagas)

    return vagas
