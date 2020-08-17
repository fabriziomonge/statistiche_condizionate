#!/usr/bin/env python
# coding: utf-8

# In[76]:


import numpy as np
import pandas_datareader as pdr
import pandas as pd
import streamlit as st

from PIL import Image
image = Image.open('statistiche_condizionate.png')
st.sidebar.image(image, use_column_width=True)


st.write("""
# Statistiche condizionate APP 1.0
L'applicazione consente di calcolare le statistiche di rendimento e volatilità di un titolo o di un indice in base ai parametri scelti dall' operatore
""")


# In[77]:


# In[706]:

#controllo accessi

url = 'http://www.sphereresearch.net/Notebooks/Accessi.xlsx'
accessi = pd.read_excel(url)
accessi = accessi.set_index('User', drop = True)

Utente = st.text_input("Inserire il nome utente")
Psw = st.text_input("Inserire la password", type='password')

try:
    
    if Psw == accessi['Password'][Utente]:
        
        st.write("""
        ## Base dell' analisi:
        """)

        titolo = st.text_input("Inserire il ticker da analizzare", "VTI")
        st.write("""
        A questo link è possibile trovare un elenco dei principali tickers:
        """)
        
        st.write('https://wp.me/P9LLei-37')
        
    else:
        st.write("""
           In caso di utilizzo senza credenziali non sarà possibile modificare l'asset oggetto di studio.
    """)
        
        st.write("""
        ## Base dell' analisi:
        """)
        
        titolo = ("VTI")
except:
    
    st.write("""
       In caso di utilizzo senza credenziali non sarà possibile modificare l'asset oggetto di analisi.
    """)
    
    st.write("""
    ## Base dell' analisi:
    """)
    
    titolo = ("VTI")

mesi_proiezione = st.number_input("Mesi per la proiezione statistica", 1)


# # Scarica la serie storica e disegnala

# In[78]:

try:

    df = pdr.get_data_yahoo(titolo, start = '1980-1-1')['Close']
    df = df.resample('M').last()
    df = pd.DataFrame(df)
    df['index']=df.index
    df = df.set_index('index',1)

except:
    
    st.write("""
    ## Attenzione: il ticker inserito non è stato trovato!
    Verrà considerato l'andamento del ticker di default...
    """)
    
    df = pdr.get_data_yahoo('VTI', start = '1980-1-1')['Close']
    df = df.resample('M').last()
    df = pd.DataFrame(df)
    df['index']=df.index
    df = df.set_index('index',1)

    titolo = "VTI"

    

# In[79]:


st.write("""
## Andamento del titolo selezionato:
 """, titolo)
st.line_chart(df)


# # Definiamo RSI

# In[80]:


def RSI(serie, lenght):
    funzione_df = pd.DataFrame(serie)
    funzione_df['var']=funzione_df.Close-funzione_df.Close.shift(1)
    funzione_df.loc[funzione_df['var']>0, 'var_pos']=funzione_df['var']
    funzione_df.loc[funzione_df['var']<0, 'var_neg']=abs(funzione_df['var'])
    funzione_df = funzione_df.fillna(0)
    funzione_df['media_pos']= funzione_df['var_pos'].rolling(lenght).mean()
    funzione_df['media_neg']= funzione_df['var_neg'].rolling(lenght).mean()
    funzione_df['rs']=funzione_df['media_pos']/funzione_df['media_neg']
    funzione_df['RSI']= 100-100 / (1 + funzione_df['rs'])
    lista_rsi = list(funzione_df['RSI'])
    return lista_rsi

#definiamo le funzione drawdown

def dd(serie):
    serief = pd.DataFrame(serie.values, columns = ["prezzo"])
    lista = []
    lista2 =[]
    a1 = serief['prezzo'].values[0]
    lista.append(a1)
    lista2.append(0)
    for i in range (1,len(serief)):
        a = max((serief['prezzo'][i]),lista[i-1])
        lista.append(a)
        dd = ((serief['prezzo'][i])-lista[i])/lista[i]
        lista2.append(dd)
    return lista2


# # Crea le features

# In[81]:


df['MA200'] = df.Close.rolling(10).mean()
df['prezzo > MA200'] = np.sign(df.Close-df.MA200)


# In[82]:


df['MA50'] = df.Close.rolling(3).mean()
df['prezzo > MA50'] = np.sign(df.Close-df.MA50)
df['MA 50 > MA200'] = np.sign(df.MA50-df.MA200)


