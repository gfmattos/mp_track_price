from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, ElementClickInterceptedException
from bs4 import BeautifulSoup
import pandas as pd
from datetime import date
import time
import re

drugstores = {
    'DRA':'https://www.drogaraia.com.br/search?w=sallve',
    'DSL':'https://www.drogasil.com.br/search?w=sallve',
    'DSP':'https://www.drogariasaopaulo.com.br/sallve',
    'DPA':'https://www.drogariaspacheco.com.br/sallve',
    'DVN':'https://www.drogariavenancio.com.br/sallve',
    'ECM':'https://www.epocacosmeticos.com.br/sallve#1'
            }

def initialize_browser(drugstore, headless=True, logless=True):

    service = Service(ChromeDriverManager().install())
    options = Options()
    options.add_argument('--start-maximized')

    if logless:
        options.add_argument('--log-level=3')

    if headless:
        options.add_argument('--headless')
        options.add_argument('--window-size=1920,1200')

    browser = webdriver.Chrome(service=service, options=options)
    browser.implicitly_wait(10)

    browser.get(drugstores[drugstore])

    return browser


def get_menuInfo(browser, drugstore):

    if drugstore == 'DRA' or drugstore == 'DSL':

        products_panel = browser.find_element(By.CLASS_NAME, 'iyYAwe')
        products = products_panel.find_elements(By.CLASS_NAME, 'LinkNext')
        
        try: 
            if browser.find_element(By.XPATH, '//*[@id="__next"]/main/div/div[2]/div/div/div/div[3]/div/ul/li[3]/a'):
                pagination = 1
            else:
                pagination = 0
        except NoSuchElementException:
            pagination = 0

        menu_info = None

        last_page = 0

        return menu_info, products, pagination, last_page

    elif drugstore == 'DSP' or drugstore == 'DPA':
        
        time.sleep(5)

        WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.ID, 'onetrust-accept-btn-handler'))).click()

        try:
            while browser.find_element(By.CLASS_NAME, 'progress-bar-prateleira'):
                load_products = browser.find_element(By.CLASS_NAME, 'btn-primary')
                browser.execute_script('arguments[0].click()', load_products)
                time.sleep(5)
        except:
            pass
        
        products = browser.find_elements(By.CLASS_NAME, 'collection-link')

        menu_info = None
        pagination = None
        last_page = None

        return menu_info, products, pagination, last_page

    elif drugstore == 'DVN':
        
        try:
            WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.XPATH, '/html/body/footer/div[6]/div/button'))).click()
        except:
            pass

        products = None

        try:
            while browser.find_element(By.CLASS_NAME, 'sr_loadMore'):
                load_products = browser.find_element(By.CLASS_NAME, 'sr_loadMore')
                browser.execute_script('arguments[0].click()', load_products)
                time.sleep(5)
        except:
            pass
        
        time.sleep(10)

        menu_info = BeautifulSoup(browser.page_source, 'html.parser')

        pagination = None
        last_page = None

        return menu_info, products, pagination, last_page

    elif drugstore == 'ECM':
        
        try:
            WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.CLASS_NAME, 'cookie_agree'))).click()
        except:
            pass
        
        products_panel = browser.find_element(By.CLASS_NAME, 'n4colunas')
        products = products_panel.find_elements(By.CLASS_NAME, 'shelf-default__item')
        
        time.sleep(10)
        menu_info = BeautifulSoup(browser.page_source, 'html.parser')

        pagination = 1 if menu_info.find_all('li', attrs={'class':'page-number'})[1].text == '2' else 0
        
        last_page = 0

        return menu_info, products, pagination, last_page


