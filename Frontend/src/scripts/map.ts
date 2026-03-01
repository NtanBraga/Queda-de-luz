export async function initMap(elementId: string) {

    const portoAlegre = {
        north: -29.95,
        south: -30.25,
        west: -51.24,
        east: -51.08,
    }

    const {Map} = await google.maps.importLibrary("maps") as google.maps.MapsLibrary;

    const map = document.getElementById(elementId);

    if(map) {
        return new Map(map, {
            center: { lat: -30.0346, lng: -51.2177 },
            zoom: 13,
            minZoom: 12,
            maxZoom: 18,
            restriction: {
                latLngBounds: portoAlegre,
                strictBounds: false,
            }
        })
    }
}