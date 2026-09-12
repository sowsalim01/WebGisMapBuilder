"""
Leaflet Generator - Generate Leaflet-based web maps
"""

import html
import os
from typing import Dict, List
from qgis.core import QgsMapLayer

from .base_generator import BaseGenerator


class LeafletGenerator(BaseGenerator):
    """Generator for Leaflet-based web maps."""

    def __init__(self, config: Dict):
        """Initialize the Leaflet generator.

        :param config: Project configuration
        """
        super().__init__(config)
        self.layer_data = {}

    def generate(self, layers: List[QgsMapLayer], **kwargs) -> Dict:
        """Generate Leaflet web map.

        :param layers: List of QGIS layers
        :param kwargs: Additional parameters
        :returns: Dictionary with generation results
        """
        results = {
            'success': False,
            'html': '',
            'css': '',
            'javascript': '',
            'layers': [],
            'errors': []
        }

        try:
            from .html_generator import HTMLGenerator
            from .css_generator import CSSGenerator
            from .js_generator import JavaScriptGenerator

            template_type = kwargs.get('template', self.get_config_value('template', 'basic'))

            # Generate HTML
            html_gen = HTMLGenerator(self.config)
            html_res = html_gen.generate(layers, template=template_type)
            results['html'] = html_res.get('html', '')
            if not html_res.get('success'):
                results['errors'].extend(html_res.get('errors', []))

            # Generate CSS
            css_gen = CSSGenerator(self.config)
            css_res = css_gen.generate(layers, template=template_type)
            results['css'] = css_res.get('css', '')
            if not css_res.get('success'):
                results['errors'].extend(css_res.get('errors', []))

            # Generate JS
            js_gen = JavaScriptGenerator(self.config)
            js_res = js_gen.generate(layers, template=template_type)
            results['javascript'] = js_res.get('javascript', '')
            if not js_res.get('success'):
                results['errors'].extend(js_res.get('errors', []))

            results['success'] = len(results['errors']) == 0

        except Exception as e:
            results['errors'].append(f"Generation error: {str(e)}")

        return results

    def _generate_layer_configs(self, layers: List[QgsMapLayer]) -> List[Dict]:
        """Generate layer configurations for Leaflet.

        :param layers: List of QGIS layers
        :returns: List of layer configuration dictionaries
        """
        layer_configs = []

        for layer in layers:
            layer_id = self.get_layer_id(layer)
            layer_config = {
                'id': layer_id,
                'name': html.escape(layer.name()),
                'type': self._get_leaflet_layer_type(layer),
                'data_file': f"data/{layer_id}.geojson",
                'visible': True,
                'opacity': 1.0,
                'popup_enabled': True,
                'label_field': None
            }
            layer_configs.append(layer_config)

        return layer_configs

    def _get_leaflet_layer_type(self, layer: QgsMapLayer) -> str:
        """Get Leaflet layer type from QGIS layer.

        :param layer: QGIS map layer
        :returns: Leaflet layer type string
        """
        from qgis.core import QgsMapLayer, QgsWkbTypes

        if layer.type() == QgsMapLayer.VectorLayer:
            geom_type = layer.geometryType()
            type_map = {
                QgsWkbTypes.PointGeometry: 'point',
                QgsWkbTypes.LineGeometry: 'line',
                QgsWkbTypes.PolygonGeometry: 'polygon',
                QgsWkbTypes.UnknownGeometry: 'unknown'
            }
            return type_map.get(geom_type, 'unknown')
        elif layer.type() == QgsMapLayer.RasterLayer:
            return 'raster'
        else:
            return 'unknown'

    def _generate_html(self, layer_configs: List[Dict]) -> str:
        """Generate HTML template.

        :param layer_configs: List of layer configurations
        :returns: HTML string
        """
        title = html.escape(self.get_config_value('project.title', 'Web Map'))
        description = html.escape(self.get_config_value('project.description', ''))

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{description}">

    <!-- Leaflet CSS -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
          crossorigin=""/>

    <!-- Custom CSS -->
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div id="map"></div>

    <!-- Leaflet JS -->
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
            crossorigin=""></script>

    <!-- Custom JS -->
    <script src="js/app.js"></script>
