from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup

class Bot:
    
    def __init__(self):
        # WebDriver setup to avoid detection
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--incognito")
        self.bot = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.bot.get("https://it.pracuj.pl/")
        self.bot.maximize_window()
        self.currentSite = 1
        
    def ClickButtonAcc(self):
        # Wait until the "Akceptuj" button is present
        WebDriverWait(self.bot, 100).until(
            EC.presence_of_element_located((By.CLASS_NAME, "size-medium.variant-primary.cookies_b1fqykql"))
        )
        # Find and click the "Akceptuj" button
        button = self.bot.find_element(By.CLASS_NAME, "size-medium.variant-primary.cookies_b1fqykql")
        button.click() 
          
    def GetSiteReady(self):
        # Wait for the content box and paginator to be present
        WebDriverWait(self.bot, 1000).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[class^='ContentBoxstyles__Wrapper-']"))
        )
        WebDriverWait(self.bot, 1000).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[class^='Paginatorstyles__Wrapper-sc-1ur9l1s-0 dDposH']"))
        )
    #Pobiera ile jest stron z ofertami
    def GetAllSitesNums(self):
        WebDriverWait(self.bot, 100).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[class^='Paginatorstyles__Wrapper-sc-1ur9l1s-0 dDposH']"))
        )
        # Find the <ul> element with class "pagination"
        ul_element = self.bot.find_element(By.CSS_SELECTOR, "[class^='Paginatorstyles__Wrapper-sc-1ur9l1s-0 dDposH']")
        # Find all the <li> elements within the <ul> element
        li_elements = ul_element.find_elements(By.TAG_NAME, 'li')
        last_item = li_elements[-2]
        # Find the <a> element within the second-to-last <li> element
        link_element = last_item.find_element(By.TAG_NAME, 'a')
        # Get the inner HTML content of the <a> element
        numer_stron_sesji = link_element.get_attribute("innerHTML")
        # Print the inner HTML content
        #print("Ilosc stron: " + numer_stron_sesji)
        return numer_stron_sesji
            
    # Pobierz divy z ofertami
    def GetOffersFromCurrentSite(self):
        oferty = self.bot.find_elements(By.CSS_SELECTOR, 'div[class^="ContentBoxstyles__Wrapper-"]')
        for oferta in oferty:
            inner_html = oferta.get_attribute("innerHTML")
            soup = BeautifulSoup(inner_html, 'html.parser')

            # Find the desired element by tag, class, or other attributes
            tytul_element = soup.find('h3', attrs={'data-test': 'offer-title'})
            company_name_element = soup.find('span', attrs={'data-test': 'company-name'})
            offer_location_element = soup.find('span', attrs={'data-test': 'offer-location'})
            offer_management_level_element = soup.find('span', attrs={'data-test': 'offer-management-level'})
            date = soup.find('div', class_='JobOfferstyles__FooterText-sc-1rq6ue2-22')

            # Get the text of the element, checking if it exists
            tytul = tytul_element.text if tytul_element else ''
            company = company_name_element.text if company_name_element else ''
            location = offer_location_element.text if offer_location_element else ''
            management_level = offer_management_level_element.text if offer_management_level_element else ''
            Pdate = date.text if date else ''
            Pdate = Pdate.replace("opublikowana: ", "")

            # Print the details only if the title is not empty
            if tytul:
                print("Tytuł oferty: " + tytul)
                print("Firma:" + company)
                print("Lokalizacja: " + location)
                print("Doświadczenie: " + management_level)
                print("Data opublikowania: " + Pdate)
                print("\n")
    
    def GoToNextSite(self):
        self.currentSite+=1
        self.bot.get("https://it.pracuj.pl/?pn=" + str(self.currentSite))
        self.GetSiteReady()
        
bot = Bot()
bot.GetSiteReady()
bot.ClickButtonAcc()
numer_stron_sesji = bot.GetAllSitesNums()

while int(bot.currentSite) < int(numer_stron_sesji):
    bot.GetOffersFromCurrentSite()
    bot.GoToNextSite()

input(" ")