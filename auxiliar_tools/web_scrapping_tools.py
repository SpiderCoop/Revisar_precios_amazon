# -*- coding: utf-8 -*-
"""
Created on Wed Jul 30 17:18:41 2025

@author: DJIMENEZ
"""
# Librerias necesarias ------------------------------------------------------------------------------------------
import os

import pandas as pd
import re

import requests

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

import time

# Funcion auxiliar -------------------------------


def limpiar_caracteres(texto):
    """
    Elimina los acentos de un string utilizando expresiones regulares.
    """
    acentos = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
        'ü': 'u', 'Ü': 'U',
        'ñ': 'n', 'Ñ': 'N',
        '/':'_', ':':'_',
        '?':'', ',':''
    }

    # Reemplazar cada carácter acentuado por su equivalente sin acento
    patron = re.compile('|'.join(re.escape(k) for k in acentos.keys()))
    return patron.sub(lambda x: acentos[x.group()], texto)

# Funciones ------------------------------------------------------------------------------------------

def configurar_driver(directorio_descarga:str = None) -> webdriver.Chrome:
    """
    Configura el driver de Selenium con opciones para GitHub Actions y descargas en un directorio específico.

    Args:
        directorio_descarga (str): Ruta donde se guardarán los archivos descargados.

    Returns:
        webdriver.Chrome: Instancia del driver configurado.
    """
    # Crear el directorio de descarga si no existe
    if directorio_descarga and not os.path.exists(directorio_descarga):
        os.makedirs(directorio_descarga)

    # Configura opciones para Chrome
    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": directorio_descarga, # Directorio para descargas
        "download.prompt_for_download": False,             # Evitar ventana de diálogo de descarga
        "download.directory_upgrade": True,                # Actualizar directorios automáticamente
        "safebrowsing.enabled": True                       # Habilitar navegación segura
    })

    # Configuraciones para entornos sin interfaz gráfica (headless)
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")  # Solucionar problemas de memoria compartida
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-logging")  # Desactivar logs de DevTools
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--log-level=3")

    # Iniciar el driver usando webdriver-manager para instalar ChromeDriver automáticamente
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    return driver

# Funcion para revisar la pagina de miembros de ISDA
def obtener_precio(driver, url:str) -> float:
    """
    Obtiene el precio de un producto en Amazon utilizando Selenium.
    """

    # Navegar a la URL del producto
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)

    except:
        print("❌ No se pudo acceder a la página del producto o el formato ha cambiado.")
        return None, None

    # Buscar el titulo del producto
    try:
        product_element = wait.until(EC.presence_of_element_located((By.ID, 'productTitle')))
        product_name = product_element.get_attribute("textContent").strip()

    except:
        print("❌ No se encontró el elemento del nombre")
        product_name = None


    # Buscar el precio
    try:
        price_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'a-offscreen')))
        price_text = price_element.get_attribute("textContent").strip()
        price = float(price_text.replace('$', '').replace(',', ''))

    except:
        try:
            price_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'aok-offscreen')))
            price_text = price_element.get_attribute("textContent").strip()
            price = float(price_text.replace('$', '').replace(',', ''))

        except:
            print("❌ No se encontró el elemento del precio")
            price = None
    
    return product_name, price