def exec_webscraping(browser, drugstore, attempts, menu_info, products, pagination, last_page):

    names_list = []
    prices_list = []
    eans_list = []

    if drugstore == 'DRA':

        pag = 1

        while last_page == 0:
            
            try:
                last_page = 1 if browser.find_element(By.XPATH, '//*[@id="__next"]/main/div/div[2]/div/div/div/div[3]/div/ul/li[3]/a') == None else 0

            except NoSuchElementException:
                last_page = 1

            index = 0

            for i in range(0, attempts):

                try:

                    print(f'Attempt: {i+1} - {drugstore}')

                    for product in range(index, len(products), 2):
                    
                        index = product

                        if drugstores['DRA'] not in browser.current_url:
                            browser.get(f'https://www.drogaraia.com.br/search?w=sallve&p={pag}')
                            time.sleep(2)
                            browser.refresh()

                        products_panel = browser.find_element(By.CLASS_NAME, 'iyYAwe')
                        products = products_panel.find_elements(By.CLASS_NAME, 'LinkNext')
                        products[product].click()

                        time.sleep(10)
                        product_page = BeautifulSoup(browser.page_source, 'html.parser')

                        name = product_page.find('h1', attrs={'data-qa':'my-account-title'}).text
                        ean = product_page.find_all('div', attrs={'data-testid':'htmlParse'})[1].text

                        if product_page.find('button', attrs={'data-qa':'PDP_btn_tell_me'}):
                            price = 'Esgotado'
                        else:
                            price = product_page.find('span', attrs={'class':'ProductPricestyles__Price-sc-1fizsje-2'}).text[3:]

                        browser.back()

                        names_list.append(name)
                        prices_list.append(price)
                        eans_list.append(ean)

                        str_error = None                        

                except Exception as e:
                    str_error = str(e)

                if str_error:
                    time.sleep(2)

                else:
                    break
                
            if pagination == 1:
                browser.find_element(By.LINK_TEXT, 'próximo').click()

                pag += 1

                products_panel = browser.find_element(By.CLASS_NAME, 'iyYAwe')
                products = products_panel.find_elements(By.CLASS_NAME, 'LinkNext')

            else:
                break
            
        browser.quit()

        return names_list, prices_list, eans_list
    
    elif drugstore == 'DSL':

        pag = 1

        while last_page == 0:
        
            try:
                last_page = 1 if browser.find_element(By.XPATH, '//*[@id="__next"]/main/div/div[2]/div/div/div/div[3]/div/ul/li[3]/a') == None else 0

            except NoSuchElementException:
                last_page = 1

            index = 0

            for i in range(0, attempts):

                try:

                    print(f'Attempt: {i+1} - {drugstore}')

                    for product in range(index, len(products), 2):
                    
                        index = product

                        if drugstores['DSL'] not in browser.current_url:
                            browser.get(f'https://www.drogaraia.com.br/search?w=sallve&p={pag}')
                            time.sleep(2)
                            browser.refresh()

                        products_panel = browser.find_element(By.CLASS_NAME, 'iyYAwe')
                        products = products_panel.find_elements(By.CLASS_NAME, 'LinkNext')
                        products[product].click()

                        time.sleep(10)
                        product_page = BeautifulSoup(browser.page_source, 'html.parser')

                        name = product_page.find('h1', attrs={'data-qa':'seo-product_name-h1validator'}).text
                        ean = product_page.find_all('div', attrs={'class':'ConverterHtmlstyles__ConverterHtmlStyles-sc-186sryh-0 gjcTgl'})[3].text

                        if product_page.find('button', attrs={'data-qa':'PDP_button_check_availability'}):
                            price = 'Esgotado'
                        else:
                            price = product_page.find('div', attrs={'class':'Pricestyles__ProductPriceStyles-sc-118x8ec-0 fzwZWj price'}).text[2:]

                        browser.back()

                        names_list.append(name)
                        prices_list.append(price)
                        eans_list.append(ean)

                        str_error = None                        

                except Exception as e:
                    str_error = str(e)

                if str_error:
                    time.sleep(2)

                else:
                    break
                
            if pagination == 1:
                browser.find_element(By.LINK_TEXT, 'próximo').click()

                pag += 1

                products_panel = browser.find_element(By.CLASS_NAME, 'iyYAwe')
                products = products_panel.find_elements(By.CLASS_NAME, 'LinkNext')

            else:
                break
            
        browser.quit()

        return names_list, prices_list, eans_list

    elif drugstore == 'DSP' or drugstore == 'DPA':

        index = 0

        for i in range(0, attempts):
                
            try:
                
                print(f'Attempt: {i+1} - {drugstore}')
        
                for product in range(index, len(products)):
                
                    index = product
        
                    if drugstores['DSP'] not in browser.current_url and drugstore == 'DSP':
                        time.sleep(2)
                        browser.get(drugstores['DSP'])
                        browser.refresh()

                        try:
                            while browser.find_element(By.CLASS_NAME, 'progress-bar-prateleira'):
                                load_products = browser.find_element(By.CLASS_NAME, 'btn-primary')
                                browser.execute_script('arguments[0].click()', load_products)
                                time.sleep(5)
                        except:
                            pass

                    if drugstores['DPA'] not in browser.current_url and drugstore == 'DPA':
                        time.sleep(2)
                        browser.get(drugstores['DPA'])
                        browser.refresh()
        
                        try:
                            while browser.find_element(By.CLASS_NAME, 'progress-bar-prateleira'):
                                load_products = browser.find_element(By.CLASS_NAME, 'btn-primary')
                                browser.execute_script('arguments[0].click()', load_products)
                                time.sleep(5)
                        except:
                            pass
                    
                    products = browser.find_elements(By.CLASS_NAME, 'collection-link')
        
                    products[product].click()
        
                    time.sleep(10)
                    product_page = BeautifulSoup(browser.page_source, 'html.parser')
                    
                    name = product_page.find('div', attrs={'class':'productName'}).text
                    
                    for number_script in range(50,70):
                    
                        try:
                            ean_script = browser.find_element(By.XPATH, f'/html/head/script[{number_script}]').get_attribute('innerHTML')
                            ean = re.search('"productEans":\["(?:[^"]|"")*"\]', ean_script).group(0)[16:-2]
                        except:
                            pass
                        
                    notify_panel = product_page.find('div', attrs={'class':'notifyme-title-div','style':'display: none;'})
                    
                    if notify_panel:
                        price = product_page.find('strong', attrs={'class':'skuBestPrice'}).text[3:]
                    else:
                        price = 'Esgotado'
        
                    names_list.append(name)
                    prices_list.append(price)
                    eans_list.append(ean)
        
                    str_error = None  
        
            except Exception as e:
                str_error = str(e)
        
            if str_error:
                time.sleep(2)
                    
            else:
                break
            
        browser.quit()

        return names_list, prices_list, eans_list

    elif drugstore == 'DVN':
        
        print(f'Attempt: {i+1} - {drugstore}')

        try:
            while browser.find_element(By.CLASS_NAME, 'sr_loadMore'):
                load_products = browser.find_element(By.CLASS_NAME, 'sr_loadMore')
                browser.execute_script('arguments[0].click()', load_products)
                time.sleep(5)
        except:
            pass
        
        products_panel = menu_info.find_all('figcaption', attrs={'class':'shelf-product__info'})

        for product in range(0, len(products_panel)):
        
            name = products_panel[product].find('h4', attrs={'class':'shelf-product__title'}).text

            p = products_panel[product].find('strong', attrs={'class':'shelf-product__price-best'})

            if p:        
                p = p.get_text()[3:]
                i = p.find(',')+3
                price = p[:i]
            else:
                price = 'Esgotado'

            names_list.append(name)
            prices_list.append(price)

        eans_panel = menu_info.find_all('div', attrs={'class':'product-field product_field_169 product-field-type_1'})
        eans_list = [x.find('li').text for x in eans_panel]

        browser.quit()

        #pagination = 0

        return names_list, prices_list, eans_list
    
    elif drugstore == 'ECM':

        pag = 1

        while last_page == 0:
        
            last_page = 0 if menu_info.find('li', attrs={'class':'next pgEmpty'}) == None else 1

            index = 0

            for i in range(0, attempts):

                try:

                    print(f'Attempt: {i+1} - {drugstore}')

                    for product in range(index, len(products)):
                    
                        index = product

                        if drugstores['ECM'] not in browser.current_url:
                            browser.get(f'https://www.epocacosmeticos.com.br/sallve#{pag}')
                            time.sleep(2)
                            browser.refresh()

                        products_panel = browser.find_element(By.CLASS_NAME, 'n4colunas')
                        products = products_panel.find_elements(By.CLASS_NAME, 'shelf-default__item')

                        products[product].click()

                        time.sleep(10)
                        product_page = BeautifulSoup(browser.page_source, 'html.parser')

                        name = product_page.find('div', attrs={'class':'productName'}).text
                        ean = product_page.find('label', attrs={'class':'sku-ean-code'}).text

                        price_panel = product_page.find('strong', attrs={'class':'skuBestPrice'})
                        if price_panel:
                            price = price_panel.text[3:]
                        else:
                            price = 'Esgotado'

                        browser.back()

                        names_list.append(name)
                        prices_list.append(price)
                        eans_list.append(ean)

                        str_error = None                    

                except Exception as e:
                    str_error = str(e)

                if str_error:
                    time.sleep(2)

                else:
                    break
                
            if pagination == 1:
                browser.find_elements(By.CLASS_NAME, 'next')[1].click()
                pag += 1

                time.sleep(10)
                menu_info = BeautifulSoup(browser.page_source, 'html.parser')

            else:
                break
            
        browser.quit()

        return names_list, prices_list, eans_list


def store_data(drugstore, names, prices, eans, df=pd.DataFrame({})):

    products_dict = {}

    products_dict['drugstore'] = [drugstore for x in range(0, len(names))]
    products_dict['products_name'] = names
    products_dict['price'] = prices
    products_dict['EAN'] = eans

    df_ws = pd.DataFrame(data=products_dict)

    if not df.empty:
        df_ws = pd.concat([df,df_ws],ignore_index=True)

    return df_ws


def track_price(drugstores, headless=True, logless=True, attempts=100):

    for i,drugstore in enumerate(drugstores):

        browser = initialize_browser(drugstore, headless, logless)
        print(f'Initialized browser for {drugstore}...')

        menu_info, products, pagination, last_page = get_menuInfo(browser, drugstore)
        print(f'Menu information gathered successfully for {drugstore}, starting webscraping...')

        names, prices, eans = exec_webscraping(browser, drugstore, attempts, menu_info, products, pagination, last_page)
        print(f'Data have been collected successfully for {drugstore}, storing data...')

        if i == 0:
            df = store_data(drugstore, names, prices, eans)
            print(f'Data have been stored successfully for {drugstore}')

        else:
            df = store_data(drugstore, names, prices, eans, df)
            print(f'Data have been stored successfully for {drugstore}, concatenating with previous data...')
        
    
    df.to_csv(f'tracked_prices_{date.today()}.csv', index=False, encoding='utf-8-sig') 
    print('The data has been exported successfully in a csv file!')