document.addEventListener("DOMContentLoaded", () => {

    // =========================================================
    // MEGHDRISHTI DASHBOARD APPLICATION
    // =========================================================

    const state = {

        me: null,

        panchayat: null,

        weather: null,

        forecast: [],

        aiPrediction: null,

        risk: null,

        riskMap: null,

        riskMapMarkers: [],
        intelligenceRequest: 0

    };


    // =========================================================
    // DOM HELPER
    // =========================================================

    const $ = (id) => {

        return document.getElementById(id);

    };


    // =========================================================
    // TEXT HELPER
    // =========================================================

    function setText(id, value) {

        const element =
            $(id);

        if (!element) {
            return;
        }


        const nextValue =
            value !== null &&
            value !== undefined
                ? String(value)
                : "--";


        const currentValue =
            element.textContent;


        if (
            currentValue ===
            nextValue
        ) {
            return;
        }


        element.classList.remove(
            "md-output-transition"
        );


        void element.offsetWidth;


        element.textContent =
            nextValue;


        element.classList.add(
            "md-output-transition"
        );
    }


    // =========================================================
    // ERROR WINDOW
    // =========================================================

    function showError(message) {

        const box =
            $("errorWindow");

        const text =
            $("errorMessage");


        if (text) {

            text.textContent =
                message ||
                "Unable to load data.";
        }


        if (box) {

            box.hidden =
                false;
        }
    }


    function hideError() {

        const box =
            $("errorWindow");


        if (box) {

            box.hidden =
                true;
        }
    }


    // =========================================================
    // CONNECTION STATUS
    // =========================================================

    function setConnection(online) {

        const text =
            $("connectionStatus");

        const dot =
            $("connectionDot");


        if (text) {

            text.textContent =
                online
                    ? "Connected"
                    : "Offline";
        }


        if (!dot) {
            return;
        }


        if (online) {

            dot.style.background =
                "#91a96b";

            dot.style.boxShadow =
                "0 0 0 4px rgba(145,169,107,.13)";

        } else {

            dot.style.background =
                "#a85e50";

            dot.style.boxShadow =
                "0 0 0 4px rgba(168,94,80,.13)";
        }
    }


    // =========================================================
    // API REQUEST HELPER
    // =========================================================

    async function api(url) {

        const response =
            await fetch(
                url,
                {
                    method:
                        "GET",

                    credentials:
                        "same-origin",

                    headers: {
                        "Accept":
                            "application/json"
                    }
                }
            );


        let data = {};


        try {

            data =
                await response.json();

        }
        catch (error) {

            data = {};
        }


        if (!response.ok) {

            throw new Error(
                data.error ||
                data.details ||
                `Request failed (${response.status})`
            );
        }


        return data;
    }


    // =========================================================
    // WEATHER DESCRIPTION
    // =========================================================

    function weatherDescription(code) {

        const c =
            Number(code);


        if (c === 0) {
            return "Clear sky";
        }


        if (
            [1, 2, 3].includes(c)
        ) {
            return "Partly cloudy";
        }


        if (
            [45, 48].includes(c)
        ) {
            return "Fog";
        }


        if (
            [51, 53, 55, 56, 57].includes(c)
        ) {
            return "Drizzle";
        }


        if (
            [61, 63, 65, 66, 67].includes(c)
        ) {
            return "Rain";
        }


        if (
            [71, 73, 75, 77].includes(c)
        ) {
            return "Snow";
        }


        if (
            [80, 81, 82].includes(c)
        ) {
            return "Rain showers";
        }


        if (
            [85, 86].includes(c)
        ) {
            return "Snow showers";
        }


        if (
            [95, 96, 99].includes(c)
        ) {
            return "Thunderstorm";
        }


        return "Weather conditions";
    }


    // =========================================================
    // WEATHER ICON
    // =========================================================

    function weatherIcon(code) {

        const c =
            Number(code);


        if (c === 0) {
            return "☀";
        }


        if (
            [1, 2].includes(c)
        ) {
            return "⛅";
        }


        if (c === 3) {
            return "☁";
        }


        if (
            [45, 48].includes(c)
        ) {
            return "≋";
        }


        if (
            [51, 53, 55, 56, 57].includes(c)
        ) {
            return "☂";
        }


        if (
            [61, 63, 65, 66, 67].includes(c)
        ) {
            return "☂";
        }


        if (
            [80, 81, 82].includes(c)
        ) {
            return "☂";
        }


        if (
            [95, 96, 99].includes(c)
        ) {
            return "ϟ";
        }


        return "☁";
    }


    // =========================================================
    // DATE FORMATTER
    // =========================================================

    function formatDate(value) {

        if (!value) {
            return "--";
        }


        const date =
            new Date(value);


        if (
            Number.isNaN(
                date.getTime()
            )
        ) {

            return String(value)
                .replace(
                    "T",
                    " "
                );
        }


        return date.toLocaleString(
            "en-IN",
            {
                day:
                    "2-digit",

                month:
                    "short",

                year:
                    "numeric",

                hour:
                    "2-digit",

                minute:
                    "2-digit",

                hour12:
                    true
            }
        );
    }


    // =========================================================
    // RENDER PANCHAYAT
    // =========================================================

    function renderPanchayat() {

        const p =
            state.panchayat;


        if (!p) {
            return;
        }


        setText(
            "overviewPanchayat",
            p.name
        );


        setText(
            "weatherPanchayat",
            p.name
        );


        setText(
            "locationPanchayat",
            p.name
        );


        setText(
            "locationPanchayatDetail",
            p.name
        );


        setText(
            "mapPanchayat",
            p.name
        );


        setText(
            "aiPanchayat",
            p.name
        );


        const latitude =
            Number(
                p.latitude
            );

        const longitude =
            Number(
                p.longitude
            );


        if (
            Number.isFinite(latitude) &&
            Number.isFinite(longitude)
        ) {

            const coordinates =
                `${latitude.toFixed(4)}, ` +
                `${longitude.toFixed(4)}`;


            setText(
                "overviewCoordinates",
                coordinates
            );


            setText(
                "mapCoordinates",
                coordinates
            );


            setText(
                "locationMapCoordinates",

                `Lat ${latitude.toFixed(4)} • ` +
                `Lon ${longitude.toFixed(4)}`
            );
        }
    }


    // =========================================================
    // RENDER CURRENT WEATHER
    // =========================================================

    function renderWeather() {

        const w =
            state.weather;


        if (!w) {
            return;
        }


        const temperature =
            Number(
                w.temperature_c
            );


        const feelsLike =
            Number(
                w.feels_like_c
            );


        const humidity =
            Number(
                w.humidity_percent
            );


        const rainfall =
            Number(
                w.rainfall_mm ??
                w.precipitation_mm
            );


        const wind =
            Number(
                w.wind_speed_kmh
            );


        const pressure =
            Number(
                w.pressure_hpa
            );


        const condition =
            weatherDescription(
                w.weather_code
            );


        // ---------------------------------------------------------
        // TEMPERATURE
        // ---------------------------------------------------------

        setText(
            "weatherTemperature",

            Number.isFinite(
                temperature
            )
                ? `${temperature.toFixed(1)}°`
                : "--°"
        );


        setText(
            "overviewTemperature",

            Number.isFinite(
                temperature
            )
                ? `${temperature.toFixed(1)}°C`
                : "--°C"
        );


        // ---------------------------------------------------------
        // CONDITION
        // ---------------------------------------------------------

        setText(
            "weatherCondition",
            condition
        );


        setText(
            "overviewCondition",
            condition
        );


        // ---------------------------------------------------------
        // ICON
        // ---------------------------------------------------------

        setText(
            "weatherIcon",

            weatherIcon(
                w.weather_code
            )
        );


        // ---------------------------------------------------------
        // FEELS LIKE
        // ---------------------------------------------------------

        setText(
            "feelsLike",

            Number.isFinite(
                feelsLike
            )
                ? `${feelsLike.toFixed(1)}°C`
                : "--°C"
        );


        // ---------------------------------------------------------
        // HUMIDITY
        // ---------------------------------------------------------

        setText(
            "humidity",

            Number.isFinite(
                humidity
            )
                ? `${humidity.toFixed(0)}%`
                : "--%"
        );


        setText(
            "overviewHumidity",

            Number.isFinite(
                humidity
            )
                ? `${humidity.toFixed(0)}%`
                : "--%"
        );


        // ---------------------------------------------------------
        // RAINFALL
        // ---------------------------------------------------------

        setText(
            "rainfall",

            Number.isFinite(
                rainfall
            )
                ? `${rainfall.toFixed(1)} mm`
                : "-- mm"
        );


        setText(
            "overviewRainfall",

            Number.isFinite(
                rainfall
            )
                ? `${rainfall.toFixed(1)} mm`
                : "-- mm"
        );


        // ---------------------------------------------------------
        // WIND
        // ---------------------------------------------------------

        setText(
            "wind",

            Number.isFinite(
                wind
            )
                ? `${wind.toFixed(1)} km/h`
                : "-- km/h"
        );


        // ---------------------------------------------------------
        // PRESSURE
        // ---------------------------------------------------------

        setText(
            "pressure",

            Number.isFinite(
                pressure
            )
                ? `${pressure.toFixed(0)} hPa`
                : "-- hPa"
        );


        // ---------------------------------------------------------
        // SOURCE
        // ---------------------------------------------------------

        setText(
            "weatherSource",

            w.source ||
            "Open-Meteo"
        );


        setText(
            "weatherDataType",

            w.data_type ||
            "LIVE"
        );


        // ---------------------------------------------------------
        // UPDATED
        // ---------------------------------------------------------

        if (w.observed_at) {

            setText(
                "weatherUpdated",

                `Updated ${formatDate(
                    w.observed_at
                )}`
            );
        }


        setConnection(
            true
        );
    }


    // =========================================================
    // RENDER FORECAST
    // =========================================================

    function renderForecast() {

        const grid =
            $("forecastGrid");


        if (!grid) {
            return;
        }


        if (
            !Array.isArray(
                state.forecast
            ) ||
            state.forecast.length === 0
        ) {

            grid.innerHTML = `
                <div class="md-loading-card">
                    No forecast records returned.
                </div>
            `;

            return;
        }


        const items =
            state.forecast.slice(
                0,
                12
            );


        grid.innerHTML =
            items
                .map(
                    item => {

                        const temperature =
                            Number(
                                item.temperature_c
                            );


                        const probability =
                            Number(
                                item.precipitation_probability
                            );


                        const rain =
                            Number(
                                item.rain_mm ??
                                item.precipitation_mm
                            );


                        return `
                            <article
                                class="md-forecast-card"
                            >

                                <div
                                    class="md-forecast-time"
                                >
                                    ${formatDate(
                                        item.forecast_time
                                    )}
                                </div>


                                <div
                                    class="md-forecast-temp"
                                >
                                    ${
                                        Number.isFinite(
                                            temperature
                                        )
                                            ? `${temperature.toFixed(1)}°C`
                                            : "--"
                                    }
                                </div>


                                <div
                                    style="
                                        font-size:1.35rem;
                                    "
                                >

                                    ${weatherIcon(
                                        item.weather_code
                                    )}

                                    <span
                                        style="
                                            font-size:.70rem;
                                            color:
                                            rgba(
                                                245,
                                                237,
                                                226,
                                                .60
                                            );
                                            margin-left:5px;
                                        "
                                    >
                                        ${weatherDescription(
                                            item.weather_code
                                        )}
                                    </span>

                                </div>


                                <div
                                    class="md-forecast-meta"
                                >

                                    <span>
                                        Rain ${
                                            Number.isFinite(
                                                rain
                                            )
                                                ? rain.toFixed(1)
                                                : "--"
                                        } mm
                                    </span>


                                    <span>
                                        ${
                                            Number.isFinite(
                                                probability
                                            )
                                                ? probability.toFixed(0)
                                                : "--"
                                        }%
                                    </span>

                                </div>

                            </article>
                        `;
                    }
                )
                .join("");
    }


    // =========================================================
    // LOAD WEATHER FOR PANCHAYAT
    // =========================================================

    async function loadWeatherForPanchayat(
        panchayatId
    ) {

        if (!panchayatId) {
            return;
        }


        hideError();


        try {

            const [
                weatherResponse,
                forecastResponse
            ] =
                await Promise.all(
                    [

                        api(
                            `/api/weather/panchayat/${panchayatId}`
                        ),

                        api(
                            `/api/weather/panchayat/${panchayatId}/forecast`
                        )

                    ]
                );


            state.weather =
                weatherResponse.weather;


            state.forecast =
                forecastResponse.forecast ||
                [];


            renderWeather();

            renderForecast();


            setText(
                "overviewStatus",
                "LIVE WEATHER"
            );


            setConnection(
                true
            );
        }


        catch (error) {

            console.error(
                "Weather loading error:",
                error
            );


            setConnection(
                false
            );


            showError(
                error.message
            );
        }
    }


    // =========================================================
    // RISK ASSESSMENT
    // =========================================================

    function riskClass(level) {
        return `md-risk-${String(level || "none").toLowerCase()}`;
    }


    function resetRisk() {

        state.risk = null;

        setText("riskScore", "--");
        setText("riskLevelText", "NO RISK DATA");
        setText("riskPanchayat", state.panchayat?.name || "Select Panchayat");
        setText("riskTargetTime", "Generate an AI prediction first.");
        setText("riskRainfallComponent", "--");
        setText("riskWindComponent", "--");
        setText("riskHumidityComponent", "--");
        setText("riskFloodComponent", "--");

        const pill = $("riskLevelPill");
        const ring = $("riskScoreRing");
        if (pill) pill.className = "md-risk-pill md-risk-none";
        if (ring) ring.className = "md-risk-score-ring md-risk-none";
    }


    function renderRisk(payload) {

        const risk = payload?.risk;
        const prediction = payload?.prediction;

        if (!risk) {
            resetRisk();
            return;
        }

        state.risk = payload;

        const level = String(risk.level || "NONE").toLowerCase();
        const cls = riskClass(risk.level);
        const pill = $("riskLevelPill");
        const ring = $("riskScoreRing");

        if (pill) pill.className = `md-risk-pill ${cls}`;
        if (ring) ring.className = `md-risk-score-ring ${cls}`;

        setText("riskScore", Number(risk.score).toFixed(1));
        setText("riskLevelText", `${risk.level} • ${risk.label}`);
        setText("roleRiskSummary", risk.level || "NO RISK DATA");
        setText("riskPanchayat", payload.panchayat?.name || state.panchayat?.name || "Panchayat");
        setText("riskTargetTime", prediction?.target_time ? `Based on target: ${formatDate(prediction.target_time)}` : "Latest modelled prediction");

        const components = risk.components || {};
        setText("riskRainfallComponent", `${components.rainfall?.value ?? "--"} mm`);
        setText("riskWindComponent", `${components.wind?.value ?? "--"} km/h`);
        setText("riskHumidityComponent", `${components.humidity?.value ?? "--"}%`);
        setText("riskFloodComponent", components.flood_susceptibility?.value != null ? `${(components.flood_susceptibility.value * 100).toFixed(0)}%` : "--");

        const explanation = $("riskExplanation");
        if (explanation) {
            const reasons = (risk.explanation || []).map(item => `<li>${item}</li>`).join("");
            explanation.innerHTML = `
                <strong>Why this risk level?</strong>
                <p>${risk.method || "Rule-based weighted hazard screening index"}</p>
                <ul>${reasons}</ul>
            `;
        }
    }


    async function loadRiskForPanchayat(panchayatId) {

        if (!panchayatId) {
            resetRisk();
            return null;
        }

        try {
            const payload = await api(`/api/risk/panchayat/${panchayatId}`);
            renderRisk(payload);
            setText("alertSelectedArea", state.panchayat?.name || "--");
            setText("alertSelectedRisk", payload?.risk?.level ? `${payload.risk.level} screening level` : "No screening risk data");
            return payload;
        } catch (error) {
            console.error("Risk loading error:", error);
            resetRisk();
            setText("riskTargetTime", error.message || "Risk assessment unavailable.");
            return null;
        }
    }


    function markerColor(level) {
        const colors = {
            GREEN: "#91a96b",
            YELLOW: "#debe52",
            ORANGE: "#e28b44",
            RED: "#ba534c"
        };
        return colors[level] || "#8f8a86";
    }


    function createRiskMarker(item) {
        const p = item.panchayat || {};
        const risk = item.risk;
        const level = risk?.level || "NONE";
        const score = risk?.score != null ? Number(risk.score).toFixed(1) : "--";
        const color = markerColor(level);

        const marker = L.circleMarker(
            [Number(p.latitude), Number(p.longitude)],
            {
                radius: 10,
                color: "#fffaf5",
                weight: 2,
                fillColor: color,
                fillOpacity: .9
            }
        );

        marker.bindPopup(`
            <div class="md-risk-popup">
                <h4>${p.name || "Panchayat"}</h4>
                <span class="risk-badge" style="background:${color};color:#fff">${level}</span>
                <p><strong>Risk score:</strong> ${score}/100</p>
                <p>${risk?.label || "Prediction required"}</p>
                <button type="button" data-map-panchayat="${p.id}">View risk details</button>
            </div>
        `);

        marker.on("popupopen", event => {
            const button = event.popup.getElement()?.querySelector("[data-map-panchayat]");
            if (button) {
                button.addEventListener("click", async () => {
                    const selected = Number(button.dataset.mapPanchayat);
                    const candidate = {
                        id: selected,
                        name: p.name,
                        latitude: Number(p.latitude),
                        longitude: Number(p.longitude)
                    };
                    await loadSelectedPanchayatIntelligence(candidate);
                    document.querySelector('[data-target="risk-map"]')?.click();
                });
            }
        });

        return marker;
    }


    async function loadRiskMap() {

        const mapElement = $("panchayatRiskMap");
        if (!mapElement || typeof L === "undefined") return;

        if (!state.riskMap) {
            state.riskMap = L.map(mapElement, { zoomControl: true }).setView([19.0, 73.0], 6);
            L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
                maxZoom: 18,
                attribution: '&copy; OpenStreetMap contributors'
            }).addTo(state.riskMap);
        }

        state.riskMapMarkers.forEach(marker => marker.remove());
        state.riskMapMarkers = [];

        try {
            const data = await api("/api/risk/overview");
            const valid = (data.panchayats || []).filter(item =>
                Number.isFinite(Number(item.panchayat?.latitude)) &&
                Number.isFinite(Number(item.panchayat?.longitude))
            );

            const bounds = [];
            valid.forEach(item => {
                const marker = createRiskMarker(item);
                marker.addTo(state.riskMap);
                state.riskMapMarkers.push(marker);
                bounds.push([Number(item.panchayat.latitude), Number(item.panchayat.longitude)]);
            });

            if (bounds.length) {
                state.riskMap.fitBounds(bounds, { padding: [30, 30], maxZoom: 13 });
            }
        } catch (error) {
            console.error("Risk map loading error:", error);
        }

        setTimeout(() => state.riskMap?.invalidateSize(), 150);
    }


    function setupRiskMap() {

        const refresh = $("refreshRiskMap");
        if (refresh) {
            refresh.addEventListener("click", async () => {
                refresh.disabled = true;
                try { await loadRiskMap(); }
                finally { refresh.disabled = false; }
            });
        }

        if (typeof L !== "undefined") {
            loadRiskMap();
        } else {
            window.addEventListener("load", loadRiskMap, { once: true });
        }
    }


    // =========================================================
    // RESET AI PREDICTION
    // =========================================================

    function resetAiPrediction() {

        state.aiPrediction =
            null;


        setText(
            "aiPanchayat",

            state.panchayat?.name ||
            "Select Panchayat"
        );


        setText(
            "aiTargetTime",
            "Prediction target time"
        );


        setText(
            "aiTemperature",
            "-- °C"
        );


        setText(
            "aiRainfall",
            "-- mm"
        );


        setText(
            "aiHumidity",
            "-- %"
        );


        setText(
            "aiWind",
            "-- km/h"
        );


        setText(
            "aiModel",
            "--"
        );


        setText(
            "aiModelVersion",
            "--"
        );


        setText(
            "aiDataType",
            "MODELLED_PREDICTION"
        );


        setText(
            "aiSource",
            "MEGHDRISHTI AI"
        );


        setText(
            "aiPredictionStatus",
            "MODEL READY"
        );


        const loading =
            $("aiPredictionLoading");


        const error =
            $("aiPredictionError");


        const results =
            $("aiPredictionResults");


        if (loading) {

            loading.hidden =
                true;
        }


        if (error) {

            error.hidden =
                true;
        }


        if (results) {

            results.hidden =
                false;
        }


        const button =
            $("generateAiPrediction");


        if (button) {

            button.disabled =
                false;

            button.classList.remove(
                "is-loading"
            );


            const content =
                button.querySelector(
                    ".md-ai-button-content"
                );


            const arrow =
                button.querySelector(
                    ".md-ai-button-arrow"
                );


            if (content) {

                content.innerHTML = `
                    <strong>
                        Run AI Downscaling
                    </strong>
                `;
            }


            if (arrow) {

                arrow.textContent =
                    "→";
            }
        }
    }


    // =========================================================
    // GENERATE AI PREDICTION
    // =========================================================

    async function generateAiPrediction(expectedPanchayatId = null) {

        if (
            !state.panchayat ||
            !state.panchayat.id
        ) {

            const errorBox =
                $("aiPredictionError");

            const errorMessage =
                $("aiPredictionErrorMessage");


            if (errorMessage) {

                errorMessage.textContent =
                    "Please select a Panchayat first.";
            }


            if (errorBox) {

                errorBox.hidden =
                    false;
            }


            return;
        }


        const panchayatId =
            state.panchayat.id;


        const button =
            $("generateAiPrediction");


        const loading =
            $("aiPredictionLoading");


        const errorBox =
            $("aiPredictionError");


        const errorMessage =
            $("aiPredictionErrorMessage");


        const buttonContent =
            button?.querySelector(
                ".md-ai-button-content"
            );


        const buttonArrow =
            button?.querySelector(
                ".md-ai-button-arrow"
            );


        // ---------------------------------------------------------
        // START UI
        // ---------------------------------------------------------

        if (button) {

            button.disabled =
                true;


            button.classList.add(
                "is-loading"
            );
        }


        if (buttonContent) {

            buttonContent.innerHTML = `
                <strong>
                    Processing Panchayat weather
                </strong>
            `;
        }


        if (buttonArrow) {

            buttonArrow.textContent =
                "⋯";
        }


        if (loading) {

            loading.hidden =
                false;
        }


        if (errorBox) {

            errorBox.hidden =
                true;
        }


        setText(
            "aiPredictionStatus",
            "RUNNING MODEL"
        );


        try {

            // -----------------------------------------------------
            // AI PREDICTION API
            // -----------------------------------------------------

            const response =
                await fetch(
                    `/api/ai/panchayat/${panchayatId}/predict`,
                    {
                        method:
                            "POST",

                        credentials:
                            "same-origin",

                        headers: {

                            "Accept":
                                "application/json",

                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify({})
                    }
                );


            let data = {};


            try {

                data =
                    await response.json();

            }
            catch (jsonError) {

                data = {};
            }


            if (!response.ok) {

                throw new Error(
                    data.error ||
                    data.details ||
                    `AI request failed (${response.status})`
                );
            }


            if (
                data.success === false
            ) {

                throw new Error(
                    data.error ||
                    data.details ||
                    "AI prediction failed."
                );
            }


            const prediction =
                data.prediction ||
                data;


            if (!prediction) {

                throw new Error(
                    "AI prediction response was empty."
                );
            }


            if (expectedPanchayatId && Number(state.panchayat?.id) !== Number(expectedPanchayatId)) {
                return null;
            }

            state.aiPrediction =
                prediction;

            updateLiveIntelligenceSnapshot();


            // -----------------------------------------------------
            // PANCHAYAT
            // -----------------------------------------------------

            setText(
                "aiPanchayat",

                state.panchayat.name
            );


            // -----------------------------------------------------
            // TEMPERATURE
            // -----------------------------------------------------

            const temperature =
                Number(
                    prediction.temperature_c ??
                    prediction.predicted_temperature_c
                );


            setText(
                "aiTemperature",

                Number.isFinite(
                    temperature
                )
                    ? `${temperature.toFixed(2)} °C`
                    : "-- °C"
            );


            // -----------------------------------------------------
            // RAINFALL
            // -----------------------------------------------------

            const rainfall =
                Number(
                    prediction.rainfall_mm ??
                    prediction.predicted_rainfall_mm
                );


            setText(
                "aiRainfall",

                Number.isFinite(
                    rainfall
                )
                    ? `${rainfall.toFixed(2)} mm`
                    : "-- mm"
            );


            // -----------------------------------------------------
            // HUMIDITY
            // -----------------------------------------------------

            const humidity =
                Number(
                    prediction.humidity_percent ??
                    prediction.predicted_humidity_percent
                );


            setText(
                "aiHumidity",

                Number.isFinite(
                    humidity
                )
                    ? `${humidity.toFixed(1)} %`
                    : "-- %"
            );


            // -----------------------------------------------------
            // WIND
            // -----------------------------------------------------

            const wind =
                Number(
                    prediction.wind_speed_kmh ??
                    prediction.predicted_wind_speed_kmh
                );


            setText(
                "aiWind",

                Number.isFinite(
                    wind
                )
                    ? `${wind.toFixed(2)} km/h`
                    : "-- km/h"
            );


            // -----------------------------------------------------
            // MODEL INFORMATION
            // -----------------------------------------------------

            setText(
                "aiModel",

                prediction.model_name ||
                data.model_name ||
                "MEGHDRISHTI MODEL"
            );


            setText(
                "aiModelVersion",

                prediction.model_version ||
                data.model_version ||
                "MEGHDRISHTI-RF"
            );


            setText(
                "aiDataType",

                prediction.data_type ||
                data.data_type ||
                "MODELLED_PREDICTION"
            );


            setText(
                "aiSource",

                prediction.source ||
                data.source ||
                "MEGHDRISHTI AI"
            );


            // -----------------------------------------------------
            // TARGET TIME
            // -----------------------------------------------------

            const targetTime =
                prediction.target_time ||
                prediction.prediction_time ||
                data.target_time;


            if (targetTime) {

                setText(
                    "aiTargetTime",

                    `Target: ${formatDate(
                        targetTime
                    )}`
                );

            } else {

                setText(
                    "aiTargetTime",
                    "Next available prediction"
                );
            }


            // -----------------------------------------------------
            // SUCCESS
            // -----------------------------------------------------

            setText(
                "aiPredictionStatus",
                "PREDICTION GENERATED"
            );

            // Immediately calculate explainable risk from the new prediction.
            if (expectedPanchayatId && Number(state.panchayat?.id) !== Number(expectedPanchayatId)) {
                return prediction;
            }

            await loadRiskForPanchayat(panchayatId);
            await loadRiskMap();
            return prediction;


            console.log(
                "MeghDrishti AI prediction:",
                prediction
            );
        }


        catch (error) {

            console.error(
                "AI prediction error:",
                error
            );


            if (errorMessage) {

                errorMessage.textContent =
                    error.message ||
                    "Unable to generate AI prediction.";
            }


            if (errorBox) {

                errorBox.hidden =
                    false;
            }


            setText(
                "aiPredictionStatus",
                "PREDICTION FAILED"
            );
        }


        finally {

            if (loading) {

                loading.hidden =
                    true;
            }


            if (button) {

                button.disabled =
                    false;


                button.classList.remove(
                    "is-loading"
                );
            }


            if (buttonContent) {

                buttonContent.innerHTML = `
                    <strong>
                        Run AI Downscaling
                    </strong>
                `;
            }


            if (buttonArrow) {

                buttonArrow.textContent =
                    "→";
            }
        }
    }


    // =========================================================
    // AI BUTTON SETUP
    // =========================================================

    function setupAiPrediction() {

        const button =
            $("generateAiPrediction");


        if (!button) {
            return;
        }


        button.addEventListener(
            "click",
            async () => {

                await generateAiPrediction();

            }
        );


        resetAiPrediction();
    }


    // =========================================================
    // SELECT HELPER
    // =========================================================

    function fillSelect(
        select,
        items,
        placeholder
    ) {

        if (!select) {
            return;
        }


        select.innerHTML =
            `<option value="">
                ${placeholder}
            </option>`;


        if (
            Array.isArray(items)
        ) {

            items.forEach(
                item => {

                    const option =
                        document.createElement(
                            "option"
                        );


                    option.value =
                        item.id;


                    option.textContent =
                        item.name;


                    select.appendChild(
                        option
                    );
                }
            );
        }


        select.disabled =
            false;
    }


    // =========================================================
    // LOAD STATES
    // =========================================================

    async function loadStates() {

        const select =
            $("stateSelect");


        if (!select) {
            return;
        }


        const states =
            await api(
                "/api/locations/states"
            );


        fillSelect(
            select,
            states,
            "Select State"
        );
    }


    // =========================================================
    // LOAD DISTRICTS
    // =========================================================

    async function loadDistricts(
        stateId
    ) {

        const district =
            $("districtSelect");


        const taluka =
            $("talukaSelect");


        const panchayat =
            $("panchayatSelect");


        if (!district) {
            return;
        }


        district.innerHTML =
            '<option value="">Select District</option>';


        district.disabled =
            true;


        if (taluka) {

            taluka.innerHTML =
                '<option value="">Select Taluka</option>';


            taluka.disabled =
                true;
        }


        if (panchayat) {

            panchayat.innerHTML =
                '<option value="">Select Panchayat</option>';


            panchayat.disabled =
                true;
        }


        if (!stateId) {
            return;
        }


        const data =
            await api(
                `/api/locations/districts/${stateId}`
            );


        fillSelect(
            district,
            data,
            "Select District"
        );
    }


    // =========================================================
    // LOAD TALUKAS
    // =========================================================

    async function loadTalukas(
        districtId
    ) {

        const taluka =
            $("talukaSelect");


        const panchayat =
            $("panchayatSelect");


        if (!taluka) {
            return;
        }


        taluka.innerHTML =
            '<option value="">Select Taluka</option>';


        taluka.disabled =
            true;


        if (panchayat) {

            panchayat.innerHTML =
                '<option value="">Select Panchayat</option>';


            panchayat.disabled =
                true;
        }


        if (!districtId) {
            return;
        }


        const data =
            await api(
                `/api/locations/talukas/${districtId}`
            );


        fillSelect(
            taluka,
            data,
            "Select Taluka"
        );
    }


    // =========================================================
    // LOAD PANCHAYATS
    // =========================================================

    async function loadPanchayats(
        talukaId
    ) {

        const select =
            $("panchayatSelect");


        if (!select) {
            return;
        }


        select.innerHTML =
            '<option value="">Select Panchayat</option>';


        select.disabled =
            true;


        if (!talukaId) {
            return;
        }


        const data =
            await api(
                `/api/locations/panchayats/${talukaId}`
            );


        fillSelect(
            select,
            data,
            "Select Panchayat"
        );
    }


    // =========================================================
    // GOVERNMENT LOCATION SELECTOR
    // =========================================================

    async function loadSelectedPanchayatIntelligence(panchayat, options = {}) {

        if (!panchayat?.id) return;

        const requestId = ++state.intelligenceRequest;
        const panchayatId = Number(panchayat.id);
        const autoAi = options.autoAi !== false;

        state.panchayat = panchayat;
        renderPanchayat();
        resetAiPrediction();
        resetRisk();
        setText("overviewStatus", "LOADING INTELLIGENCE");
        setText("overviewLocation", panchayat.name || "Selected Panchayat");
        setText("heroScope", panchayat.name || "Selected Panchayat");

        try {
            await loadWeatherForPanchayat(panchayatId);
            if (requestId !== state.intelligenceRequest || Number(state.panchayat?.id) !== panchayatId) return;

            if (autoAi) {
                await generateAiPrediction(panchayatId);
                if (requestId !== state.intelligenceRequest || Number(state.panchayat?.id) !== panchayatId) return;
            } else {
                await loadRiskForPanchayat(panchayatId);
            }

            if (requestId !== state.intelligenceRequest || Number(state.panchayat?.id) !== panchayatId) return;
            await loadRiskMap();
            setText("overviewStatus", "LIVE INTELLIGENCE");
            setSelectionStatus(`${panchayat.name || "Panchayat"} • Updated ${new Date().toLocaleTimeString([], {hour: "2-digit", minute: "2-digit"})}`, "live");
            if (state.me?.user?.role === "government") {
                setText("govSelectedArea", panchayat.name || "Selected Panchayat");
                setText("govSelectedAreaMeta", "Active monitoring target");
                await loadGovernmentResponsePreparation();
            }
        } catch (error) {
            if (requestId !== state.intelligenceRequest) return;
            console.error("Panchayat intelligence loading error:", error);
            showError(error.message || "Unable to load Panchayat intelligence.");
            setText("overviewStatus", "DATA UNAVAILABLE");
            setSelectionStatus("Panchayat intelligence unavailable — retry or choose another Panchayat", "error");
        }
    }

    function getSelectedGovernmentPanchayat() {
        const select = $("panchayatSelect");
        if (!select?.value) return null;
        const option = select.options[select.selectedIndex];
        return {
            id: Number(select.value),
            name: option?.textContent?.trim() || "Selected Panchayat"
        };
    }

    function setupGovernmentSelectors() {
        const stateSelect = $("stateSelect");
        const districtSelect = $("districtSelect");
        const talukaSelect = $("talukaSelect");
        const panchayatSelect = $("panchayatSelect");
        if (!stateSelect) return;

        stateSelect.addEventListener("change", async () => {
            state.intelligenceRequest++;
            state.panchayat = null;
            setSelectionStatus("Loading location hierarchy…", "loading");
            resetAiPrediction();
            resetRisk();
            try { await loadDistricts(stateSelect.value); }
            catch (error) { showError(error.message); }
        });

        districtSelect?.addEventListener("change", async () => {
            state.intelligenceRequest++;
            state.panchayat = null;
            setSelectionStatus("Loading location hierarchy…", "loading");
            resetAiPrediction();
            resetRisk();
            try { await loadTalukas(districtSelect.value); }
            catch (error) { showError(error.message); }
        });

        talukaSelect?.addEventListener("change", async () => {
            state.intelligenceRequest++;
            state.panchayat = null;
            setSelectionStatus("Loading location hierarchy…", "loading");
            resetAiPrediction();
            resetRisk();
            try { await loadPanchayats(talukaSelect.value); }
            catch (error) { showError(error.message); }
        });

        panchayatSelect?.addEventListener("change", async () => {
            const selected = getSelectedGovernmentPanchayat();
            if (!selected) {
                state.intelligenceRequest++;
                state.panchayat = null;
                resetAiPrediction();
                resetRisk();
                setText("overviewStatus", "SELECT PANCHAYAT");
                setSelectionStatus("Choose a Panchayat to begin monitoring", "");
                return;
            }

            // Resolve full Panchayat record from the current Taluka so map coordinates are available.
            try {
                const panchayats = await api(`/api/locations/panchayats/${talukaSelect.value}`);
                const full = panchayats.find(item => Number(item.id) === selected.id);
                if (full) await loadSelectedPanchayatIntelligence(full);
            } catch (error) {
                showError(error.message);
            }
        });

        loadStates().catch(error => showError(error.message));
    }

    // =========================================================
    // RESOLVE ASSIGNED PANCHAYAT
    // =========================================================

    async function resolveAssignedPanchayat() {
        const user = state.me?.user;
        if (!user?.panchayat) return;

        const states = await api("/api/locations/states");
        const matchedState = states.find(item => item.name === user.state);
        if (!matchedState) return;

        const districts = await api(`/api/locations/districts/${matchedState.id}`);
        const matchedDistrict = districts.find(item => item.name === user.district);
        if (!matchedDistrict) return;

        const talukas = await api(`/api/locations/talukas/${matchedDistrict.id}`);
        const matchedTaluka = talukas.find(item => item.name === user.taluka);
        if (!matchedTaluka) return;

        const panchayats = await api(`/api/locations/panchayats/${matchedTaluka.id}`);
        const matchedPanchayat = panchayats.find(item => item.name === user.panchayat);
        if (!matchedPanchayat) return;

        await loadSelectedPanchayatIntelligence(matchedPanchayat);
    }

    // =========================================================
    // NAVIGATION — ACTIVE SECTION
    // =========================================================

    function updateNavPill() {

        const nav =
            $("mdNavLinks");


        const activeItem =
            nav?.querySelector(
                ".md-nav-item.active"
            );


        if (
            !nav ||
            !activeItem
        ) {
            return;
        }


        const navRect =
            nav.getBoundingClientRect();


        const itemRect =
            activeItem.getBoundingClientRect();


        nav.style.setProperty(
            "--nav-pill-x",
            `${itemRect.left - navRect.left}px`
        );


        nav.style.setProperty(
            "--nav-pill-width",
            `${itemRect.width}px`
        );
    }


    function activateSection(
        target
    ) {

        const sections =
            document.querySelectorAll(
                ".md-section"
            );


        const navItems =
            document.querySelectorAll(
                ".md-nav-item"
            );


        sections.forEach(
            section => {

                section.classList.toggle(
                    "active",

                    section.dataset.section ===
                    target
                );
            }
        );


        navItems.forEach(
            item => {

                item.classList.toggle(
                    "active",

                    item.dataset.target ===
                    target
                );
            }
        );


        requestAnimationFrame(
            updateNavPill
        );


        // =========================================================
// CLOSE MENU AFTER NAVIGATION SELECTION
// =========================================================

const nav = $("mdNavLinks");
const menuButton = $("mdMenuButton");

if (nav) {
    nav.classList.remove("open");
}

if (menuButton) {

    // Return X → two lines
    menuButton.classList.remove("is-open");

    menuButton.setAttribute(
        "aria-expanded",
        "false"
    );

    menuButton.setAttribute(
        "aria-label",
        "Open navigation"
    );
}

    } // End activateSection()

    // =========================================================
    // NAVIGATION SETUP
    // =========================================================

    function setupNavigation() {

        const nav = $("mdNavLinks");
        const menuButton = $("mdMenuButton");
        const navbar = $("mdNavbar");
        const navItems = document.querySelectorAll(".md-nav-item");

        if (!nav || !navbar) {
            return;
        }

        function closeMobileMenu() {
            nav.classList.remove("open");

            if (menuButton) {
                menuButton.classList.remove("is-open");
                menuButton.setAttribute("aria-expanded", "false");
                menuButton.setAttribute("aria-label", "Open navigation");
            }
        }

        function updateNavPillSafe() {
            const activeItem = nav.querySelector(".md-nav-item.active");

            if (!activeItem || navbar.classList.contains("nav-collapsed")) {
                return;
            }

            const navRect = nav.getBoundingClientRect();
            const itemRect = activeItem.getBoundingClientRect();

            nav.style.setProperty(
                "--nav-pill-x",
                `${itemRect.left - navRect.left}px`
            );

            nav.style.setProperty(
                "--nav-pill-width",
                `${itemRect.width}px`
            );
        }

        /*
         * Collapse before Logout loses its space.
         * This measures the actual rendered navbar instead of relying
         * only on a fixed breakpoint.
         */
        function syncNavbarMode() {
            if (window.innerWidth <= 700) {
                navbar.classList.add("nav-collapsed");
                closeMobileMenu();
                return;
            }

            const brand = navbar.querySelector(".md-brand");
            const right = navbar.querySelector(".md-nav-right");
            const links = navbar.querySelector(".md-nav-links");

            if (!brand || !right || !links) {
                return;
            }

            const previous = navbar.classList.contains("nav-collapsed");

            /* Temporarily measure the full desktop layout. */
            navbar.classList.remove("nav-collapsed");
            links.classList.remove("open");

            const navbarWidth = navbar.clientWidth;
            const brandWidth = brand.getBoundingClientRect().width;
            const rightWidth = right.getBoundingClientRect().width;
            const linksWidth = links.scrollWidth;
            const styles = getComputedStyle(navbar);
            const gap = parseFloat(styles.columnGap || styles.gap || "18") || 18;

            /* 28px safety reserve prevents the Logout button from touching overflow. */
            const required = brandWidth + linksWidth + rightWidth + (gap * 2) + 28;
            const shouldCollapse = required > navbarWidth;

            if (shouldCollapse) {
                navbar.classList.add("nav-collapsed");
                closeMobileMenu();
            } else if (previous && !shouldCollapse) {
                navbar.classList.remove("nav-collapsed");
            }

            requestAnimationFrame(updateNavPillSafe);
        }

        navItems.forEach(item => {
            item.addEventListener("click", () => {
                const target = item.dataset.target;
                if (!target) return;

                if (target !== "alerts") {
                    activateSection(target);
                } else {
                    navItems.forEach(navItem => {
                        navItem.classList.toggle(
                            "active",
                            navItem.dataset.target === target
                        );
                    });
                    requestAnimationFrame(updateNavPillSafe);
                }

                /* Every selection closes the menu and returns X → two lines. */
                closeMobileMenu();

                const section = document.querySelector(
                    `[data-section="${target}"]`
                );

                if (section) {
                    window.scrollTo({
                        top:
                            section.getBoundingClientRect().top +
                            window.scrollY -
                            100,
                        behavior: "smooth"
                    });
                }
            });
        });

        if (menuButton) {
            menuButton.addEventListener("click", event => {
                event.stopPropagation();

                if (!navbar.classList.contains("nav-collapsed")) {
                    return;
                }

                const isOpen = nav.classList.toggle("open");

                menuButton.classList.toggle("is-open", isOpen);
                menuButton.setAttribute("aria-expanded", String(isOpen));
                menuButton.setAttribute(
                    "aria-label",
                    isOpen ? "Close navigation" : "Open navigation"
                );
            });
        }

        /* Close when clicking outside the navbar. */
        document.addEventListener("click", event => {
            if (!navbar.contains(event.target)) {
                closeMobileMenu();
            }
        });

        /* Escape closes the interactive menu. */
        document.addEventListener("keydown", event => {
            if (event.key === "Escape") {
                closeMobileMenu();
                menuButton?.focus();
            }
        });

        window.addEventListener("resize", () => {
            requestAnimationFrame(syncNavbarMode);
        }, { passive: true });

        requestAnimationFrame(() => {
            syncNavbarMode();
            updateNavPillSafe();
        });
    }


    // =========================================================
    // NAVBAR SCROLL EFFECT
    // =========================================================

    function setupNavbarScroll() {

        const navbar =
            $("mdNavbar");


        if (!navbar) {
            return;
        }


        window.addEventListener(
            "scroll",
            () => {

                navbar.classList.toggle(
                    "scrolled",

                    window.scrollY >
                    30
                );
            },
            {
                passive:
                    true
            }
        );
    }


    // =========================================================
    // WEATHER REFRESH
    // =========================================================

    function setupWeatherRefresh() {

        const refresh =
            $("refreshWeather");


        if (!refresh) {
            return;
        }


        refresh.addEventListener(
            "click",
            async () => {

                if (
                    !state.panchayat ||
                    !state.panchayat.id
                ) {
                    return;
                }


                refresh.disabled =
                    true;


                refresh.classList.add(
                    "is-refreshing"
                );


                refresh.innerHTML = `
                    <span class="md-refresh-spinner"></span>
                    Updating weather
                `;


                try {

                    await loadSelectedPanchayatIntelligence(
                        state.panchayat,
                        { autoAi: true }
                    );

                }
                catch (error) {

                    showError(
                        error.message
                    );
                }


                finally {

                    refresh.disabled =
                        false;


                    refresh.classList.remove(
                        "is-refreshing"
                    );


                    refresh.innerHTML =
                        "↻ Refresh";
                }
            }
        );
    }


    // =========================================================
    // LIVE INTELLIGENCE SNAPSHOT
    // =========================================================

    function updateLiveIntelligenceSnapshot() {
        const w = state.weather;
        const risk = state.risk?.risk || state.risk;
        const prediction = state.aiPrediction?.prediction || state.aiPrediction;

        if (w) {
            const temp = Number(w.temperature_c);
            const rain = Number(w.rainfall_mm);
            setText("overviewForecastValue", state.forecast?.length ? `${state.forecast.length} points` : "Available");
            setText("overviewForecastMeta", Number.isFinite(rain) ? `Current rain ${rain.toFixed(1)} mm • ${Number.isFinite(temp) ? temp.toFixed(1) : "--"}°C` : "Forecast data available for the selected Panchayat.");
        }

        if (risk) {
            const level = String(risk.level || "").toUpperCase();
            const badge = $("overviewRiskBadge");
            if (badge) {
                badge.className = `md-mini-risk md-risk-${level.toLowerCase() || "none"}`;
                badge.textContent = level || "NO DATA";
            }
            setText("overviewRiskValue", risk.label || level || "No risk data");
            const reasons = risk.explanation || risk.reasons || [];
            setText("overviewRiskReason", Array.isArray(reasons) && reasons.length ? reasons[0] : "Risk is calculated using the transparent screening engine.");
        }

        if (prediction) {
            const model = prediction.model_name || prediction.model || "MeghDrishti model";
            const target = prediction.target_time || prediction.prediction_time;
            setText("overviewAiValue", model);
            setText("overviewAiMeta", target ? `Target ${formatDate(target)} • Modelled Panchayat estimate` : "Latest Panchayat-level modelled estimate");
        }
    }

    // =========================================================
    // ROLE DASHBOARD SUMMARY
    // =========================================================

    async function loadRoleDashboardSummary() {
        const role = state.me?.user?.role;
        if (!role) return;

        if (role === "government") {
            try {
                const data = await api("/api/risk/overview");
                const items = data.panchayats || [];
                const counts = { GREEN: 0, YELLOW: 0, ORANGE: 0, RED: 0 };
                items.forEach(item => {
                    const level = String(item.risk?.level || "").toUpperCase();
                    if (Object.prototype.hasOwnProperty.call(counts, level)) counts[level] += 1;
                });
                setText("govTotalPanchayats", items.length);
                setText("govGreenCount", counts.GREEN);
                setText("govYellowCount", counts.YELLOW);
                setText("govOrangeCount", counts.ORANGE);
                setText("govRedCount", counts.RED);
                const high = items.filter(item => ["ORANGE", "RED"].includes(String(item.risk?.level || "").toUpperCase()));
                setText("roleRiskSummary", high.length ? `${high.length} elevated` : "No elevated risk");
                setText("govMonitorMessage", high.length ? `${high.length} Panchayat${high.length === 1 ? "" : "s"} currently require elevated-risk attention.` : "No Panchayat is currently in an elevated screening category.");
            } catch (error) {
                console.error("Government summary error:", error);
                setText("govMonitorMessage", "Monitoring summary unavailable. Use the Risk Map to inspect current data.");
            }
            return;
        }

        if (role === "panchayat_official" && state.panchayat?.id) {
            const risk = state.risk?.risk;
            setText("officialRiskLevel", risk ? `${risk.level} • ${risk.label}` : "NO RISK DATA");
            setText("officialRiskReason", risk?.explanation?.[0] || "Latest localized risk assessment is not available yet.");
            if (risk) {
                const level = String(risk.level).toUpperCase();
                const actions = {
                    GREEN: ["Routine monitoring", "Continue normal local weather awareness."],
                    YELLOW: ["Increase vigilance", "Review local conditions and keep response teams informed."],
                    ORANGE: ["Prepare local response", "Inspect vulnerable locations and prepare appropriate local resources."],
                    RED: ["Immediate preparedness", "Inspect vulnerable/low-lying areas and follow applicable official instructions."]
                };
                const action = actions[level] || actions.YELLOW;
                setText("officialActionTitle", action[0]);
                setText("officialActionText", action[1]);
            }
            return;
        }

        if (role === "citizen" && state.panchayat?.id) {
            const risk = state.risk?.risk;
            const weather = state.weather;
            setText("roleWeatherSummary", weather?.temperature_c != null ? `${Number(weather.temperature_c).toFixed(1)}°C` : "Weather ready");
            setText("citizenSafetyTitle", risk ? `${risk.level} • ${risk.label}` : "Local conditions available");
            setText("citizenSafetyText", risk?.explanation?.[0] || "Check the latest forecast and follow official instructions during severe weather.");
        }

    }

    // =========================================================
    // GOVERNMENT RESPONSE MONITORING
    // =========================================================

    function responseStateForRisk(level) {
        const normalized = String(level || "").toUpperCase();
        if (normalized === "RED") return ["Priority attention", "Review applicable official procedures"];
        if (normalized === "ORANGE") return ["Prepare locally", "Inspect vulnerable areas and resources"];
        if (normalized === "YELLOW") return ["Heightened watch", "Continue local monitoring"];
        return ["Routine monitoring", "Continue normal awareness"];
    }

    function renderGovernmentResponseRows(items) {
        const tbody = $("govResponseRows");
        if (!tbody) return;
        if (!items.length) {
            tbody.innerHTML = '<tr><td colspan="4">No Panchayat monitoring data available.</td></tr>';
            return;
        }
        tbody.innerHTML = items.map(item => {
            const name = item.panchayat?.name || "Panchayat";
            const level = String(item.risk?.level || "NO DATA").toUpperCase();
            const score = Number(item.risk?.score);
            const [stateLabel, nextStep] = responseStateForRisk(level);
            const scoreText = Number.isFinite(score) ? ` • ${score.toFixed(0)}/100` : "";
            return `<tr><td><strong>${name}</strong></td><td><span class="md-table-risk md-table-risk-${level.toLowerCase()}">${level}${scoreText}</span></td><td>${stateLabel}<small>Monitoring only — no acknowledgement recorded</small></td><td>${nextStep}</td></tr>`;
        }).join("");
    }

    async function loadGovernmentResponsePreparation() {
        if (state.me?.user?.role !== "government") return;
        try {
            const data = await api("/api/risk/overview");
            const items = data.panchayats || [];
            const elevated = items.filter(item => ["ORANGE", "RED"].includes(String(item.risk?.level || "").toUpperCase())).length;
            setText("govElevatedCount", elevated);
            renderGovernmentResponseRows(items);
            const selected = state.panchayat;
            setText("govSelectedArea", selected?.name || "None");
            setText("govSelectedAreaMeta", selected?.id ? "Active monitoring target" : "Choose a Panchayat");
        } catch (error) {
            console.error("Government response preparation error:", error);
            setText("govElevatedCount", "--");
            const tbody = $("govResponseRows");
            if (tbody) tbody.innerHTML = '<tr><td colspan="4">Operational monitoring data is temporarily unavailable.</td></tr>';
        }
    }

    function setSelectionStatus(message, mode = "") {
        const el = $("selectedPanchayatStatus");
        if (!el) return;
        const wrap = el.closest(".md-selection-status");
        if (wrap) wrap.classList.remove("is-loading", "is-live", "is-error");
        if (wrap && mode) wrap.classList.add(`is-${mode}`);
        el.textContent = message;
    }

    function setupRoleDashboardActions() {
        document.querySelectorAll("[data-target]").forEach(button => {
            if (!button.classList.contains("md-nav-item")) {
                button.addEventListener("click", () => {
                    const target = button.dataset.target;
                    if (!target) return;
                    const navItem = document.querySelector(`.md-nav-item[data-target="${target}"]`);
                    if (navItem) navItem.click();
                });
            }
        });
    }

    // =========================================================
    // ALERT & RESPONSE CENTER
    // =========================================================

    function escapeHtml(value) {
        return String(value ?? "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    function alertFeedback(message, isError = false) {
        const box = $("alertFeedback");
        if (!box) return;
        box.hidden = !message;
        box.classList.toggle("is-error", Boolean(isError));
        box.textContent = message || "";
    }

    function renderAlerts(alerts) {
        const list = $("alertList");
        if (!list) return;
        setText("alertActiveCount", alerts.length);
        if (!alerts.length) {
            list.innerHTML = '<div class="md-alert-empty">No active screening alerts in the current account scope.</div>';
            return;
        }
        list.innerHTML = alerts.map(alert => {
            const level = escapeHtml(String(alert.severity || "").toUpperCase());
            const status = escapeHtml(alert.status || "ACTIVE");
            const name = escapeHtml(alert.panchayat?.name || "Panchayat");
            const score = Number(alert.risk_score);
            const scoreText = Number.isFinite(score) ? `${score.toFixed(1)}/100` : "--";
            const generated = alert.generated_at ? formatDate(alert.generated_at) : "--";
            const response = escapeHtml(alert.response_status || "PENDING");
            const summary = alert.notification_summary || {};
            const queued = Number(summary.in_app_queued || 0) + Number(summary.sms_ready_queued || 0);
            const accepted = Number(summary.accepted || 0);
            const delivered = Number(summary.delivered || 0);
            const dryRun = Number(summary.dry_run || 0);
            const failed = Number(summary.failed || 0);
            const smsReady = Number(summary.sms_ready_queued || 0);
            const isOperational = ["government", "panchayat_official"].includes(state.me?.user?.role);
            const totalTracked = queued + delivered + dryRun + failed;
            const deliveryPercent = totalTracked ? Math.round(((delivered + dryRun) / totalTracked) * 100) : 0;
            const deliveryClass = failed ? "is-warning" : (dryRun ? "is-neutral" : (delivered ? "is-good" : "is-neutral"));
            const deliveryLabel = failed ? "ATTENTION" : (dryRun ? `${dryRun} SIMULATED` : (delivered ? `${deliveryPercent}% TRACKED` : "READY"));
            const deliveryMeta = failed ? `${failed} failed • ${delivered} delivered • ${dryRun} simulated` : `${delivered} delivered • ${dryRun} simulated • ${smsReady} SMS-ready`;
            const acknowledged = String(alert.response_status || "").toUpperCase() === "ACKNOWLEDGED";
            const smsButton = isOperational && alert.status === "ACTIVE" && smsReady > 0
                ? `<button type="button" class="md-alert-action sms" data-sms-alert="${alert.id}">Send SMS (${smsReady})</button>`
                : "";
            const buttons = isOperational && alert.status === "ACTIVE"
                ? `${smsButton}<button type="button" class="md-alert-action${acknowledged ? " is-current" : ""}" data-ack-alert="${alert.id}">${acknowledged ? "Update Acknowledgement" : "Acknowledge"}</button><button type="button" class="md-alert-action resolve" data-resolve-alert="${alert.id}">Resolve</button>`
                : "";
            const latestResponse = alert.responses?.[0];
            const note = latestResponse?.note ? `<div class="md-alert-response-note"><span>Latest response</span><p>${escapeHtml(latestResponse.note)}</p></div>` : "";
            return `<article class="md-alert-card">
                <div>
                    <div class="md-alert-card-head"><span class="md-alert-severity ${level.toLowerCase()}">${level}</span><span class="md-alert-status">${status}</span><h4>${name}</h4></div>
                    <p>${escapeHtml(alert.message)}</p>
                    <div class="md-alert-meta"><span>Risk ${scoreText}</span><span>Generated ${escapeHtml(generated)}</span><span>Response ${response}</span></div>
                    <div class="md-alert-delivery">
                        <div class="md-alert-delivery-head"><span>NOTIFICATION DELIVERY</span><strong class="${deliveryClass}">${deliveryLabel}</strong></div>
                        <div class="md-alert-delivery-track"><span style="width:${Math.min(deliveryPercent,100)}%"></span></div>
                        <div class="md-alert-delivery-meta"><span>${accepted} accepted</span><span>${delivered} delivered</span><span>${dryRun} simulated</span><span>${queued} queued</span><span>${failed} failed</span><span>${smsReady} SMS-ready</span></div>
                    </div>
                    ${note}
                    <div class="md-alert-notification-note">QUEUED = waiting for provider processing • ACCEPTED = Fast2SMS accepted the request • DELIVERED = handset/provider delivery confirmed when available • SMS-ready = provider handoff prepared.</div>
                </div>
                <div class="md-alert-actions">${buttons}</div>
            </article>`;
        }).join("");

        list.querySelectorAll("[data-ack-alert]").forEach(button => {
            button.addEventListener("click", () => updateAlertStatus(button.dataset.ackAlert, "acknowledge"));
        });
        list.querySelectorAll("[data-resolve-alert]").forEach(button => {
            button.addEventListener("click", () => updateAlertStatus(button.dataset.resolveAlert, "resolve"));
        });
        list.querySelectorAll("[data-sms-alert]").forEach(button => {
            button.addEventListener("click", () => sendAlertSms(button.dataset.smsAlert, button));
        });
    }

    async function loadAlerts() {
        try {
            const data = await api("/api/alerts?status=ACTIVE");
            const alerts = data.alerts || [];
            if (["government", "panchayat_official"].includes(state.me?.user?.role) && alerts.length) {
                await Promise.all(alerts.map(async (alert) => {
                    try {
                        const notificationData = await api(`/api/alerts/${alert.id}/notifications`);
                        alert.notification_summary = notificationData.summary || alert.notification_summary;
                    } catch (notificationError) {
                        console.warn("Notification summary unavailable:", notificationError);
                    }
                }));
            }
            renderAlerts(alerts);
            const queued = alerts.reduce((total, alert) => {
                const summary = alert.notification_summary || {};
                return total + Number(summary.queued || (Number(summary.in_app_queued || 0) + Number(summary.sms_ready_queued || 0)));
            }, 0);
            setText("alertQueueStatus", alerts.length ? (queued ? `${queued} QUEUED` : "READY") : "READY");
            const tracked = alerts.reduce((acc, alert) => {
                const summary = alert.notification_summary || {};
                acc.queued += Number(summary.queued || (Number(summary.in_app_queued || 0) + Number(summary.sms_ready_queued || 0)));
                acc.accepted += Number(summary.accepted || 0);
                acc.delivered += Number(summary.delivered || 0);
                acc.dryRun += Number(summary.dry_run || 0);
                acc.failed += Number(summary.failed || 0);
                acc.sms += Number(summary.sms_ready_queued || 0);
                return acc;
            }, { queued: 0, accepted: 0, delivered: 0, dryRun: 0, failed: 0, sms: 0 });
            const totalTracked = tracked.queued + tracked.delivered + tracked.dryRun + tracked.failed;
            const deliveryPercent = totalTracked ? Math.round(((tracked.delivered + tracked.dryRun) / totalTracked) * 100) : 0;
            setText("alertDeliveryHealth", tracked.failed ? "ATTENTION" : (tracked.dryRun ? `${tracked.dryRun} SIMULATED` : (totalTracked ? `${deliveryPercent}%` : "READY")));
            setText("alertDeliveryMeta", tracked.failed ? `${tracked.failed} failed • ${tracked.accepted} accepted • ${tracked.delivered} delivered • ${tracked.dryRun} simulated` : `${tracked.accepted} accepted • ${tracked.delivered} delivered • ${tracked.dryRun} simulated • ${tracked.sms} SMS-ready`);
            const deliveryHealth = $("alertDeliveryHealth");
            if (deliveryHealth) deliveryHealth.className = tracked.failed ? "is-warning" : (tracked.delivered ? "is-good" : "is-neutral");
            setText("alertSelectedArea", state.panchayat?.name || "--");
            const level = state.risk?.risk?.level;
            setText("alertSelectedRisk", level ? `${level} screening level` : "Select a Panchayat");
            return data.alerts || [];
        } catch (error) {
            console.error("Alert loading error:", error);
            setText("alertActiveCount", "--");
            setText("alertQueueStatus", "UNAVAILABLE");
            alertFeedback(error.message || "Unable to load alerts.", true);
            return [];
        }
    }

    function renderAlertHistory(events) {
        const list = $("alertHistoryList");
        if (!list) return;
        if (!events.length) {
            list.innerHTML = '<div class="md-alert-history-empty">No alert activity matches the selected history filter.</div>';
            return;
        }

        list.innerHTML = events.map(event => {
            const severity = escapeHtml(String(event.severity || "").toUpperCase());
            const eventName = escapeHtml(String(event.event || "EVENT").replaceAll("_", " "));
            const panchayat = escapeHtml(event.panchayat?.name || "Panchayat");
            const actor = escapeHtml(event.user_name || "System");
            const at = event.at ? formatDate(event.at) : "--";
            const note = event.note ? escapeHtml(event.note) : "No operational note recorded.";
            const stateClass = String(event.status || "").toLowerCase();
            return `<article class="md-alert-history-row ${stateClass}">
                <div class="md-alert-history-main">
                    <span class="md-alert-severity ${severity.toLowerCase()}">${severity || "ALERT"}</span>
                    <div><strong>${panchayat}</strong><small>Alert #${escapeHtml(String(event.alert_id))}</small></div>
                </div>
                <div class="md-alert-history-event">${eventName}</div>
                <div class="md-alert-history-time">${at}<br>Actor: ${actor}</div>
                <div class="md-alert-history-note-cell"><span class="md-alert-history-note">${note}</span></div>
            </article>`;
        }).join("");
    }

    async function loadAlertHistory() {
        const list = $("alertHistoryList");
        const status = $("alertHistoryStatus")?.value || "ALL";
        if (list) list.innerHTML = '<div class="md-alert-history-empty">Loading alert history…</div>';
        try {
            const data = await api(`/api/alerts/history?status=${encodeURIComponent(status)}&limit=100`);
            renderAlertHistory(data.events || []);
            return data;
        } catch (error) {
            console.error("Alert history loading error:", error);
            if (list) list.innerHTML = `<div class="md-alert-history-empty">${escapeHtml(error.message || "Unable to load alert history.")}</div>`;
            return { events: [] };
        }
    }

    async function generateScreeningAlert() {
        if (!state.panchayat?.id) {
            alertFeedback("Select a Panchayat and load its current intelligence first.", true);
            return;
        }
        const button = $("generateAlertButton");
        if (button) { button.disabled = true; button.textContent = "Generating…"; }
        alertFeedback("");
        try {
            const response = await fetch(`/api/alerts/generate/${state.panchayat.id}`, {
                method: "POST",
                credentials: "same-origin",
                headers: { "Accept": "application/json", "Content-Type": "application/json" },
                body: JSON.stringify({})
            });
            const data = await response.json().catch(() => ({}));
            if (!response.ok) throw new Error(data.error || "Alert generation failed.");
            alertFeedback(data.message || "Screening alert created.");
            await loadAlerts();
        } catch (error) {
            console.error("Alert generation error:", error);
            alertFeedback(error.message || "Alert generation failed.", true);
        } finally {
            if (button) { button.disabled = false; button.textContent = "Generate Screening Alert"; }
        }
    }

    async function sendAlertSms(alertId, button) {
        if (button) {
            button.disabled = true;
            button.textContent = "Sending…";
        }
        alertFeedback("");
        try {
            const response = await fetch(`/api/alerts/${alertId}/send-sms`, {
                method: "POST",
                credentials: "same-origin",
                headers: { "Accept": "application/json", "Content-Type": "application/json" },
                body: JSON.stringify({})
            });
            const data = await response.json().catch(() => ({}));
            if (!response.ok) throw new Error(data.error || "SMS delivery could not be processed.");
            alertFeedback(data.message || "SMS delivery processed.");
            await loadAlerts();
            await loadAlertHistory();
        } catch (error) {
            console.error("SMS delivery error:", error);
            alertFeedback(error.message || "SMS delivery failed.", true);
        } finally {
            if (button) {
                button.disabled = false;
                button.textContent = "Send SMS";
            }
        }
    }

    async function updateAlertStatus(alertId, action) {
        const note = window.prompt(action === "resolve" ? "Optional resolution note:" : "Optional acknowledgement note:", "") ?? "";
        try {
            const response = await fetch(`/api/alerts/${alertId}/${action}`, {
                method: "POST",
                credentials: "same-origin",
                headers: { "Accept": "application/json", "Content-Type": "application/json" },
                body: JSON.stringify({ note })
            });
            const data = await response.json().catch(() => ({}));
            if (!response.ok) throw new Error(data.error || `Unable to ${action} alert.`);
            alertFeedback(data.message || `Alert ${action}d.`);
            await loadAlerts();
            await loadAlertHistory();
            if (state.me?.user?.role === "government") await loadGovernmentResponsePreparation();
        } catch (error) {
            console.error(`Alert ${action} error:`, error);
            alertFeedback(error.message || `Unable to ${action} alert.`, true);
        }
    }

    function setupAlertCenter() {
        $("refreshAlerts")?.addEventListener("click", async () => {
            alertFeedback("");
            await loadAlerts();
        });
        $("generateAlertButton")?.addEventListener("click", async () => {
            await generateScreeningAlert();
            await loadAlertHistory();
        });
        $("refreshAlertHistory")?.addEventListener("click", loadAlertHistory);
        $("alertHistoryStatus")?.addEventListener("change", loadAlertHistory);
        loadAlerts();
        loadAlertHistory();
    }

    // =========================================================
    // APPLICATION INITIALIZATION
    // =========================================================

    async function initialize() {

        // -----------------------------------------------------
        // SAFETY CHECK
        // -----------------------------------------------------

        if (
            !document.getElementById(
                "mdNavbar"
            )
        ) {

            console.log(
                "MeghDrishti: dashboard elements not found. Initialization skipped."
            );

            return;
        }


        // -----------------------------------------------------
        // UI SETUP
        // -----------------------------------------------------

        setupNavigation();

        setupNavbarScroll();

        setupWeatherRefresh();

        setupAiPrediction();
        setupRiskMap();

        setupGovernmentSelectors();


        try {

            // -------------------------------------------------
            // CURRENT USER
            // -------------------------------------------------

            state.me =
                await api(
                    "/api/auth/me"
                );


            // -------------------------------------------------
            // AUTHENTICATION CHECK
            // -------------------------------------------------

            if (
                !state.me ||
                !state.me.authenticated
            ) {

                window.location.href =
                    "/";

                return;
            }


            setConnection(
                true
            );

            setupRoleDashboardActions();
            setupAlertCenter();

            // -------------------------------------------------
            // ROLE
            // -------------------------------------------------

            const role =
                state.me.user?.role;


            // -------------------------------------------------
            // GOVERNMENT
            // -------------------------------------------------

            if (
                role ===
                "government"
            ) {

                /*
                 * Government users manually
                 * select the Panchayat.
                 */

                await loadRoleDashboardSummary();
                await loadGovernmentResponsePreparation();

                // Government detail view is driven by the hierarchy selectors.
                // The selector handler calls the same intelligence pipeline used by scoped roles.
            }


            // -------------------------------------------------
            // PANCHAYAT OFFICIAL / CITIZEN
            // -------------------------------------------------

            await resolveAssignedPanchayat();
            await loadRoleDashboardSummary();

        }


        catch (error) {

            console.error(
                "MeghDrishti initialization error:",
                error
            );


            setConnection(
                false
            );


            showError(
                error.message
            );
        }
    }


    // =========================================================
    // START APPLICATION
    // =========================================================

    initialize();

});