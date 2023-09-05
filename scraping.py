from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time, base64
import os, zipfile



def scraping(cliente, user='hsoto@cigepty.com', password='hsm280466'):
    os.chdir(os.path.join(os.path.expanduser("~"), "Downloads"))
    for file in os.listdir():
        if 'partner-export' in file:
            os.remove(file)
            
    link = 'https://partner-emporiaenergy-com.auth.us-east-2.amazoncognito.com/login?client_id=2eh64j5kmdcecnc2vqhtl8naj8&response_type=code&scope=email+openid&redirect_uri=https://partner.emporiaenergy.com/logincb'
    print('Loading scraping...')
    options = Options()
    driver = webdriver.Chrome(options=options); driver.get(link)
    wait = WebDriverWait(driver, 5)
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="signInFormUsername"]'))).send_keys(user)
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="signInFormPassword"]'))).send_keys(password)
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@name="signInSubmitButton"]'))).click()
    driver.maximize_window(); time.sleep(5)
    cliente_element = wait.until(EC.element_to_be_clickable((By.XPATH, f'//*[text()="{cliente}"]')))
    driver.execute_script("arguments[0].scrollIntoView(true);", cliente_element)
    cliente_element.click(); time.sleep(7)
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[text()="Export Data"]'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[text()="Hourly Data"]'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[text()="All"]'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[text()="Start"]'))).click()
    time.sleep(7.5); driver.quit()
    print('Files downloaded !')

    for file in os.listdir():
        if 'partner-export' in file:
            with zipfile.ZipFile(file, 'r') as zip_file:
                for file_name in zip_file.namelist():
                    if file_name.endswith('.csv'):
                        with zip_file.open(file_name) as csv_file:
                            data = pd.read_csv(csv_file)
    
    return data