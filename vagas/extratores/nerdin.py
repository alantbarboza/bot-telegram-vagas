from logging import info, warning
from vagas.filtros import MAX_PAGINAS
from utils.playwright import texto, atributo, elemento
from datetime import datetime

def extrair_nerdin(page, termos_busca):
    info("Extraindo vagas do Nerdin.")
    vagas = []
 
    for termo in termos_busca:
        for pagina in range(1, MAX_PAGINAS + 1):
            try:
                url = f"https://www.nerdin.com.br/vagas.php?busca={termo.replace(' ', '+')}&pagina={pagina}&filtro_home_office=1"

                page.goto(url, timeout=45000,  wait_until="domcontentloaded")
                page.wait_for_selector(".vaga-card", timeout=15000)

                cards = elemento(page, ".vaga-card", todos=True)
                total_cards = cards.count()

                if total_cards == 0:
                    info(f"Nerdin | TERMO='{termo}' |  PAGINA={pagina} |  SEM RESULTADOS")
                    break

                info(f"Nerdin | TERMO='{termo}' | PAGINA={pagina} | VAGAS={total_cards} | URL={page.url}")

                vagas_capturadas = 0

                for i in range(total_cards):
                    try:
                        v = cards.nth(i)

                        if v.count() == 0:
                            continue
                        
                        titulo = texto(elemento(v, ".vaga-titulo"))

                        if titulo:
                            titulo = " ".join(titulo.replace("Nova", "").split())

                        link = atributo(elemento(v, ".btn-ver-vaga"), "href")

                        if link and not link.startswith("http"):
                            link = "https://www.nerdin.com.br/" + link

                        empresa = texto(elemento(v, ".vaga-empresa"))

                        local = texto(elemento(v, ".vaga-local-linha"))

                        data = None
                        data_iso = atributo(elemento(v, "time"), "datetime")

                        if data_iso:
                            data = datetime.fromisoformat(data_iso)

                        hashtags = []

                        resumo = texto(elemento(v, ".vaga-resumo-linha"))

                        if resumo:
                            partes = [p.strip() for p in resumo.split("•")]

                            for parte in partes:
                                if parte:
                                    hashtags.append(parte)

                        hashtags_el = elemento(v, ".hashtag", todos=True)

                        for j in range(hashtags_el.count()):
                            valor = texto(hashtags_el.nth(j))

                            if valor:
                                hashtags.append(valor.replace("#", "").strip())

                        hashtags = " ".join(dict.fromkeys(hashtags))

                        vagas.append({
                            "title": titulo,
                            "extra": " hashtags: " + hashtags,
                            "company": empresa,
                            "location": local,
                            "link": link,
                            "source": "Nerdin",
                            "posted_date": data.strftime("%Y-%m-%d") if data else None,
                        })

                        vagas_capturadas += 1
                    except Exception as e:
                        warning(f"Erro ao processar vaga Nerdin | TERMO='{termo}' | PAGINA={pagina} | URL={page.url} | ERRO={e}")
                        continue

                info(f"Nerdin | TERMO='{termo}' | PAGINA={pagina} | CAPTURADAS={vagas_capturadas}/{total_cards}")

            except Exception as e:
                warning(f"Erro ao acessar Nerdin | TERMO='{termo}' | PAGINA={pagina} | URL={page.url} | ERRO={e}")
                continue

    return vagas
