let map;
let drawingManager;
let currentPolygon;

// Mapa
function initMap() {
    // Declaración. Centrado en México
    map = new google.maps.Map(document.getElementById('map'), {
        center: { lat: 23.634501, lng: -102.552784 },
        zoom: 6,
        mapTypeId: 'satellite'
    });

    // Herramienta de dibujado
    drawingManager = new google.maps.drawing.DrawingManager({
        drawingMode: google.maps.drawing.OverlayType.POLYGON,
        drawingControl: true,
        drawingControlOptions: {
            position: google.maps.ControlPosition.TOP_CENTER,
            drawingModes: ['polygon']
        }
    });

    drawingManager.setMap(map);

    // Trazado de polígonos
    google.maps.event.addListener(drawingManager, 'overlaycomplete', function (event) {
        if (event.type == google.maps.drawing.OverlayType.POLYGON) {
            if (currentPolygon) {
                currentPolygon.setMap(null); // Borrar el polígono anterior
            }
            currentPolygon = event.overlay;
            
            let vertices = currentPolygon.getPath().getArray().map(coord => ({
                lat: coord.lat(),
                lng: coord.lng()
            }));

            let zoom = map.getZoom()

            fetch('/process_polygon', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ vertices: vertices, zoom: zoom})
            })
                .then(response => response.json())
                .then(data => {
                    console.log('Número de vértices:', data.num_vertices);
                });

            // Habilitar el botón "Calcular"
            document.getElementById('calcular').disabled = false;
        }
    });

    document.getElementById('borrar').addEventListener('click', function () {
        if (currentPolygon) {
            currentPolygon.setMap(null);
            currentPolygon = null;

            // Deshabilitar el botón "Calcular"
            document.getElementById('calcular').disabled = true;
        }
    });

    document.getElementById('calcular').addEventListener('click', function () {
        if (currentPolygon) {
            let vertices = currentPolygon.getPath().getArray().map(coord => ({
                lat: coord.lat(),
                lng: coord.lng()
            }));

            sessionStorage.setItem('polygonVertices', JSON.stringify(vertices));
            window.location.href = '/results';
        } else {
            alert('Por favor, dibuja un polígono primero.');
        }
    });

    
}

window.onload = initMap;

