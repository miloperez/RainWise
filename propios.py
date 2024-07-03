from geopy.geocoders import Nominatim
import urllib.request
import numpy as np
import pandas as pd
import plotly.express as px
import cv2
from ultralytics import YOLO
import plotly.graph_objects as go
from datetime import date
import math


def centroid(polygon):
    sum_lat = 0
    sum_lng = 0
    
    for p in polygon:
        sum_lat = sum_lat + p['lat']
        sum_lng = sum_lng + p['lng']
    
    sum_lat = sum_lat/len(polygon)
    sum_lng = sum_lng/len(polygon)

    point = {
        "lat": sum_lat,
        "lng": sum_lng
        }
    return point

def getCity(point):
    geolocator = Nominatim(user_agent="tlaloc")
    location = geolocator.reverse(str(point['lat'])+","+str(point['lng']))
    return location

def getSatelliteImg(centro, zoom):
  
    lat = str(centro['lat'])
    lng = str(centro['lng'])
    
    if zoom < 14:
        zoom = str(14)
    else:
        zoom = str(zoom)

    size = '640x640'

    url = 'https://maps.googleapis.com/maps/api/staticmap?center=' + lat + ','+ lng +'&zoom='+ zoom +'&size=' + size +'&maptype=satellite&key=API_KEY'
    save_as = 'static/img.jpg'

    urllib.request.urlretrieve(url, save_as)


def SerieTiempo(dir):
    data = pd.read_csv('Res_pred_sequia.csv')

    address = dir.raw['address']
    if address.get('city'):
        city = address.get('city', '')
    else:
        city = address.get('county', '')

    city_title = city
    
    if city not in np.array(data['Municipio']):
        city_title = city
        city = address.get('state', '')

        actual = data[data['Estado'] == city]['Actual']
        arr = np.array(data[data['Estado'] == city].drop(['Municipio','Estado','Actual'],axis=1))[0]
    else:
        actual = data[data['Municipio'] == city]['Actual']
        arr = np.array(data[data['Municipio'] == city].drop(['Municipio','Estado','Actual'],axis=1))[0]

    n = arr.size
    dic = {'D0': 0,'D1': 1,'D2': 2,'D3': 3,'D4': 4}

    actual = np.array(actual)[0]
    actual = dic[actual]

    Y = np.zeros(n)
    i = 0
    
    for a in arr:
        Y[i] = dic[a]; i+=1
    
    X = np.array(range(n))
    mayor = max(Y)

    df = pd.DataFrame(Y,X)
    df.columns = ['Tipo de Sequía']

    fig = px.line(df,title = city_title)
    fig.update_layout(legend_title = 'Gravedad 0 a 4',
                    yaxis_title = 'Gravedad de sequía',
                    xaxis_title = 'Tiempo en meses',
                    legend=dict(orientation="h"),
                    yaxis_range = [0,4])
    
    fig.write_image('static/pred_nivel_seq.jpg')

    res = {
        'actual' : actual,
        'maximo' : mayor
    }

    return res, precip(address.get('state', ''))

def deteccionTechos(lat, zoom):

    dir = 'static/img.jpg'
    img = cv2.imread(dir)

    model = YOLO('static/RoofModel.pt')
    results = model.predict(img)[0]

    Area = 0
    if results[0].boxes.xyxy is not None:
        #pixeles a m
        escala = 156543.03392 * math.cos(lat * math.pi / 180) / math.pow(2, zoom)

        for box in results[0].boxes.xyxy:
            R = np.array(box).astype(int)
        Area += (abs(R[2]-R[0])*abs(R[3]-R[1]))
        Area = Area*(escala**2) #Escala/Conversion a m2


        res = results.plot()
        cv2.imwrite("static/areas_potenciales.jpg",res)
    
    return Area
    
def saveRes(vars):
    file = open("info.txt","w+")
    for i in vars:
        file.writelines(str(i) + "\n")

    file.close()


def readRes():
    lineas = []
    file = open('info.txt', 'r')

    while True:
        # Get next line from file
        line = file.readline()
        # if line is empty
        # end of file is reached
        if not line:
            file.close()
            return lineas
        else:
            lineas.append(line.strip())


def precip(estado):
    # lectura de archivo
    df = pd.read_csv('precipitaciones.csv')

    # Conservar registros del estado de interés
    df.drop(df[df['Estado'] != estado].index, inplace=True)
    df.drop(df[df['Indice'] <420].index, inplace=True)

    # Eliminar columnas de ubicación de datos
    df.drop('Estado', axis=1, inplace=True)
    df.drop('Indice', axis=1, inplace=True)

    # Separar entre datos históricos y predicciones
    today = date.today()

    hist = df[df['Fecha'] < str(today)]
    pred = df[df['Fecha'] > str(today)]

    fig = go.Figure()

    # Agregar la serie histórica
    fig.add_trace(go.Scatter(x=hist['Fecha'], y=hist['MM/D'], mode='lines', name='Histórico'))

    # Agregar el pronóstico
    fig.add_trace(go.Scatter(x=pred['Fecha'], y=pred['MM/D'], mode='lines', name='Pronóstico', line=dict(color='red')))

    # Configurar el diseño del gráfico
    fig.update_layout(
        title='Forecast de Precipitación en '+ estado,
        xaxis_title='Fecha',
        yaxis_title='Precipitación (mm)',
        showlegend=True,
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=True),
        plot_bgcolor='white'
    )
    
    fig.write_image("static/pred_precip.png")

    res = {
        "presente" : (hist.iloc[len(hist)-1])['MM/D'],
        "futuro" : sum((pred['MM/D'])[:6])
    }

    return res
