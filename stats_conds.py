#!/usr/bin/env python
# coding: utf-8

# In[705]:


import numpy as np
import pandas_datareader as pdr
import pandas as pd
import warnings
import pandas_ta as ta
import streamlit as st

warnings.filterwarnings("ignore")


# In[706]:

#controllo accessi

url = 'http://www.sphereresearch.net/Notebooks/Accessi.xlsx'
accessi = pd.read_excel(url)
accessi = accessi.set_index('User', drop = True)

# In[4]:


Utente = st.text_input("Inserire il nome utente")
Psw = st.text_input("Inserire la password", type='password')


# In[12]:


try:

    if Psw == accessi['Password'][Utente]:

        titolo = st.text_input("Inserire il ticker da analizzare", "VTI")   
    else:
        st.write("""
           In caso di utilizzo senza credenziali non sarà possibile modificare l'asset oggetto di studio.
    """)
        titolo = ("VTI")
except:
    
    st.write("""
       In caso di utilizzo senza credenziali non sarà possibile modificare l'asset oggetto di analisi.
    """)
    titolo = ("VTI")



mesi_proiezione = st.number_input("mesi per la proiezione statistica", 1)



# # Scarica la serie storica e disegnala

# In[708]:


df = pdr.get_data_yahoo(titolo, start = '1980-1-1')['Close']
df = df.resample('M').last()
df = pd.DataFrame(df)
df['index']=df.index
df = df.set_index('index',1)


# In[710]:


st.write("""
## Andamento del titolo selezionato:
 """, titolo)
st.line_chart(df)


# # Crea le features

# In[711]:


df['MA200'] = df.Close.rolling(10).mean()
df['prezzo > MA200'] = np.sign(df.Close-df.MA200)


# In[712]:


df['MA50'] = df.Close.rolling(3).mean()
df['prezzo > MA50'] = np.sign(df.Close-df.MA50)
df['MA 50 > MA200'] = np.sign(df.MA50-df.MA200)


# In[713]:


df.ta.rsi(lenght=5, close=df.Close, append = True)
df.loc[df.RSI_14 >= 75, 'RSI']=2
df.loc[df.RSI_14 <= 30, 'RSI']=0
df.RSI = df.RSI.fillna(1)
df = df.drop('RSI_14',1)


# # Crea le labels

# In[714]:


df = df.dropna()
df['return']=df.Close.shift(-mesi_proiezione)/df.Close-1
df['return+1']=df.Close.shift(-mesi_proiezione)/df.Close
df['return_log']=np.log(df.Close.shift(-mesi_proiezione)/df.Close)


# # Crea il df1 che serivirà per le statistiche sull' intero DB

# In[715]:


df1 = df.drop(['Close', 'MA200', 'MA50'],1)


# # Calcola la feature importance <<< da fare
# https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeRegressor.html

# In[716]:


from sklearn.ensemble import RandomForestRegressor

# df1_ = df1

# df1_['return+1'] = df1_['return+1'].fillna(1)
# df1_['return'] = df1_['return'].fillna(0)

regressor = RandomForestRegressor(random_state=0)
X = np.array(df1.dropna().drop(['return', 'return+1', 'return_log'],1))
y = np.array(df1.dropna()['return'])
regressor.fit(X,y)
importanza = pd.DataFrame(regressor.feature_importances_, columns=['importanza'], index=list(df1.columns)[:len(df1.columns)-3])
previsti = regressor.predict(X)
df_risultati = pd.DataFrame(regressor.predict(X), columns=['previsti'])
df_risultati['reali']=y


# In[718]:


importanza['index']=importanza.index
importanza = importanza.set_index('index', drop=True)
st.bar_chart(importanza)


# In[719]:


§


# # Condizioni da utilizzare

# streamlit.multiselect(element, label, options, default=None, format_func=<class 'str'>, key=None)

# In[720]:


filtri = st.multiselect("seleziona i filtri da utilizzare", ['Media mobile 200', 'Media mobile 50', 'Incrocio delle medie', 'RSI'], default = ['Media mobile 200', 'Media mobile 50', 'Incrocio delle medie', 'RSI'] )


if "Media mobile 200" in filtri:
    condizione1 = "ON"
else:
    condizione1 = "OFF"
    
if "Media mobile 50" in filtri:
    condizione2 = "ON"
else:
    condizione2 = "OFF"
    
if "Incrocio delle medie" in filtri:
    condizione3 = "ON"
else:
    condizione3 = "OFF"
    
if "RSI" in filtri:
    condizione4 = "ON"
else:
    condizione4 = "OFF"
    




if condizione1 == "ON":
    cond1 = (df1['prezzo > MA200'].values==df1.tail(1)['prezzo > MA200'].values)
else:
    cond1 = (df1['prezzo > MA200'].values==df1['prezzo > MA200'].values)
    
if condizione2 == "ON":
    cond2 = (df1['prezzo > MA50'].values==df1.tail(1)['prezzo > MA50'].values)
else:
    cond2 = (df1['prezzo > MA50'].values==df1['prezzo > MA50'].values)
    
if condizione3 == "ON":
    cond3 = (df1['MA 50 > MA200'].values==df1.tail(1)['MA 50 > MA200'].values)
else:
    cond3 = (df1['MA 50 > MA200'].values==df1['MA 50 > MA200'].values)
    
if condizione4 == "ON":
    cond4 = (df1['RSI'].values==df1.tail(1)['RSI'].values)    
else:
    cond4 = (df1['RSI'].values==df1['RSI'].values)   
    

cond = (cond1&cond2&cond3&cond4)


# # Filtra il df in base alle condizioni definite sopra

# In[721]:


df2 = df1.loc[cond]


# # Restituisci le statistiche

# In[722]:


print("STATISTICHE COMPARATE. Filtri applicati: ", filtri)
print("")

casi=  len(df2)
casi_tot = len(df1)
positivi = round((len(df2.loc[df2['return']>=0]))/len(df2)*100,2)
positivi_tot =round((len(df1.loc[df1['return']>0]))/len(df1)*100,2)
media = round(df2['return_log'].mean()*100,2) 
media_tot = round(df1['return_log'].mean()*100,2)

varianza = round(df2['return_log'].std()*100,2) 
varianza_tot=round(df1['return_log'].std()*100,2)


mediana = round(df2['return_log'].median()*100,2) 
mediana_tot = round(df1['return_log'].median()*100,2)

peggiore = round(df2['return'].min()*100,2) 
peggiore_tot = round(df1['return'].min()*100,2)

migliore = round(df2['return'].max()*100,2) 
migliore_tot=round(df1['return'].max()*100,2)

lista_sit = [ casi, positivi, media, varianza, mediana, peggiore, migliore]
lista_tot = [ casi_tot, positivi_tot, media_tot, varianza_tot, mediana_tot, peggiore_tot, migliore_tot]

statistiche = pd.DataFrame(lista_sit, index=['casi', 'positivi (%)', 'media (%)', 'varianza (%)', 'mediana (%)', 'peggiore risultato (%)', 'migliore risultato(%)'], columns=['con i parametri attuali'])
statistiche['nella storia']=lista_tot
statistiche


# In[ ]:




