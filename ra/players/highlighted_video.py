import glob
import os
import os.path
import ssl
import time
import urllib.request as urllib2
import requests
from bs4 import BeautifulSoup
from django.core.files import File
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import glob
import os.path
import urllib.request as urllib2
from django.core.files import File
def get_highlighted_video(player,url):
    try:
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--incognito")
            chrome_options.add_argument("disk-cache-size=0")
            chrome_options.add_argument("--disable-browser-cache-memory")
            chrome_options.add_argument("--disable-browser-cache-disk")
            chrome_options.add_argument("--disable-browser-cache-offline")
            chrome_options.add_argument("--disable-browser-cache-disk-enable")
            chrome_options.add_argument("--disable-cache-offline-enable")
            chrome_options.add_argument("--disable-network-http-use-cache")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--no-sandbox")
            driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            print("{}".format(e))
        max_retries = ''
        video_link = ''
        try:
            driver.get(url)
        except Exception as H:
            if H.args[0][0] == 'H':
                max_retries = 'Exception'
                pass
        if max_retries == '':        
            try:
                WebDriverWait(driver,4).until(EC.presence_of_element_located((By.XPATH, '/html/head/meta[19]')))
                print("Page is ready!")
            except TimeoutException:
                print("Loading took too much time!")
                driver.delete_all_cookies()
                
            html = driver.page_source
            driver.delete_all_cookies()
            soup = BeautifulSoup(html, 'html.parser')
            try:
                video_link = soup.find('meta',{'property':'og:video:secure_url'}).get('content').split('?')[0]
                print('----------------',video_link,'----------------------')
                player.video_highlight = video_link  
            except Exception as e:
                print(e,"video link exception")

            driver.quit()
            if video_link != '':
                video_url = video_link
                try:
                    ssl._create_default_https_context = ssl._create_unverified_context
                    result = urllib2.urlretrieve(video_url)
                    player.web_highlighted_video.save(
                    os.path.basename(player.first_name + player.last_name + '-highlighted-video.mp4'),
                    File(open(result[0], 'rb'))
                    )
                    player.save()
                except Exception as e:
                    print(e, "video url error")

                files = glob.glob('/tmp/tmp*')
                remove_tmp = [os.remove(file) for file in files]

        else:
            driver.quit()
    except Exception as e:
        print(e)    
