import selenium
import bs4
import time
import csv
import sys

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

from bs4 import BeautifulSoup

class YfinanceCrawler:

    #Iniciando a classe
    def __init__(self,region):
        self.region = region
        self.url = "https://finance.yahoo.com/screener/new"
        self.driver = webdriver.Firefox()
        self.data = []

    #Interacao com o filtro de regioes
    def filter(self):
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR,'[style="margin-bottom: 8px; padding-top: 12px; margin-left: auto; margin-right: auto; text-align: center; line-height: 0px; position: relative; z-index: 5; min-height: 250px;"]')))

        #Abre o menu de regioes
        filter_area = self.driver.find_element(By.CSS_SELECTOR,"[data-test='label-filter-list']")
        region_button = filter_area.find_element(By.CSS_SELECTOR, "[data-icon='new']")
        region_button.click()
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.ID,"dropdown-menu")))
        menu = self.driver.find_element(By.ID,"dropdown-menu")
        
        #Retira a regiao padrao
        checkbox = menu.find_element(By.XPATH, f"//span[contains(text(), 'United States')]/../input[@type='checkbox']")
        checkbox.click()

        #Seleciona a regiao desejada
        try:
            checkbox = menu.find_element(By.XPATH, f"//span[contains(text(), '{self.region}')]/../input[@type='checkbox']")
            checkbox.click()
        #Caso a regiao desejada nao seja um dos filtros diponiveis    
        except NoSuchElementException:
            print(f"A região '{self.region}' não é um filtro disponível neste momento.")
            return False
            

        #Fecha o menu de regioes
        close_button = menu.find_element(By.CLASS_NAME, "close")
        close_button.click()

        #Aplica o filtro
        find_button = self.driver.find_element(By.CSS_SELECTOR, "[data-test='find-stock']")
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(find_button))
        find_button.click()

        return True

    #Executa
    def run(self):
        self.driver.get(self.url)
        correct = self.filter()
        if correct:
            self.extraction()
            self.save_to_csv()
        self.driver.close()
        
        
        
    #Extracao
    def extraction(self):

        more_data = True

        #Repete enquanto houver mais dados disponiveis
        while more_data:
                  
            #Espera a página estar carregada
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//span/span[contains(text(), 'Next')]/ancestor::button")))
            results = self.driver.find_element(By.ID, "screener-results")
            soup = BeautifulSoup(results.get_attribute("innerHTML"), 'html.parser')
            table = soup.find('tbody')

            #Cria dicionario com os dados da tabela
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if cols:
                    stock_data = {
                        'symbol': cols[0].text,
                        'name': cols[1].text,
                        'price': cols[2].text,
                    }
                    self.data.append(stock_data)

            #Define se existem mais dados
            next_button = self.driver.find_element(By.XPATH, "//span/span[contains(text(), 'Next')]/ancestor::button")
            if next_button.is_enabled():
                self.driver.execute_script("arguments[0].click();", next_button)
                time.sleep(1)
            
            else:
                more_data = False
        
            
    #Salva os dados em arquivo csv    
    def save_to_csv(self):
        with open('yahoo_finance_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, quoting=csv.QUOTE_NONNUMERIC)

            for item in self.data:
                writer.writerow(item.values())          

            
        
if __name__ == "__main__":
    region = input("Digite a região para filtrar: ")
    crawler = YfinanceCrawler(region)
    crawler.run()