from  logging import info

DEBUG = False

def criar_navegador(playwright):

    browser = playwright.chromium.launch(
        headless=not DEBUG,
        slow_mo=150 if DEBUG else 0,
        args=[
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu"
        ]
    )

    context = browser.new_context(
        viewport=None,
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/150.0.0.0 Safari/537.36"
        ),
        locale="pt-BR",
        timezone_id="America/Sao_Paulo"
    )

    return browser, context


def criar_pagina(context):

    page = context.new_page()

    page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        })
    """)

    page.set_extra_http_headers({
        "Accept-Language": "pt-BR,pt;q=0.9"
    })

    page.set_default_timeout(15000)
    page.set_default_navigation_timeout(45000)

    if DEBUG:
        page.pause()

    page.mouse.move(500, 300)

    return page