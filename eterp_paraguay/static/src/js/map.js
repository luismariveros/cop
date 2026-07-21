/** @odoo-module **/
const {markup,xml, Component, onMounted} = owl;
import { standardFieldProps } from "@web/views/fields/standard_field_props";
// Import the registry
import {registry} from "@web/core/registry";

const API_KEY = "AIzaSyA88Zn1HJcSBsCNhc4FIF_h9Uv1SMNlxmU"


export class Map extends Component {
    setup() {
        super.setup();

        onMounted(() => {
            console.log(this.props.value)
            const url = this.props.value
            renderMap(url)
        })
    }
    divMap = markup(`<div style="width: 55vw; height: 55vw" id="map"></div>`)
}

Map.template = xml`<t t-out="divMap"/>`;
Map.props = standardFieldProps;

// Add the field to the correct category
registry.category("fields").add("mapa", Map);

function getCoordinates(url) {
    if(!url.includes("!3d")) return false
    
    const indexStartLat = url.indexOf("!3d") + 3
    const indexEndLat = url.indexOf("!", indexStartLat)
    
    const indexStartLng = url.indexOf("!4d", indexEndLat) + 3
    const indexEndLng = url.indexOf("?", indexStartLng)
    
    const lat = parseFloat(url.substring(indexStartLat, indexEndLat))
    const lng = parseFloat(url.substring(indexStartLng, indexEndLng > 0 ? indexEndLng : url.length))
    
    return {lat, lng}
}


function renderMap(url) {
    const coordinates = getCoordinates(url)

    if(!coordinates.lat || !coordinates.lng) {
        const map = document.getElementById("map")
        map.style.height = "auto"
        map.innerHTML = "<h2>Para ver el mapa complete el campo de ubicación con una url valida.</h2>"
        return false
    }

    // Create the script tag, set the appropriate attributes
    var script = document.createElement('script');
    script.src = `https://maps.googleapis.com/maps/api/js?key=${API_KEY}&callback=initMap`;
    script.async = true;

    let map;

    // Attach your callback function to the `window` object
    window.initMap = function () {
        // JS API is loaded and available
        map = new google.maps.Map(document.getElementById("map"), {
            center: coordinates,
            zoom: 8,
        });

        new google.maps.Marker({
            position: coordinates,
            map,
            title: "Hello World!",
        });
    };

    // Append the 'script' element to 'head'
    document.head.appendChild(script);

}