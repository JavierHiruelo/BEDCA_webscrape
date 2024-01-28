from playwright.sync_api import Playwright, sync_playwright, expect
from bs4 import BeautifulSoup
import time
import pandas as pd
import numpy as np
import csv

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False, slow_mo=50)
    context = browser.new_context()
    page = context.new_page()
    # Vamos a coger los datos que vienen en la Base de Datos BEDCA
    page.goto("https://www.bedca.net/bdpub/index.php")
    page.get_by_role("link", name="Consulta").click()
    page.get_by_role("link", name="Lista alfabética").click()
    
    alfabeto = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    
    for letra in alfabeto:
        page.get_by_role("link", name=letra, exact=True).click()
        html = page.inner_html('#content')
        soup = BeautifulSoup(html, 'html.parser')
        a_list = []
        # Los elementos que nos queremos quedar están en elementos 'a' 
        #TODO LOS ELEMENTOS QUE QUIERO SACAR DE LAS TABLAS ESTÁN EN ELEMENTOS TR (Table Row)
        # será algo parecido a lo que acabo de hacer
        for a in soup.select('a'):
            a_list.append(a.string)

        # Solo nos importan los elementos que van después de ID
        id_position = a_list.index('Id')
        a_list = a_list[id_position:]
        # Creamos una matriz (como la tabla que acabamos de scrapear)
        # con dimensiones indeterminadas en las filas (-1) y 3 columnas
        matrix = np.array(a_list[3:]).reshape(-1,3)
        # Creamos el nombre del csv y guardamos la tabla
        file_path = "csv/comidas_" + letra + ".csv"
        pd.DataFrame(matrix,columns=a_list[0:3]).to_csv(file_path,
                                                        index=False)

    # ---------------------
    context.close()
    browser.close()



with sync_playwright() as playwright:
    run(playwright)