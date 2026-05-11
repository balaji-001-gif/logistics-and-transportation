/**
 * route_map.js
 * ─────────────────────────────────────────────────────────────────────────────
 * Reusable Google Maps panel for Freight Order and Trip Sheet forms.
 *
 * Usage (from freight_order.js / trip_sheet.js):
 *   window.LogisticsRouteMap.render(frm, { origin: "Mumbai", destination: "Pune" });
 *
 * Requires:
 *   - Google Maps API key configured in Logistics Settings
 *   - The API key is fetched server-side to keep it out of the client bundle
 * ─────────────────────────────────────────────────────────────────────────────
 */

window.LogisticsRouteMap = (function () {

    let _mapApiKey  = null;
    let _initialized = false;

    // ── Fetch Maps API key once from backend ──────────────────────────────
    function _getApiKey() {
        return new Promise((resolve) => {
            if (_mapApiKey !== null) { resolve(_mapApiKey); return; }
            frappe.call({
                method: "logistics_transport_erp.api.maps_api.get_maps_api_key",
                callback(r) {
                    _mapApiKey = (r.message && r.message.api_key) ? r.message.api_key : "";
                    resolve(_mapApiKey);
                }
            });
        });
    }

    // ── Inject Google Maps script tag once ───────────────────────────────
    function _loadGoogleMapsScript(apiKey) {
        return new Promise((resolve, reject) => {
            if (_initialized || window.google?.maps) { resolve(); return; }
            if (!apiKey) { reject("Google Maps API key not configured."); return; }
            const script   = document.createElement("script");
            script.src     = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=geometry,places`;
            script.async   = true;
            script.defer   = true;
            script.onload  = () => { _initialized = true; resolve(); };
            script.onerror = () => reject("Failed to load Google Maps API.");
            document.head.appendChild(script);
        });
    }

    // ── Build or refresh the map panel in a form ──────────────────────────
    async function render(frm, opts) {
        /**
         * opts = {
         *   origin:       string (city name or "lat,lng"),
         *   destination:  string,
         *   trackingPins: [{ lat, lng, label, event_type }]  // optional
         * }
         */
        const { origin, destination, trackingPins = [] } = opts || {};
        if (!origin || !destination) return;

        // Container element (appended once per form)
        let container = frm.fields_dict.__route_map_panel__;
        if (!container) {
            const html = `
                <div id="lt-route-map-${frm.doctype.replace(/\s/g,'')}" 
                     style="width:100%;height:380px;border-radius:8px;overflow:hidden;
                            border:1px solid var(--border-color);margin-top:12px;">
                </div>`;
            frm.set_df_property("route_map_html", "options", html);
        }

        try {
            const apiKey = await _getApiKey();
            await _loadGoogleMapsScript(apiKey);
        } catch (err) {
            console.warn("[LogisticsRouteMap]", err);
            return;
        }

        const mapId = `lt-route-map-${frm.doctype.replace(/\s/g, "")}`;
        const el    = document.getElementById(mapId);
        if (!el) return;

        const map = new google.maps.Map(el, {
            zoom:               8,
            mapTypeControl:     false,
            streetViewControl:  false,
            fullscreenControl:  true,
            styles: [
                { featureType: "poi", stylers: [{ visibility: "off" }] },
                { elementType: "geometry",   stylers: [{ color: "#1a1a2e" }] },
                { elementType: "labels.text.fill",   stylers: [{ color: "#9ca3af" }] },
                { featureType: "road",       stylers: [{ color: "#2d2d44" }] },
                { featureType: "water",      stylers: [{ color: "#0f3460" }] },
            ]
        });

        const directionsService  = new google.maps.DirectionsService();
        const directionsRenderer = new google.maps.DirectionsRenderer({
            map,
            suppressMarkers: false,
            polylineOptions: { strokeColor: "#6366f1", strokeWeight: 4 }
        });

        directionsService.route(
            {
                origin,
                destination,
                travelMode: google.maps.TravelMode.DRIVING,
            },
            (result, status) => {
                if (status === "OK") {
                    directionsRenderer.setDirections(result);
                } else {
                    console.warn("[LogisticsRouteMap] Directions failed:", status);
                }
            }
        );

        // ── Tracking event pins ───────────────────────────────────────────
        const colours = {
            "Dispatched":        "#10b981",
            "In Transit":        "#3b82f6",
            "At Hub":            "#f59e0b",
            "Out for Delivery":  "#8b5cf6",
            "Delivered":         "#6ee7b7",
        };

        trackingPins.forEach(pin => {
            if (!pin.lat || !pin.lng) return;
            new google.maps.Marker({
                position: { lat: parseFloat(pin.lat), lng: parseFloat(pin.lng) },
                map,
                title:  pin.label || pin.event_type || "Tracking Event",
                icon: {
                    path:         google.maps.SymbolPath.CIRCLE,
                    fillColor:    colours[pin.event_type] || "#6366f1",
                    fillOpacity:  1,
                    strokeWeight: 2,
                    strokeColor:  "#fff",
                    scale:        9,
                }
            });
        });
    }

    return { render };

})();
