from flask import Flask, render_template, request, jsonify
import propios

app = Flask(__name__)

riesgo_sequia = 'hola'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_polygon', methods=['POST'])
def process_polygon():
    data = request.json
    vertices = data['vertices']
    zoom = data['zoom']

    centroide = propios.centroid(vertices)
    location = propios.getCity(centroide)
    
    propios.getSatelliteImg(centroide, zoom)

    address = location.raw['address']

    print(address)

    serie, preci = propios.SerieTiempo(location)

    if serie['maximo']>=2:
        riesgo_sequia = 'Existe riesgo de sequia inminente en esta zona en los proximos seis meses.'
    else:
        riesgo_sequia = 'No hay riesgo de sequia en esta zona en los proximos seis meses.'
    
    area = propios.deteccionTechos(centroide['lat'], zoom)

    # Fórmula de cálculo de aprovechamiento
    futuro = (area*0.75)*float(preci['futuro'])*0.2

    guardados = [serie['actual'], serie['maximo'], riesgo_sequia, area, preci['presente'], futuro]
    print(guardados)
    propios.saveRes(guardados)

    return jsonify({'ciudad': address.get('city', '')})


@app.route('/results')
def results():
    vars = propios.readRes()
    #print(vars)
    return render_template('results.html', vars = vars)



app.run(host='localhost', port=5000, debug=True)