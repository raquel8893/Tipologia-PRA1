#!/usr/bin/env python
# coding: utf-8

# In[94]:


import requests
from bs4 import BeautifulSoup
import datetime
import pandas as pd


# In[95]:


# Simulamos ser el navegador Chrome:
headers_sesion_chrome={
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
"Accept-Encoding": "gzip, deflate, br",
"Accept-Language": "es-ES,es;q=0.9",
"Host": "duckduckgo.com",
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36",
"COOKIE": "ah=es-es; p=-2",
"SEC-FETCH-DEST": "document",
"SEC-FETCH-MODE": "navigate",
"SEC-FETCH-SITE": "none",
"SEC-FETCH-USER": "?1",
"UPGRADE-INSECURE-REQUESTS": "1"
}

# Header googlebot:
headers_googlebot={
"User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
}

headers=[headers_sesion_chrome, headers_googlebot]


# In[96]:


url='https://www.casadellibro.com/libros/novela-negra/126000000'

pag = requests.get(url, headers[0], timeout=10)


# In[97]:


soup = BeautifulSoup(pag.content)
#print(soup.prettify())


# In[98]:


libros = soup.find_all("div", class_="product__info")
titulos = []
autores = []
for libro in libros:
    titulo = libro.find("a", class_="title").text
    titulos.append(titulo)
    autor = libro.find("div", class_="author").text
    autores.append(autor)


# In[99]:


df = pd.DataFrame({'Título':titulos, 'Autor':autores})

df.to_csv("libros.csv")


# In[ ]:





# In[11]:





# In[12]:





# In[ ]:





# In[14]:





# In[15]:





# In[ ]:




