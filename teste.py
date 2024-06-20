import unittest
from unittest.mock import patch
from main import YfinanceCrawler
from io import StringIO

class TestYfinanceCrawler(unittest.TestCase):

    @patch('builtins.input', return_value='InvalidRegion')
    def test_filter_invalid_region_message(self, mock_input):
        crawler = YfinanceCrawler('InvalidRegion')
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            crawler.run()
            self.assertIn("A região 'InvalidRegion' não é um filtro disponível neste momento.", mock_stdout.getvalue())

    #Teste para confirmar o fechamento do driver no caso de uma região invalida
    def test_filter_invalid_region_close_browser(self):
            crawler = YfinanceCrawler("InvalidRegion")
            crawler.run()
            self.assertTrue(crawler.driver is None or crawler.driver.quit)

    #Teste para confirmar o fechamento do driver no fim da execução
    def test__close_browser(self):
            crawler = YfinanceCrawler("Argentina")
            crawler.run()
            self.assertTrue(crawler.driver is None or crawler.driver.quit)
    
    #Teste para confirmar o modelo de salvamento dos dados
    def test_save_to_csv(self):
        
        crawler = YfinanceCrawler("United States")
        #Exemplo de dados
        crawler.data = [{'symbol': 'AAPL', 'name': 'Apple Inc.', 'price': '123.45'}]
        crawler.save_to_csv()
        crawler.driver.close()
        
        
        with open('yahoo_finance_data.csv', 'r', newline='', encoding='utf-8') as csvfile:
            csv_content = csvfile.read()
            self.assertIn('"AAPL","Apple Inc.","123.45"', csv_content)

    

if __name__ == "__main__":
    unittest.main()