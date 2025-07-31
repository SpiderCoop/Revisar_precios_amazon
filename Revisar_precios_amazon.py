# -*- coding: utf-8 -*-
"""
Created on Sun Nov  24 14:18:41 2024

@author: DJIMENEZ
"""

# Librerias necesarias -------------------------------------------------------------------------

import sys
import os

import pandas as pd

from dotenv import load_dotenv

from auxiliar_tools.web_scrapping_tools import configurar_driver, obtener_precio
from auxiliar_tools.check_logs import revisar_registros_envio
from auxiliar_tools.mail_tools import enviar_correo


# Configuracion iniacial -------------------------------------------------------------------------

# Obtener la ruta del directorio del archivo de script actual para establecer el directorio de trabajo
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)
os.chdir(script_dir)

# Cargamos las variables de entorno
load_dotenv()
cuenta = os.getenv('Cuenta')
password = os.getenv('password')
destinatarios = os.getenv("Destinatarios").split(',')


# Configurar driver
driver = configurar_driver()

# Cargar base de datos de consultas
prices_df = pd.read_csv('prices_data.csv')

# Flujo de trabajo -------------------------------------------------------------------------

notificar = False
productos_en_oferta = {}
for index, row in prices_df.iterrows():
    url = row['url']
    min_price = row['min_price']
    actual_price = row['actual_price']

    print(url)

    try:
        # Obtener el precio del producto
        nombre, precio = obtener_precio(driver, url)

        # Si el precio mínimo es 0, lo actualizamos al precio actual
        if min_price == 0 or pd.isna(min_price) or min_price == '':
            prices_df.at[index, 'min_price'] = precio

        # Calcular la variación del precio
        variacion = (precio / actual_price - 1)*100

        if precio < min_price:
            prices_df.at[index, 'min_price'] = precio
            notificar = True
            productos_en_oferta[nombre] = precio
        elif variacion < -15:
            notificar = True
            productos_en_oferta[nombre] = precio

        # Actualizar el precio actual en el DataFrame
        prices_df.at[index, 'actual_price'] = precio

    except:
        pass

# Guardar los cambios en el DataFrame
prices_df.to_csv('prices_data.csv', index=False)

# Enviar notificaciones por correo si hay productos en oferta
if True:

    cuerpo_correo = ""
    for nombre, precio in productos_en_oferta.items():
        cuerpo_correo += f"El precio de {nombre} ha cambiado. Nuevo precio: ${precio}\n"

    enviar_correo(cuenta=cuenta,
    password=password,
    destinatarios=destinatarios,
    asunto=f"Notificacion de ofertas",
    cuerpo_correo=cuerpo_correo)

