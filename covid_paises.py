import requests
from bs4 import BeautifulSoup
import pandas as pd
from requests_html import HTMLSession
import re
import datetime as dt
import os

pais = ''
# Definición de funciones #####################################################
def rascador(url):
    '''
    Junta requests.get con bs html.parser. Cómo argumento recibe
    una url. Devuelve el cuerpo de la url pedida cómo html parseado por
    BeautifulSoup.
    '''
    r = requests.get(url)
    return BeautifulSoup(r.text, "html.parser")


def creafila(lista_columnas, lista_valores):
    '''
    Devuelve un df de un sólo regitro a partir de una lista de columnas
    y una lista de valores con el mismo número de elementos.
    - lista_columnas: lista con los nombres de las columnas
    - lista_valores: lista con los valores de cada columna
    '''
    if len(lista_columnas) == len(lista_valores):
        df = pd.DataFrame(dict(zip(lista_columnas, lista_valores)), index=[0])
        return df
    else:
        print("""lista_columnas y lista_valores han de tener el mismo número de
              elementos""")


def num_parser(etiqueta):
    '''
    Dada un etiqueta de texto, devuelve un numéro entero, 0 si es una
    etiqueta vacia o texto .
    '''
    etiqueta = etiqueta.strip()
    if etiqueta == "''" or etiqueta == '':
        return 0
    else:
        try:
            return int(re.sub(r"[^[0-9]+",'', etiqueta))
        except ValueError:
            print("Valor no transformable en número:\n", e)
            return 0


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
    meses_it = {"gennaio": 1, "febbraio": 2, "marzo": 3,
                "aprile": 4, "maggio": 5, "giugno": 6,
                "luglio": 7, "agosto": 8, "settembre": 9,
                "ottobre": 10, "novembre": 11, "dicembre": 12}
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
    re_dia = (r"[0-9]{2}:[0-9]{2}.* ([0-9]+).*[a-zA-Z]+|" +
              r"([0-9]{2}).*[0-9]{2}:[0-9]{2}|" +
              r"([0-9]{2}) [a-zA-Z]+|" +
              r"([0-9]+) [a-zA-Z]+")
    re_mes = (r"[0-9]+.* ([a-zA-Z]{3,}) .*[0-9]{4}|" +
              r"([a-zA-Z]{3,}) (?=[0-9]{2}. )")
    re_año = r"[0-9]{4}"
    re_hh = r"([0-9]{2}):[0-9]{2}"
    re_min = r"[0-9]{2}:([0-9]{2})"
    if pais =='Italy':
        for i in (re.findall(re_dia, fecha)):
            for e in i:
                if not re.match(re_min, e):
                    fecha_dia = e
    else:
        fecha_dia = [dd for dd in re.findall(re_dia, fecha)[0] if len(dd) > 0][0]
    fecha_mes = [mm for mm in re.findall(re_mes, fecha)[0] if len(mm) > 0][0]
    fecha_año = re.findall(re_año, fecha)[0]
    if hora is not None:
        hh = re.findall(re_hh, hora)[0]
        minuto = re.findall(re_min, hora)[0]
    else:
        hh = re.findall(re_hh, fecha)[0]
        minuto = re.findall(re_min, fecha)[0]
    # Generamos una variable con la fecha en un formato de python
    fecha_act = dt.datetime(int(fecha_año), meses[fecha_mes.lower()],
                            int(fecha_dia), int(hh), int(minuto))
    return fecha_act


# Script de recogida de datos #################################################
# Primera página de busqueda:
url = "https://www.worldometers.info/coronavirus/"
# Hacemos llamada y recogemos la página parseada
soup = rascador(url)

# Sacamos la fecha de actualización general
fecha = soup.find_all("div", attrs={'style':'font-size:13px; color:#999; margin-top:5px; text-align:center'})[0].text
fecha_act_gen = fecha_y_hora_parser(fecha, lg="en")

# Filtramos la tabla de datos de todos los países
table = soup.find("table", id="main_table_countries_today")
# filtramos las filas del cuerpo de la tabla
filas = table.tbody.find_all("tr")

# Creamos el df donde guardaremos los resultados
columnas = ['Pais', 'Region', 'Casos totales', 'Fallecimientos',
            'Recuperados', 'Casos activos', 'Casos cerrados', 'Fecha']
df_act = pd.DataFrame(columns=('Pais', 'Region', 'Casos totales',
                               'Fallecimientos', 'Recuperados',
                               'Casos activos', 'Casos cerrados', 'Fecha'))

# Paises para los que obtendremos más detalle:
lista_paises = ['USA', 'Spain', 'Italy']

# Analizamos cada país (=fila)
for fila in filas:
    pais = fila.find('td').text.strip()
    # Algunos países tienen datos más detallados
    # filtramos el enlace a la página con mayor detalle
    a = fila.find('a')
    if a is not None and pais not in lista_paises:
        # Construimos la nueva url
        extension = a.get('href')
        url_final = url + extension
        # Recogemos la nueva página
        soup = rascador(url_final)
        # Sacamos la fecha de actualización
        fecha = soup.find_all("div", attrs={'style':'font-size:13px; color:#999; text-align:center'})[0].text
        fecha_act = fecha_y_hora_parser(fecha, lg="en")
        # Sacamos los datos
        datos = soup.find_all("div", class_="maincounter-number")
        casos = num_parser(datos[0].text)
        fallecimientos = num_parser(datos[1].text)
        recuperados = num_parser(datos[2].text)
        datos = soup.find_all("div", class_="number-table-main")
        if len(datos) == 2:
            casos_activos = num_parser(datos[0].text)
            casos_cerrados = num_parser(datos[1].text)
            # Añadimos la fila al df
            df = creafila(columnas, [pais, 'Total', casos,
                                     fallecimientos, recuperados,
                                     casos_activos, casos_cerrados,
                                     fecha_act])
            df_act = df_act.append(df, ignore_index=True)
        else:
            casos_activos = casos - fallecimientos - recuperados
            casos_cerrados = fallecimientos + recuperados
            # Añadimos la fila al df
            df = creafila(columnas, [pais, 'Total', casos,
                                     fallecimientos, recuperados,
                                     casos_activos, casos_cerrados,
                                     fecha_act])
            df_act = df_act.append(df, ignore_index=True)
    elif pais == 'USA':
        # Construimos la nueva url
        extension = a.get('href')
        url_final = url + extension
        # Recogemos la nueva página
        soup = rascador(url_final)
        # Filtramos la fecha de actualización
        fecha = soup.find_all("div", attrs={'style':'font-size:13px; color:#999; text-align:center'})[0].text
        fecha_act = fecha_y_hora_parser(fecha, lg="en")
        # Filtramos la tabla de datos de regiones
        table = soup.find("table", id="usa_table_countries_today")
        # filtramos las filas del cuerpo de la tabla
        filas2 = table.tbody.find_all("tr")
        for fila2 in filas2:
            # Obtenemos los valores de las celdas
            elementos = fila2.find_all("td")
            region = elementos[0].text.strip()
            casos = num_parser(elementos[1].text)
            fallecimientos = num_parser(elementos[3].text)
            casos_activos = num_parser(elementos[5].text)
            recuperados = casos - casos_activos - fallecimientos
            casos_cerrados = fallecimientos + recuperados
            # Añadimos la fila al df
            df = creafila(columnas, [pais, region, casos,
                                     fallecimientos, recuperados,
                                     casos_activos, casos_cerrados,
                                     fecha_act])
            df_act = df_act.append(df, ignore_index=True)
        # filtramos los datos totales
        datos = soup.find_all("div", class_="maincounter-number")
        casos = num_parser(datos[0].text)
        fallecimientos = num_parser(datos[1].text)
        recuperados = num_parser(datos[2].text)
        df = creafila(columnas, [pais, 'Total', casos,
                                 fallecimientos, recuperados,
                                 casos_activos, casos_cerrados,
                                 fecha_act])
        df_act = df_act.append(df, ignore_index=True)
    elif pais == 'Spain':
        # Para España sacamos los datos del Ministerio de Sanidad
        url_final = 'https://covid19.isciii.es/'
        # Se trata de una página dinámica, por lo que usamos requests-html
        # Iniciamos una sesión
        sesion = HTMLSession()
        # Mandamos la petición
        r = sesion.get(url_final)
        # Ejecutamos el método render de la sesión para ejecutar los
        # scripts de javascript y que se cargue los datos de la fecha actual
        r.html.render()
        # Recogemos la fecha y la hora (requests-html funciona con
        # selectores CSS)
        fecha = r.html.find('#fecha', first=True).text
        hora = r.html.find('#hora', first=True).text
        fecha_act = fecha_y_hora_parser(fecha, hora, lg='es')
        # Obtenemos la tabla de regiones
        table = r.html.find(("div.column:nth-child(1) > div:nth-child(3) > " +
                             "table:nth-child(1) > tbody:nth-child(2)"),
                            first=True)
        # Obtenemos las filas de la tabla de regiones
        filas2 = table.find("tr")
        for fila2 in filas2:
            elementos = fila2.find("td")
            region = elementos[0].text
            casos = num_parser(elementos[1].text)
            # Añadimos la fila al df
            df = creafila(columnas, [pais, region, casos, None,
                                     None, None, None, fecha_act])
            df_act = df_act.append(df, ignore_index=True)
        # Obtenemos los valores totales para España
        casos = num_parser(r.html.find('#casos', first=True).text)
        recuperados = num_parser(r.html.find('#recuperados', first=True).text)
        fallecimientos = num_parser(r.html.find('#defunciones',
                                                first=True).text)
        # Añadimos la fila al df
        casos_activos = casos - fallecimientos - recuperados
        casos_cerrados = fallecimientos + recuperados
        df = creafila(columnas, [pais, 'Total', casos,
                                 fallecimientos, recuperados,
                                 casos_activos,
                                 casos_cerrados,
                                 fecha_act])
        df_act = df_act.append(df, ignore_index=True)
        # Cerramos conexiones
        r.close()
        sesion.close()
    elif pais == 'Italy':
        # Buscamos los datos por región en la wikipedia
        url_final = ('https://it.wikipedia.org/wiki/' +
                     'Pandemia_di_COVID-19_del_2020_in_Italia')
        # Hacemos la llamada y parseamos la respuesta
        soup = rascador(url_final)
        # seleccionamos la tabla con el contenido de las regiones
        table = soup.find("table", class_="wikitable sortable")
        filas2 = table.find_all("tr")
        # sacamos la fecha de actualización
        fecha_hora = filas2[-1].find("small").text
        fecha_act = fecha_y_hora_parser(fecha_hora, lg="it")
        # Sacamos los datos de las regiones (filas 0 a 20)
        for fila2 in filas2[1:21]:
            elementos = fila2.find_all("td")
            region = elementos[0].text.strip()
            casos = num_parser(elementos[1].text)
            fallecimientos = num_parser(elementos[2].text)
            recuperados = num_parser(elementos[3].text)
            # Añadimos fila al df
            casos_activos = casos - fallecimientos - recuperados
            casos_cerrados = fallecimientos + recuperados
            df = creafila(columnas, [pais, region, casos,
                                     fallecimientos, recuperados,
                                     casos_activos,
                                     casos_cerrados,
                                     fecha_act])
            df_act = df_act.append(df, ignore_index=True)
        # Los datos totales para Italia están en la fila 21
        elementos = filas2[21].find_all("th")
        casos = num_parser(elementos[1].text)
        fallecimientos = num_parser(elementos[2].text)
        recuperados = num_parser(elementos[3].text)
        casos_activos = casos - fallecimientos - recuperados
        casos_cerrados = fallecimientos + recuperados
        df = creafila(columnas, [pais, 'Total', casos,
                                 fallecimientos, recuperados,
                                 casos_activos,
                                 casos_cerrados,
                                 fecha_act])
        df_act = df_act.append(df, ignore_index=True)
    else:
        # Resto de casos
        elementos = fila.find_all('td')
        casos = num_parser(elementos[1].text)
        fallecimientos = num_parser(elementos[3].text)
        recuperados = num_parser(elementos[5].text)
        casos_activos = num_parser(elementos[6].text)
        casos_cerrados = fallecimientos + recuperados
        df = creafila(columnas, [pais, 'Total', casos,
                                 fallecimientos, recuperados,
                                 casos_activos,
                                 casos_cerrados,
                                 fecha_act_gen])
        df_act = df_act.append(df, ignore_index=True)


# Inspección de resultados ####################################################
# Debug
print("Se ha recogido información de {} regiones".format(len(df_act)))

# Formateo y extracción #######################################################
# Formateo de campos numéricos del df
try:
    df_act.loc[:, ['Casos totales', 'Fallecimientos',
                   'Recuperados', 'Casos activos',
                   'Casos cerrados']].applymap(lambda x:
                                               int(str(x).replace(",", ""))
                                               if isinstance(x, str) else x)
except ValueError as e:
    print('Tansformación de etiquetas numericas a números a fallado debido a:',
          e)
# Debug

# Extracción del df cómo un archivo csv en el directorio de ejecución
archivo = "prueba_paises.csv"
df_act.to_csv(archivo, index=False, sep=";", decimal=",", encoding="latin1",
              date_format='%Y-%m-%d %H:%M:%S')
print("Archivo {} se ha creado en el siguiente directorio:".format(archivo))
print(os.getcwd())
