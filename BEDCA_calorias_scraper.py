from playwright.sync_api import Playwright, sync_playwright, expect
from bs4 import BeautifulSoup
import re
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
    cabecera = ["Componente","Valor","Unidad","Fuente"]
    
    for letra in alfabeto:
        page.get_by_role("link", name=letra, exact=True).click()
        
        # Extraemos los nombres de las comidas de la tabla
        file_path = "CSVs_Nombres/comidas_"+letra+".csv"
        comidas_df = pd.read_csv(filepath_or_buffer=file_path)
        comidas = comidas_df["Nombre"]
        
        # Por cada comida nos quedamos con los datos de las tablas HTML
        for comida in comidas:
            page.get_by_role("link", name=comida, exact=True).first.click()
            
            # Una vez dentro de la comida sacamos los datos que queremos            
            html = page.inner_html('#content')
            soup = BeautifulSoup(html, 'html.parser')
            
            td_list = []
            for td in soup.select("td"):
                td_list.append(td.string)
            
            while "Proximales" not in td_list:
                page.wait_for_timeout(200)
                html = page.inner_html('#content')
                soup = BeautifulSoup(html, 'html.parser')
            
                td_list = []
                for td in soup.select("td"):
                    td_list.append(td.string)
                
            proximales_position = td_list.index("Proximales")
            zinc_position = td_list.index('zinc (cinc)')
            td_list = td_list[proximales_position:zinc_position + 4]
            
            # Creamos una matriz (como la tabla que acabamos de scrapear)
            # con dimensiones indeterminadas en las filas (-1) y 3 columnas
            matrix = np.array(td_list).reshape(-1,4)
            # Creamos el nombre del csv y guardamos la tabla
            file_name = re.sub(r'[^A-Za-z0-9]+', ' ', comida)
            file_path = "CSVs_ValoresNutricionales/" + file_name + ".csv"
            pd.DataFrame(matrix,columns=cabecera).to_csv(file_path,
                                                            index=False)
            
            # Volvemos a la página anterior para que haga click en la siguiente comida
            page.get_by_role("link", name="Listado anterior").click()
            
    # ---------------------
    context.close()
    browser.close()
    
    
with sync_playwright() as playwright:
    run(playwright)