# In[83]:


df['RSI_F'] = RSI(df.Close, 14)
df.loc[df.RSI_F >= 80, 'RSI']=2
df.loc[df.RSI_F <= 20, 'RSI']=0
df.RSI = df.RSI.fillna(1)
# df = df.drop('RSI_F',1)

#calcoliamo il drawdown storico binarizzato

df['DD'] = dd(df.Close)
df.DD = pd.cut(df.DD, 4, labels=False)


# # Crea le labels

# In[84]:


df = df.dropna()
df['return']=df.Close.shift(-mesi_proiezione)/df.Close-1
df['return+1']=df.Close.shift(-mesi_proiezione)/df.Close
df['return_log']=np.log(df.Close.shift(-mesi_proiezione)/df.Close)


# # Crea il df1 che serivirà per le statistiche sull' intero DB

# In[85]:


df1 = df.drop(['Close', 'MA200', 'MA50'],1)


# # Calcola la feature importance <<< da fare
# https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeRegressor.html

# In[86]:


# from sklearn.ensemble import RandomForestRegressor

# # df1_ = df1

# # df1_['return+1'] = df1_['return+1'].fillna(1)
# # df1_['return'] = df1_['return'].fillna(0)

# regressor = RandomForestRegressor(random_state=0)
# X = np.array(df1.dropna().drop(['return', 'return+1', 'return_log'],1))
# y = np.array(df1.dropna()['return'])
# regressor.fit(X,y)
# importanza = pd.DataFrame(regressor.feature_importances_, columns=['importanza'], index=list(df1.columns)[:len(df1.columns)-3])
# previsti = regressor.predict(X)
# df_risultati = pd.DataFrame(regressor.predict(X), columns=['previsti'])
# df_risultati['reali']=y


# In[87]:


# importanza['index']=importanza.index
# importanza = importanza.set_index('index', drop=True)
# st.bar_chart(importanza)


# # Condizioni da utilizzare

# streamlit.multiselect(element, label, options, default=None, format_func=<class 'str'>, key=None)

# In[88]:

st.write("""
## Parametri disponibili per l'analisi statistica:
 """)
df_plotted = df[['Close','MA200','MA50']]
df_plotted2 = df[['RSI_F']]
df_plotted3 = df[['DD']]


if st.checkbox('Mostra gli indicatori disponibili'):

    st.line_chart(df_plotted)
    st.line_chart(df_plotted2)
    st.line_chart(df_plotted3)

st.write("""
## Seleziona i parametri che intendi considerare:
 """)
filtri = st.multiselect("Utilizza il selettore qui sotto per variare i parametri", ['Media mobile 200', 'Media mobile 50', 'Incrocio delle medie', 'RSI', 'Drawdown'], default = ['Media mobile 200', 'Media mobile 50', 'Incrocio delle medie', 'RSI', 'Drawdown'] )


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
    
if "Drawdown" in filtri:
    condizione5 = "ON"
else:
    condizione5 = "OFF"



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

if condizione5 == "ON":
    
    cond5 = (df1['DD'].values==df1.tail(1)['DD'].values)    
else:
    cond5 = (df1['DD'].values==df1['DD'].values)   
    
    

cond = (cond1&cond2&cond3&cond4&cond5)


# # Filtra il df in base alle condizioni definite sopra

# In[89]:


df2 = df1.loc[cond]


# # Restituisci le statistiche

# In[90]:


print("STATISTICHE COMPARATE. Filtri applicati: ", filtri)
print("")

casi=  len(df2.dropna())
casi_tot = len(df1.dropna())
positivi_ass = round((len(df2.dropna().loc[df2.dropna()['return']>=0])))
positivi = round((len(df2.dropna().loc[df2.dropna()['return']>=0]))/len(df2.dropna())*100,2)
positivi_tot_ass =round((len(df1.dropna().loc[df1.dropna()['return']>0])))
positivi_tot =round((len(df1.dropna().loc[df1.dropna()['return']>0]))/len(df1.dropna())*100,2)
media = round(df2.dropna()['return_log'].mean()*100,2) 
media_tot = round(df1.dropna()['return_log'].mean()*100,2)

varianza = round(df2.dropna()['return_log'].std()*100,2) 
varianza_tot=round(df1.dropna()['return_log'].std()*100,2)


mediana = round(df2.dropna()['return_log'].median()*100,2) 
mediana_tot = round(df1.dropna()['return_log'].median()*100,2)

