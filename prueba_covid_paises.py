import requests
from bs4 import BeautifulSoup
from time import sleep
import pandas as pd
import csv

url = "https://www.worldometers.info/coronavirus/"
r = requests.get(url)
soup = BeautifulSoup(r.text, "html.parser")    
table = soup.find_all("td")  # Obtenmos la lista de todos los tags de la lista de juegos de la url
lista = []
contador = 0
multiple = 11
#print(table[0])
dict_paises = dict()
for i in range(0, len(table)):
    resto = i % multiple
    if resto == 0:
        #lista.append(table[i].text)
        a = table[i].find('a')
        if a != None:
        #print(table[i])
        #print (table[i].text)
            pais = table[i].text
            extension = a.get('href')
            url_final = url + extension
            r = requests.get(url_final)
            #print (url_final)
            soup = BeautifulSoup(r.text, "html.parser")
            datos = soup.find("div", class_="maincounter-number").text
            dict_paises[pais] = [datos]
            #print (datos.text)
        #lista.append(extension)
        #print (table[i])
        #print (extension)
df_act = pd.DataFrame(dict_paises.values(), index=dict_paises.keys(), columns=[
                       'Casos'])        
archivo = "prueba_paises.csv"
df_act.to_csv(archivo)

# import requests
# from bs4 import BeautifulSoup
 
# #url = "http://www.htmlandcssbook.com/code-samples/chapter-04/example.html"
 
# # Getting the webpage, creating a Response object.
# #response = requests.get(url)
 
# # Extracting the source code of the page.
# #data = response.text

# r = requests.get("http://www.htmlandcssbook.com/code-samples/chapter-04/example.html")
# # Passing the source code to BeautifulSoup to create a BeautifulSoup object for it.
# #soup = BeautifulSoup(data, 'lxml')
# soup = BeautifulSoup(r.text, "html.parser") 
 
# # Extracting all the <a> tags into a list.
# tags = soup.find_all('a')
# print(tags[0])
# # Extracting URLs from the attribute href in the <a> tags.
# #for tag in tags:
# for i in range(0, len(tags)):
    # print(tags[i].get('href'))