</body>
</html>"""

        return html_content

    def _generate_css(self) -> str:
        """Generate CSS styles.

        :returns: CSS string
        """
        theme = self.get_config_value('theme', {})
        primary_color = theme.get('primary_color', '#2c3e50')
        secondary_color = theme.get('secondary_color', '#3498db')
        font_family = theme.get('font_family', 'Arial, sans-serif')

        css = f"""/* Basic Map Styling */
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    font-family: {font_family};
    height: 100vh;
    width: 100vw;
}}

#map {{
    height: 100%;
    width: 100%;
}}

/* Custom Popup Styling */
.leaflet-popup-content-wrapper {{
    border-radius: 4px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.3);
}}

.leaflet-popup-content {{
    margin: 10px;
    max-width: 300px;
}}

.popup-header {{
    font-weight: bold;
    color: {primary_color};
    margin-bottom: 5px;
    border-bottom: 2px solid {secondary_color};
    padding-bottom: 5px;
}}

.popup-field {{
    margin: 5px 0;
    font-size: 12px;
}}

.popup-label {{
    font-weight: bold;
    color: {primary_color};
}}

.popup-value {{
    color: #333;
}}

/* Custom Legend Styling */
.legend {{
    background: white;
    padding: 10px;
    border-radius: 4px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.3);
    font-size: 12px;
}}

.legend-title {{
    font-weight: bold;
    color: {primary_color};
    margin-bottom: 5px;
    border-bottom: 2px solid {secondary_color};
    padding-bottom: 5px;
}}

.legend-item {{
    margin: 5px 0;
    display: flex;
    align-items: center;
}}

.legend-color {{
    width: 20px;
    height: 20px;
    margin-right: 8px;
    border: 1px solid #ccc;
}}

.legend-label {{
    color: #333;
}}

/* Loading Indicator */
.loading {{
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: white;
    padding: 20px;
    border-radius: 4px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.3);
    z-index: 9999;
}}

.loading-spinner {{
    border: 4px solid #f3f3f3;
    border-top: 4px solid {secondary_color};
    border-radius: 50%;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
    margin: 0 auto;
}}

@keyframes spin {{
    0% {{ transform: rotate(0deg); }}
    100% {{ transform: rotate(360deg); }}
}}

/* Responsive Design */
@media (max-width: 768px) {{
    .leaflet-popup-content {{
        max-width: 250px;
    }}

    .legend {{
        font-size: 10px;
        padding: 8px;
    }}
}}"""

        return css

    def _generate_javascript(self, layer_configs: List[Dict]) -> str:
        """Generate JavaScript code.

        :param layer_configs: List of layer configurations
        :returns: JavaScript string
        """
        # Get map configuration
        map_config = self.get_config_value('map', {})
        center = map_config.get('center', [0, 0])
        zoom = map_config.get('zoom', 2)
        min_zoom = map_config.get('min_zoom', 0)
        max_zoom = map_config.get('max_zoom', 18)

        # Get basemap configuration
        basemap = self.get_config_value('basemap', {})
        basemap_url = basemap.get('url', 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png')
        basemap_attribution = basemap.get('attribution', '© OpenStreetMap contributors')
        basemap_max_zoom = basemap.get('max_zoom', 19)

        # Get UI configuration
        ui_config = self.get_config_value('ui', {})
        show_zoom_control = ui_config.get('show_zoom_control', True)
        show_scale_control = ui_config.get('show_scale_control', True)
        show_layer_control = ui_config.get('show_layer_control', True)

        # Generate layer loading code
        layer_loading_code = self._generate_layer_loading_code(layer_configs)

        javascript = f"""// Initialize the map
var map = L.map('map', {{
    center: [{center[0]}, {center[1]}],
    zoom: {zoom},
    minZoom: {min_zoom},
    maxZoom: {max_zoom}
}});

