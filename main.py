#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Strycnine"
__copyright__ = "Copyright (C) 2022 Strycnine"
__license__ = "Public Domain"
__version__ = "1.0"

################################################################################

import warnings
warnings.filterwarnings("ignore")

import requests
from bs4 import BeautifulSoup
from selenium import webdriver

import os
import glob
import shutil
import logging
import time

import pandas as pd

################################################################################
#               CONSTANTES
################################################################################

URL = '' # lien url
CSV = 'books.csv' # nom du fichier

################################################################################
#               INITIALISATION LOG
################################################################################

logging.basicConfig(filename='Books/erreur.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y/%m/%d %H:%M:%S')

################################################################################
#               FONCTIONS
################################################################################

def scrap_df():
    names = []
    links = []
    paths = []
    i = 0
    print('Construction du fichier csv......')
    while True:
        i += 1
        lien = URL + '/book.php?id=' + str(i)
        URL_galerie = requests.get(lien)
        soup_galerie = BeautifulSoup(URL_galerie.text, "html.parser")
        name = soup_galerie.find('h1')
        link = soup_galerie.select('td a')
        if len(link) == 2 and name != None:
            print(f'Book ID = {i}')
            names.append(name.text)
            links.append(URL + link[0].get('href'))
            paths.append(link[1].text.replace('\\\\', '/').replace(':', ' -'))
        else:
            print('Terminé !')
            break
    df = pd.DataFrame({'name':names, 'link':links, 'path':paths})
    df.to_csv('Books/' + CSV)
    print('Construction du fichier csv terminé !')


def Download_book(link):
    driver.get(link)
    time.sleep(1)
    target = driver.find_element_by_css_selector('a[download=""]')
    target.click()
    time.sleep(4)

################################################################################
#               BOUCLE PRINCIPALE
################################################################################

print('\n##################################################')
print('#               Books Scraping !!!               #')
print('##################################################\n\n')

try:
    os.mkdir('Books')
except:
    pass

if CSV not in os.listdir('Books/'):
    scrap_df()
print('Chargement du fichier csv......')
df = pd.read_csv('Books/' + CSV)
df = df.dropna(axis=0)
print('Chargement du fichier csv terminé !')

print('\nDébut du scraping......')
for folder in df['path'].unique():
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    ###     methode 1 :
    prefs = {"download.default_directory":os.path.abspath('.')}

    ###     methode 2 :
    # prefs = {"download.default_directory":os.path.abspath('Books/' + folder)}

    options.add_experimental_option("prefs",prefs)
    driver = webdriver.Chrome(executable_path = "C:\\chromedriver.exe", options=options)

    print(f'\nRécupération de la catégorie {folder}')

    for link in df['link'][df['path'] == folder]:
        print(f'Fichier en cours : {link.split("=")[1]}')
        try:
            Download_book(link)
        except:
            print('ERREUR')
            logging.error(link)
            time.sleep(30)

    print(f'Enregistrement de la catégorie {folder}......')
    time.sleep(30)
    driver.quit()

    ###     methode 1 :
    try:
        os.makedirs('Books/' + folder)
    except:
        pass
    pdf = glob.glob('*.pdf')
    for file in pdf:
        new_path = 'Books/' + folder + '/' + file
        shutil.move(file, new_path)
    ###

print('Scraping terminé !')