peggiore = round(df2.dropna()['return'].min()*100,2) 
peggiore_tot = round(df1.dropna()['return'].min()*100,2)

migliore = round(df2.dropna()['return'].max()*100,2) 
migliore_tot=round(df1.dropna()['return'].max()*100,2)

lista_sit = [ casi, positivi_ass, positivi, media, varianza, mediana, peggiore, migliore]
lista_tot = [ casi_tot,positivi_tot_ass, positivi_tot, media_tot, varianza_tot, mediana_tot, peggiore_tot, migliore_tot]

statistiche = pd.DataFrame(lista_sit, index=['Casi', 'Di cui positivi', 'Positivi (%)', 'Media (%)', 'Varianza (%)', 'Mediana (%)', 'Peggiore risultato (%)', 'Migliore risultato(%)'], columns=['Con i parametri attuali'])
statistiche['Nella storia']=lista_tot

st.write("""
## Statistiche elaborate in base all'attuale condizione:
 """)

st.write("""Asset considerato: """, titolo)
st.write("""Inizio analisi: """,df.index[0])
st.write("""Fine analisi: """,df.index[len(df)-2])
st.write("""Mesi proiezione: """,mesi_proiezione)

#trasforma alcune colonne in percentuale

statistiche = statistiche.transpose()

statistiche['Positivi (%)'] = pd.Series(["{0:.2f}%".format(val) for val in statistiche['Positivi (%)']], index = statistiche.index)
statistiche['Media (%)'] = pd.Series(["{0:.2f}%".format(val) for val in statistiche['Media (%)']], index = statistiche.index)
statistiche['Varianza (%)'] = pd.Series(["{0:.2f}%".format(val) for val in statistiche['Varianza (%)']], index = statistiche.index)
statistiche['Mediana (%)'] = pd.Series(["{0:.2f}%".format(val) for val in statistiche['Mediana (%)']], index = statistiche.index)
statistiche['Peggiore risultato (%)'] = pd.Series(["{0:.2f}%".format(val) for val in statistiche['Peggiore risultato (%)']], index = statistiche.index)
statistiche['Migliore risultato(%)'] = pd.Series(["{0:.2f}%".format(val) for val in statistiche['Migliore risultato(%)']], index = statistiche.index)

statistiche = statistiche.transpose()

statistiche


# st.write("""
# ## Cono di volatilità:
#  """)


av = media/mesi_proiezione

dev = varianza/mesi_proiezione


cono = pd.DataFrame(index=range(mesi_proiezione+1))
cono['rendimento_medio']= av*cono.index
cono['volatilità'] = dev*(cono.index**(1/2))
cono['volatilità2'] = dev*2*(cono.index**(1/2))
cono['worst (1 deviazione)']= cono.rendimento_medio-cono.volatilità
cono['best (1 deviazione)']= cono.rendimento_medio+cono.volatilità
cono['worst(2 deviazioni)']= cono.rendimento_medio-cono.volatilità2
cono['best(2 deviazione)']= cono.rendimento_medio+cono.volatilità2

cono['index'] = cono.index
cono = cono.set_index('index',1)

# if st.checkbox('Mostra il cono di volatilità'):

#     st.line_chart(cono.drop(['volatilità','volatilità2'],1))
import matplotlib.pyplot as plt
fig = plt.hist(df1.return_log, density=True, color = "red", histtype = 'step')
fig = plt.hist(df2.return_log, density = True, histtype = 'bar')

st.pyplot(fig)

st.write("""
#  
 """)
st.write("""
## DISCLAIMER:
 """)
st.write("""
Il contenuto del presente report non costituisce e non può in alcun modo essere interpretato come consulenza finanziaria, né come invito ad acquistare, vendere o detenere strumenti finanziari.
Le analisi esposte sono da interpretare come supporto di analisi statistico-quantitativa e sono completamente automatizzate: tutte le indicazioni sono espressione di algoritmi matematici applicati su dati storici.
Sebbene tali metodologie rappresentino modelli ampiamente testati e calcolati su una base dati ottenuta da fonti attendibili e verificabili non forniscono alcuna garanzia di profitto.
In nessun caso il contenuto del presente report può essere considerato come sollecitazione all’ investimento. Si declina qualsiasi responsabilità legata all'utilizzo improprio di questa applicazione.
I contenuti sono di proprietà di **Fabrizio Monge** e sia la divulgazione, come la riproduzione totale o parziale sono riservati ai sottoscrittori del servizio.
 """)
