import requests
from bs4 import BeautifulSoup
from time import sleep
import pandas as pd
import csv
from requests_html import HTMLSession

url = "https://www.worldometers.info/coronavirus/"
r = requests.get(url)
soup = BeautifulSoup(r.text, "html.parser")    
table = soup.find_all("td")  # Obtenmos la lista de todos los tags de la lista de juegos de la url
lista = []
contador = -1
multiple = 11
df_act = pd.DataFrame(columns=('Pais', 'Region', 'Casos totales', 'Fallecimientos', 'Recuperados', 'Casos activos', 'Casos cerrados'))
#dict_paises = dict()
for i in range(0, len(table)):
    resto = i % multiple
    if resto == 0:
        a = table[i].find('a')
        if a != None:
            pais = table[i].text
            extension = a.get('href')
            url_final = url + extension
            r = requests.get(url_final)
            soup = BeautifulSoup(r.text, "html.parser")
            datos = soup.find_all("div", class_="maincounter-number")
            casos = datos[0].text
            fallecimientos = datos[1].text
            recuperados = datos[2].text
            datos = soup.find_all("div", class_="number-table-main")
            if len(datos) == 2:
                casos_activos = datos[0].text
                casos_cerrados = datos[1].text
                contador = contador + 1
                df_act.loc[contador]=[pais, 'Total', casos, fallecimientos, recuperados, casos_activos, casos_cerrados]
                #dict_paises[pais] = ['Total', casos, fallecimientos, recuperados, casos_activos, casos_cerrados]
            else:
                #dict_paises[pais] = ['Total', casos, fallecimientos, recuperados, None, None]
                contador = contador + 1
                df_act.loc[contador]=[pais, 'Total', casos, fallecimientos, recuperados, None, None]
            if pais =='USA':
                table2 = soup.find_all("td")
                cont = 0
                for elemento in table2:
                    if cont == 0:
                        region = elemento.text
                        cont += 1
                    elif cont == 1:
                        casos = elemento.text
                        cont += 1
                    elif cont == 2:
                        cont += 1
                    elif cont == 3:
                        fallecimientos = elemento.text
                        cont += 1
                    elif cont == 4:
                        cont += 1
                    elif cont == 5:
                        casos_activos = elemento.text
                        cont += 1
                    elif cont == 6:
                        cont = 0
                        #dict_paises[pais] = [region, casos, fallecimientos, None, casos_activos, None]
                        contador = contador + 1
                        df_act.loc[contador]=[pais, region, casos, fallecimientos, None, casos_activos, None]
            if pais == 'Spain':
                url_final ='https://covid19.isciii.es/'
                sesion = HTMLSession()
                r = sesion.get(url_final)
                r.html.render()
                table2 = [td.text for td in r.html.find("td")]
                cont = 0
                for elemento in table2:
                    if cont == 0:
                        region = elemento
                        cont += 1
                    elif cont == 1:
                        casos = elemento
                        cont += 1
                    elif cont == 2:
                        cont += 1
                    elif cont == 3:
                        cont = 0
                        contador = contador + 1
                        df_act.loc[contador]=[pais, region, casos, None, None, None, None]
                        #dict_paises[pais] = [region, casos, None, None, None, None]
                r.close()
                sesion.close()
            if pais == 'Italy':
                url_final = 'https://it.wikipedia.org/wiki/Pandemia_di_COVID-19_del_2020_in_Italia'
                r = requests.get(url_final)
                soup = BeautifulSoup(r.text, "html.parser")
                table3 = soup.find("table", class_="wikitable sortable")
                table2 = table3.find_all("td")
                cont = 0
                for elemento in table2:
                    if cont == 0:
                        region = elemento.text
                        cont += 1
                    elif cont == 1:
                        casos = elemento.text
                        cont += 1
                    elif cont == 2:
                        fallecimientos = elemento.text
                        cont += 1
                    elif cont == 3:
                        recuperados = elemento.text
                        cont += 1
                    elif cont == 4:
                        cont = 0
                        contador = contador + 1
                        #dict_paises[pais] = [region, casos, fallecimientos, recuperados, None, None]
                        df_act.loc[contador]=[pais, region, casos, fallecimientos, recuperados, None, None]

        
            
#print(df_act)
#df_act = pd.DataFrame(dict_paises.values(), index=dict_paises.keys(), columns=[

print(contador)                       #'Region', 'Casos totales', 'Fallecimientos', 'Recuperados', 'Casos activos', 'Casos cerrados'])
print(len(df_act))
print(df_act)                      
archivo = "prueba_paises.csv"
df_act.to_csv(archivo, index = False)

