from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as expected_conditions
import pandas as pd
import time
from selenium.common.exceptions import TimeoutException

# ========================================
# PARTE 1 -CONFIGURAÇÕES DO DRIVER
# ========================================

chrome_driver = r"c:\chromedriver-win64\chromedriver.exe"
service = Service(chrome_driver)

options = webdriver.ChromeOptions()
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(service=service , options=options)

url = "https://masander.github.io/AlimenticiaLTDA/#/operational"
driver.get(url)
time.sleep(5)

# ========================================
# PARTE 2 - NAVEGA PARA A PRÓXIMA PÁGINA
# ========================================

nav = driver.find_element(By.CLASS_NAME, "subpage_button")
buttons = nav.find_elements(By.TAG_NAME, "button")

botao_proximo = buttons[1]
botao_proximo.click()
time.sleep(5)

# ========================================
# PARTE 3 - CAPTURA DADOS DA TABELA
# ========================================

dic_coleta = {
    "Id_material": [], 
    "Nome": [],
    "Quantidade_uso": [],
    "Unidade": [],
    "Setor_uso": [],
    "Custo_unitario": [],
    "Fornecedor": [],
    "Filial": [],
    "Turno": []
}

produtos = driver.find_elements(By.XPATH, "//table/tbody//tr")
for produto in produtos:
    try:
        id_material = produto.find_element(By.CLASS_NAME, "td_id_material").text.strip()
        nome = produto.find_element(By.CLASS_NAME, "td_nome").text.strip()
        quantidade_uso = produto.find_element(By.CLASS_NAME, "td_quantidade_uso").text.strip()
        unidade = produto.find_element(By.CLASS_NAME, "td_unidade").text.strip()
        setor_uso = produto.find_element(By.CLASS_NAME, "td_setor_uso").text.strip()
        custo_unitario = produto.find_element(By.CLASS_NAME, "td_custo_unitario").text.strip()
        fornecedor = produto.find_element(By.CLASS_NAME, "td_fornecedor").text.strip()
        filial = produto.find_element(By.CLASS_NAME, "td_Filial").text.strip()
        turno = produto.find_element(By.CLASS_NAME, "td_turno").text.strip()

        print(f'{id_material}, {nome}, {quantidade_uso}, {unidade}, {setor_uso}, {custo_unitario}, {fornecedor}, {filial}, {turno}')

        dic_coleta["Id_material"].append(id_material)
        dic_coleta["Nome"].append(nome)
        dic_coleta["Quantidade_uso"].append(quantidade_uso)
        dic_coleta["Unidade"].append(unidade)
        dic_coleta["Setor_uso"].append(setor_uso)
        dic_coleta["Custo_unitario"].append(custo_unitario)
        dic_coleta["Fornecedor"].append(fornecedor)
        dic_coleta["Filial"].append(filial)
        dic_coleta["Turno"].append(turno)

    except Exception as e:
        print("Erro ao coletar dados:", e)

# ========================================
# PARTE 4 - EXPORTAÇÃO DOS DADOS
# ========================================

df_materiais = pd.DataFrame(dic_coleta)
df_materiais.to_excel("Materiais.xlsx", index=False)
print(f"\n✅ Arquivo 'Materiais.xlsx' salvo com sucesso! {len(df_materiais)} valores capturados.\n")

# Encerra o navegador
driver.quit()