// Add basemap
L.tileLayer('{basemap_url}', {{
    attribution: '{basemap_attribution}',
    maxZoom: {basemap_max_zoom}
}}).addTo(map);

// Add controls
{f"L.control.scale().addTo(map);" if show_scale_control else ""}

// Layer groups
var layerGroups = {{
    overlays: {{}}
}};

// Load layers
{layer_loading_code}

// Add layer control
{self._generate_layer_control_code(layer_configs, show_layer_control)}

// Fit map to layer bounds if layers exist
var layerBounds = null;
Object.values(layerGroups.overlays).forEach(function(layer) {{
    if (layer.getBounds) {{
        if (layerBounds) {{
            layerBounds.extend(layer.getBounds());
        }} else {{
            layerBounds = layer.getBounds();
        }}
    }}
}});

if (layerBounds) {{
    map.fitBounds(layerBounds);
}}

// Custom popup function
function createPopupContent(feature, layer) {{
    var properties = feature.properties;
    var content = '<div class="popup-content">';

    if (properties.name) {{
        content += '<div class="popup-header">' + properties.name + '</div>';
    }}

    for (var key in properties) {{
        if (properties.hasOwnProperty(key) && key !== 'name') {{
            content += '<div class="popup-field">';
            content += '<span class="popup-label">' + key + ':</span> ';
            content += '<span class="popup-value">' + properties[key] + '</span>';
            content += '</div>';
        }}
    }}

    content += '</div>';
    return content;
}}

console.log('Web map initialized successfully');"""

        return javascript

    def _generate_layer_loading_code(self, layer_configs: List[Dict]) -> str:
        """Generate JavaScript code for loading layers.

        :param layer_configs: List of layer configurations
        :returns: JavaScript string
        """
        loading_code = ""

        for layer_config in layer_configs:
            layer_id = layer_config['id']
            data_file = layer_config['data_file']
            layer_type = layer_config['type']

            if layer_type in ['point', 'line', 'polygon']:
                loading_code += f"""
// Load layer: {layer_config['name']}
fetch('{data_file}')
    .then(response => response.json())
    .then(data => {{
        var layer = L.geoJSON(data, {{
            style: function(feature) {{
                return {{
                    color: '#3388ff',
                    weight: 2,
                    opacity: 1,
                    fillOpacity: 0.5
                }};
            }},
            onEachFeature: function(feature, layer) {{
                if (feature.properties) {{
                    layer.bindPopup(createPopupContent(feature, layer));
                }}
            }}
        }});

        layerGroups.overlays['{layer_config['name']}'] = layer;
        layer.addTo(map);
    }})
    .catch(error => console.error('Error loading layer {layer_id}:', error));
"""

        return loading_code

    def _generate_layer_control_code(self, layer_configs: List[Dict], show_control: bool) -> str:
        """Generate JavaScript code for layer control.

        :param layer_configs: List of layer configurations
        :param show_control: Whether to show layer control
        :returns: JavaScript string
        """
        if not show_control or not layer_configs:
            return ""

        layer_names = []
        for layer_config in layer_configs:
            layer_names.append(f"'{layer_config['name']}': layerGroups.overlays['{layer_config['name']}']")

        layer_objects = ",\n        ".join(layer_names)

        return ("var layerControl = L.control.layers(\n"
                "    {}, // Base layers\n"
                "    {\n"
                "        " + layer_objects + "\n"
                "    },\n"
                "    {\n"
                "        collapsed: false,\n"
                "        position: 'topright'\n"
                "    }\n"
                ").addTo(map);")

    def validate(self) -> tuple:
        """Validate Leaflet generator configuration.

        :returns: Tuple of (is_valid, error_messages)
        """
        errors = []

        # Check required configuration
        if not self.get_config_value('map.center'):
            errors.append("Map center not configured")

        if not self.get_config_value('map.zoom'):
            errors.append("Map zoom not configured")

        if not self.get_config_value('basemap.url'):
            errors.append("Basemap URL not configured")

        return (len(errors) == 0, errors)
