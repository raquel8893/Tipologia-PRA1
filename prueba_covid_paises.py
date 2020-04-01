import requests
from bs4 import BeautifulSoup
from time import sleep
import pandas as pd
from requests_html import HTMLSession
import re
import datetime as dt


def rascador(url):
    '''
    Función que junta requsts.get con bs html.parser. Cómo argumento recibe
    una url. Devuelve el cuerpo de la url pedida html parseado por BeautifulSoup
    '''
    r = requests.get(url)
    return BeautifulSoup(r.text, "html.parser")


def fecha_y_hora_parser(fecha, hora=None, lg='es'):
    '''
    Dada una/dos cadena/s de texto fecha, hora y un indicador de idioma,
    devuelve la fecha y hora en un objeto datetime de python.
    - fecha: cadena de texto que incluya la fecha con día numérico de dos
             cifras, mes cómo nombre en texto completo y año cómo número;
             opcionalmente y si hora es None, también puede incluir la hora
             y minuto con formato hh:mm
    - hora:  cadena de texto con hora cómo dos numeros y minuto cómo dos
             numeros separados por dos puntos
    - lg:    cadena de texto que sigue formato iso de idiomas indicadora
             del idioma en que esta escrito el mes (sólo se acepta es, it y en)
    '''
    # Diccionarios de meses (es, it y en)
    meses_es = {"enero": 1, "febrero": 2, "marzo": 3,
                "abril": 4, "mayo": 5, "junio": 6,
                "julio": 7, "agosto": 8, "septiembre": 9,
                "octubre": 10, "noviembre": 11, "diciembre": 12}
    meses_en = {"january": 1, "february": 2, "march": 3,
                "april": 4, "may": 5, "june": 6,
                "july": 7, "august": 8, "september": 9,
                "october": 10, "november": 11, "december": 12}
    meses_it = {"gennaio":1, "febbraio":2, "marzo":3,
                "aprile":4, "maggio":5, "giugno":6,
                "luglio":7, "agosto":8, "settembre":9,
                "ottobre":10, "novembre":11, "dicembre":12}
    # Validación de idioma
    if lg == 'es':
        meses = meses_es
    elif lg == 'en':
        meses = meses_en
    elif lg == 'it':
        meses = meses_it
    else:
        return print('Lengua no sorportada')
    # Usamos re para trocear las etiquetas en los valores que nos interesan
    re_dia = r"[0-9]{2}:[0-9]{2}.* ([0-9]+).*[a-zA-Z]+|([0-9]{2}).*[0-9]{2}:[0-9]{2}|([0-9]{2}) [a-zA-Z]+"
    re_mes = r"[0-9]{2}.* ([a-zA-Z]{3,}) .*[0-9]{4}|([a-zA-Z]{3,}) (?=[0-9]{2}. )"
    re_año = r"[0-9]{4}"
    re_hh = r"([0-9]{2}):[0-9]{2}"
    re_min = r"[0-9]{2}:([0-9]{2})"
    fecha_dia = [dd for dd in re.findall(re_dia, fecha)[0] if len(dd) > 0][0]
    fecha_mes = [mm for mm in re.findall(re_mes, fecha)[0] if len(mm) > 0][0]
    fecha_año = re.findall(re_año, fecha)[0]
    if hora != None:
        hh = re.findall(re_hh, hora)[0]
        minuto = re.findall(re_min, hora)[0]
    else :
        hh = re.findall(re_hh, fecha)[0]
        minuto = re.findall(re_min, fecha)[0]
    # Generamos una variable con la fecha en un formato de python
    fecha_act = dt.datetime(int(fecha_año), meses[fecha_mes.lower()],
                            int(fecha_dia), int(hh), int(minuto))
    return fecha_act

url = "https://www.worldometers.info/coronavirus/"
soup = rascador(url)
table = soup.find_all("td")  # Obtenmos la lista de todos los tags de la lista de juegos de la url
lista = []
contador = -1
multiple = 11
df_act = pd.DataFrame(columns=('Pais', 'Region', 'Casos totales', 'Fallecimientos', 'Recuperados', 'Casos activos', 'Casos cerrados', 'Fecha'))
#dict_paises = dict()
for i in range(0, len(table)):
    resto = i % multiple
    if resto == 0:
        a = table[i].find('a')
        if a != None:
            pais = table[i].text
            extension = a.get('href')
            url_final = url + extension
            soup = rascador(url_final)
            datos = soup.find_all("div", class_="maincounter-number")
            casos = datos[0].text
            fallecimientos = datos[1].text
            recuperados = datos[2].text
            datos = soup.find_all("div", class_="number-table-main")
            if len(datos) == 2:
                casos_activos = datos[0].text
                casos_cerrados = datos[1].text
                contador = contador + 1
                df_act.loc[contador]=[pais, 'Total', casos, fallecimientos, recuperados, casos_activos, casos_cerrados, None]
                #dict_paises[pais] = ['Total', casos, fallecimientos, recuperados, casos_activos, casos_cerrados]
            else:
                #dict_paises[pais] = ['Total', casos, fallecimientos, recuperados, None, None]
                contador = contador + 1
                df_act.loc[contador]=[pais, 'Total', casos, fallecimientos, recuperados, None, None, None]
            if pais =='USA':
                table2 = soup.find_all("tr")
                for fila in table2[1:len(table2)-1]:
                    cont = 0
                    for elemento in fila.find_all("td"):
                        if cont == 0:
                            region = elemento.text.strip()
                            cont += 1
                        elif cont == 1:
                            casos = elemento.text.strip()
                            cont += 1
                        elif cont == 2:
                            cont += 1
                        elif cont == 3:
                            fallecimientos = elemento.text.strip()
                            cont += 1
                        elif cont == 4:
                            cont += 1
                        elif cont == 5:
                            casos_activos = elemento.text.strip()
                            cont += 1
                        elif cont == 6:
                            pass
                            #dict_paises[pais] = [region, casos, fallecimientos, None, casos_activos, None]
                    contador += 1
                    df_act.loc[contador]=[pais, region, casos, fallecimientos, None, casos_activos, None, None]
            if pais == 'Spain':
                url_final ='https://covid19.isciii.es/'
                sesion = HTMLSession()
                r = sesion.get(url_final)
                r.html.render()
                fecha = r.html.find('#fecha', first=True).text
                hora = r.html.find('#hora', first=True).text
                fecha_act = fecha_y_hora_parser(fecha, hora, lg='es')
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
                        contador += 1
                        df_act.loc[contador]=[pais, region, casos, None, None, None, None, fecha_act]
                        #dict_paises[pais] = [region, casos, None, None, None, None]
                r.close()
                sesion.close()
            if pais == 'Italy':
                url_final = 'https://it.wikipedia.org/wiki/Pandemia_di_COVID-19_del_2020_in_Italia'
                soup = rascador(url_final)
                table3 = soup.find("table", class_="wikitable sortable")
                table2 = table3.find_all("td")
                fecha_hora = table2[-1].find("small").text
                fecha_act = fecha_y_hora_parser(fecha_hora, lg="it")
                cont = 0
                for elemento in table2[:-1]:
                    if cont == 0:
                        region = elemento.text.strip()
                        cont += 1
                    elif cont == 1:
                        casos = elemento.text.strip()
                        cont += 1
                    elif cont == 2:
                        fallecimientos = elemento.text.strip()
                        cont += 1
                    elif cont == 3:
                        recuperados = elemento.text.strip()
                        cont += 1
                    elif cont == 4:
                        cont = 0
                        contador = contador + 1
                        #dict_paises[pais] = [region, casos, fallecimientos, recuperados, None, None]
                        df_act.loc[contador]=[pais, region, casos, fallecimientos, recuperados, None, None, fecha_act]

#print(df_act)
#df_act = pd.DataFrame(dict_paises.values(), index=dict_paises.keys(), columns=[

print(contador)                       #'Region', 'Casos totales', 'Fallecimientos', 'Recuperados', 'Casos activos', 'Casos cerrados'])
print(len(df_act))
try:
    df_act.loc[:,['Casos totales', 'Fallecimientos',
                  'Recuperados','Casos activos',
                  'Casos cerrados']].applymap(lambda x: float(str(x).replace(",", ".")) if isinstance(x, str) else x)
except ValueError as e:
    print('Tansformación de etiquetas numericas a números a fallado debido a:', e)

print(df_act)
archivo = "prueba_paises.csv"
df_act.to_csv(archivo, index = False, sep=";", decimal=",", encoding="latin1", date_format='%d/%m/%Y')
