import html
import json
from typing import Dict, List
from qgis.core import QgsMapLayer

from .base_generator import BaseGenerator

try:
    from ..core.style_manager import StyleManager
except (ImportError, ValueError):
    from core.style_manager import StyleManager


class JavaScriptGenerator(BaseGenerator):
    """Generator for JavaScript code."""

    def __init__(self, config: Dict):
        """Initialize the JavaScript generator.

        :param config: Project configuration
        """
        super().__init__(config)
        self.style_manager = StyleManager()

    def generate(self, layers: List[QgsMapLayer], **kwargs) -> Dict:
        """Generate JavaScript code.

        :param layers: List of QGIS layers
        :param kwargs: Additional parameters
        :returns: Dictionary with generation results
        """
        results = {
            'success': False,
            'javascript': '',
            'errors': []
        }

        try:
            template_type = kwargs.get('template', self.get_config_value('template', 'basic'))
            javascript = self._generate_javascript(template_type, layers)
            results['javascript'] = javascript
            results['success'] = True

        except Exception as e:
            results['errors'].append(f"JavaScript generation error: {str(e)}")

        return results

    def _generate_javascript(self, template_type: str, layers: List[QgsMapLayer]) -> str:
        """Generate JavaScript based on template type.

        :param template_type: Template type (basic, dashboard, storymap)
        :param layers: List of QGIS layers
        :returns: JavaScript string
        """
        if template_type == 'basic':
            return self._generate_basic_javascript(layers)
        elif template_type == 'dashboard':
            return self._generate_dashboard_javascript(layers)
        elif template_type == 'storymap':
            return self._generate_storymap_javascript(layers)
        else:
            return self._generate_basic_javascript(layers)

    def _generate_basic_javascript(self, layers: List[QgsMapLayer]) -> str:
        """Generate complete modern Leaflet JavaScript code.

        :param layers: List of QGIS layers
        :returns: JavaScript string
        """
        map_config = self.get_config_value('map', {})
        center = map_config.get('center', [0, 0])
        zoom = map_config.get('zoom', 3)
        min_zoom = map_config.get('min_zoom', 0)
        max_zoom = map_config.get('max_zoom', 20)

        basemap = self.get_config_value('basemap', {})
        default_basemap_provider = basemap.get('provider', 'osm')

        ui_config = self.get_config_value('ui', {})
        show_zoom_control = ui_config.get('show_zoom_control', True)
        show_scale_control = ui_config.get('show_scale_control', True)
        show_layer_control = ui_config.get('show_layer_control', True)
        show_fullscreen = ui_config.get('show_fullscreen', True)
        show_mouse_position = ui_config.get('show_mouse_position', True)
        show_legend = ui_config.get('show_legend', True)

        layer_configs = self._generate_layer_configs(layers)
        layer_loading_code = self._generate_layer_loading_code(layer_configs)
        legend_data = self._generate_legend_data(layers)

        javascript = f"""/**
 * WebGisMapBuilder - Generated Web Map Application
 * Powered by Leaflet & PyQGIS
 */

(function() {{
    'use strict';

    // 1. Initial Map Setup
    var map = L.map('map', {{
        center: [{center[0]}, {center[1]}],
        zoom: {zoom},
        minZoom: {min_zoom},
        maxZoom: {max_zoom},
        zoomControl: {str(show_zoom_control).lower()}
    }});

    // 2. Basemaps Catalog
    var basemaps = {{
        'OpenStreetMap': L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            maxZoom: 19
        }}),
        'CartoDB Positron': L.tileLayer('https://{{s}}.basemaps.cartocdn.com/light_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
            attribution: '&copy; OpenStreetMap &copy; CARTO',
            maxZoom: 20
        }}),
        'CartoDB Dark': L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
            attribution: '&copy; OpenStreetMap &copy; CARTO',
            maxZoom: 20
        }}),
        'ESRI World Imagery': L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
            attribution: 'Tiles &copy; Esri',
            maxZoom: 18
        }}),
        'OpenTopoMap': L.tileLayer('https://{{s}}.tile.opentopomap.org/{{z}}/{{x}}/{{y}}.png', {{
            attribution: '&copy; OpenStreetMap contributors, SRTM',
            maxZoom: 17
        }})
    }};

    // Add default basemap
    var selectedBasemap = basemaps['OpenStreetMap'];
    if ('{default_basemap_provider}' === 'carto_positron') selectedBasemap = basemaps['CartoDB Positron'];
    else if ('{default_basemap_provider}' === 'carto_dark') selectedBasemap = basemaps['CartoDB Dark'];
    else if ('{default_basemap_provider}' === 'esri_world') selectedBasemap = basemaps['ESRI World Imagery'];
    else if ('{default_basemap_provider}' === 'opentopomap') selectedBasemap = basemaps['OpenTopoMap'];
    selectedBasemap.addTo(map);

    // 3. Layer Groups
    var layerGroups = {{
        baseLayers: basemaps,
        overlays: {{}}
    }};

    // 4. Loading Layers with Styles and Popups
    {layer_loading_code}

    // 5. Controls
    {f"L.control.scale({{ metric: true, imperial: false }}).addTo(map);" if show_scale_control else ""}

    {'''// Mouse Position Control
    var coordsControl = L.control({ position: 'bottomleft' });
    coordsControl.onAdd = function() {
        var div = L.DomUtil.create('div', 'leaflet-coords-control');
        div.innerHTML = 'Lat: 0.00000 | Lon: 0.00000';
        return div;
    };
    coordsControl.addTo(map);
    map.on('mousemove', function(e) {
        var el = document.querySelector('.leaflet-coords-control');
        if (el) {
            el.innerHTML = 'Lat: ' + e.latlng.lat.toFixed(5) + ' | Lon: ' + e.latlng.lng.toFixed(5);
        }
    });''' if show_mouse_position else ''}

    {'''// Fullscreen Control
    var fullScreenControl = L.control({ position: 'topleft' });
    fullScreenControl.onAdd = function() {
        var btn = L.DomUtil.create('button', 'leaflet-bar leaflet-fullscreen-btn');
        btn.innerHTML = '⛶';
        btn.title = 'Toggle Fullscreen';
        btn.onclick = function() {
            if (!document.fullscreenElement) {
                document.documentElement.requestFullscreen().catch(function(err) {});
            } else {
                if (document.exitFullscreen) document.exitFullscreen();
            }
        };
        return btn;
    };
    fullScreenControl.addTo(map);''' if show_fullscreen else ''}

    // Layer Switcher Control
    {self._generate_layer_control_code(layer_configs, show_layer_control)}

    // 6. Interactive Legend
    {self._generate_legend_code(legend_data) if show_legend else '// Legend disabled'}

    // 7. Auto Zoom to Data Extents
    window.fitMapToBounds = function() {{
        var bounds = null;
        Object.values(layerGroups.overlays).forEach(function(l) {{
            if (map.hasLayer(l) && l.getBounds) {{
                var b = l.getBounds();
                if (b && b.isValid()) {{
                    bounds = bounds ? bounds.extend(b) : b;
                }}
            }}
        }});
        if (bounds && bounds.isValid()) {{
            map.fitBounds(bounds, {{ padding: [30, 30] }});
        }}
    }};

    setTimeout(function() {{
        window.fitMapToBounds();
    }}, 400);

}})();"""

        return javascript

    def _generate_dashboard_javascript(self, layers: List[QgsMapLayer]) -> str:
        """Generate dashboard JavaScript code."""
        base_js = self._generate_basic_javascript(layers)
        dashboard_js = base_js + """
    // Dashboard Stats update
    function updateDashboardStats() {
        var statContainer = document.getElementById('statistics');
        if (!statContainer) return;
        var total = Object.keys(layerGroups.overlays).length;
        var active = 0;
        Object.values(layerGroups.overlays).forEach(function(l) {
            if (map.hasLayer(l)) active++;
        });
        statContainer.innerHTML = '<div class="stat-pill"><b>Total Couches:</b> ' + total + '</div>' +
                                  '<div class="stat-pill"><b>Couches Actives:</b> ' + active + '</div>';
    }
    map.on('layeradd layerremove', updateDashboardStats);
    setTimeout(updateDashboardStats, 500);
"""
        return dashboard_js

    def _generate_storymap_javascript(self, layers: List[QgsMapLayer]) -> str:
        """Generate storymap JavaScript code."""
        base_js = self._generate_basic_javascript(layers)
        storymap_js = base_js + """
    // Storymap step navigation
    var sections = document.querySelectorAll('.storymap-section');
    sections.forEach(function(sec, idx) {
        sec.addEventListener('click', function() {
            sections.forEach(function(s) { s.classList.remove('active'); });
            sec.classList.add('active');
            var lat = parseFloat(sec.getAttribute('data-lat'));
            var lng = parseFloat(sec.getAttribute('data-lng'));
            var zoom = parseInt(sec.getAttribute('data-zoom')) || map.getZoom();
            if (!isNaN(lat) && !isNaN(lng)) {
                map.flyTo([lat, lng], zoom, { duration: 1.2 });
            }
        });
    });
"""
        return storymap_js

    def _generate_layer_configs(self, layers: List[QgsMapLayer]) -> List[Dict]:
        """Generate detailed configurations for all layers."""
        layer_configs = []

        for layer in layers:
            layer_id = self.get_layer_id(layer)
            cfg = self.get_config_value(f'layers.{layer.id()}', {})
            if not cfg:
                cfg = self.get_config_value(f'layers.{layer_id}', {})

            display_name = cfg.get('display_name', layer.name()) or layer.name()
            visible = cfg.get('visible', True)
            opacity = cfg.get('opacity', 1.0)
            geom_type = self._get_layer_type(layer)

            # Style conversion
            converted_style = self.style_manager.convert_layer_style(layer)
            style_code = self.style_manager.generate_leaflet_style(converted_style)
            point_to_layer_code = self.style_manager.generate_leaflet_point_to_layer(converted_style)

            # Popups
            popup_fields = cfg.get('popup_fields', [])
            if not popup_fields and layer.type() == QgsMapLayer.VectorLayer:
                for f in layer.fields():
                    popup_fields.append({
                        'name': f.name(),
                        'alias': f.alias() or f.name(),
                        'visible': True
                    })

            layer_configs.append({
                'id': layer_id,
                'name': display_name,
                'type': geom_type,
                'visible': visible,
                'opacity': opacity,
                'style_code': style_code,
                'point_to_layer_code': point_to_layer_code,
                'popup_fields': popup_fields
            })

        return layer_configs

    def _get_layer_type(self, layer: QgsMapLayer) -> str:
        """Get layer geometry type."""
        from qgis.core import QgsMapLayer, QgsWkbTypes

        if layer.type() == QgsMapLayer.VectorLayer:
            geom_type = layer.geometryType()
            type_map = {
                QgsWkbTypes.PointGeometry: 'point',
                QgsWkbTypes.LineGeometry: 'line',
                QgsWkbTypes.PolygonGeometry: 'polygon'
            }
            return type_map.get(geom_type, 'unknown')
        return 'raster'

    def _generate_layer_loading_code(self, layer_configs: List[Dict]) -> str:
        """Generate JavaScript code for loading layers with style, popups and offline fallback."""
        code_chunks = []

        for cfg in layer_configs:
            lid = cfg['id']
            lname = cfg['name']
            ltype = cfg['type']
            visible = cfg['visible']
            opacity = cfg['opacity']
            style_code = cfg['style_code']
            point_to_layer = cfg['point_to_layer_code']
            popup_fields = cfg['popup_fields']

            # Build popup formatting code
            popup_rows = []
            for pf in popup_fields:
                if isinstance(pf, dict) and pf.get('visible', True):
                    fname = pf.get('name')
                    falias = pf.get('alias', fname)
                    fname_esc = str(fname).replace("'", "\\'")
                    falias_esc = html.escape(str(falias))
                    popup_rows.append(f"""
        if (props['{fname_esc}'] !== undefined && props['{fname_esc}'] !== null && props['{fname_esc}'] !== '') {{
            html += '<tr><td class="popup-label">{falias_esc}</td><td class="popup-val">' + props['{fname_esc}'] + '</td></tr>';
        }}""")

            popup_func_body = "\n".join(popup_rows)

            options_parts = []
            if ltype == 'point' and point_to_layer:
                options_parts.append(f"pointToLayer: {point_to_layer}")
            elif style_code and style_code != '{}':
                options_parts.append(f"style: {style_code}")

            lname_title = html.escape(str(lname))
            lname_key_js = json.dumps(str(lname))

            options_parts.append(f"""onEachFeature: function(feature, layer) {{
        if (feature.properties) {{
            var props = feature.properties;
            var html = '<div class="popup-container"><div class="popup-title">{lname_title}</div><table class="popup-table">';
            {popup_func_body}
            html += '</table></div>';
            layer.bindPopup(html);
        }}
    }}""")

            options_js = "{\n        " + ",\n        ".join(options_parts) + "\n    }"

            chunk = f"""
    // --- Layer: {lname} ({lid}) ---
    function initLayer_{lid}(geojsonData) {{
        var layer = L.geoJSON(geojsonData, {options_js});
        layerGroups.overlays[{lname_key_js}] = layer;
        {f"layer.addTo(map);" if visible else ""}
    }}

    if (typeof json_{lid} !== 'undefined') {{
        initLayer_{lid}(json_{lid});
    }} else {{
        fetch('data/{lid}.geojson')
            .then(function(res) {{ return res.json(); }})
            .then(function(data) {{ initLayer_{lid}(data); }})
            .catch(function(err) {{ console.warn('Could not load layer {lid}:', err); }});
    }}
"""
            code_chunks.append(chunk)

        return "\n".join(code_chunks)

    def _generate_layer_control_code(self, layer_configs: List[Dict], show_control: bool) -> str:
        """Generate JavaScript code for layer control."""
        if not show_control:
            return ""

        return """var layerControl = L.control.layers(layerGroups.baseLayers, layerGroups.overlays, {
        collapsed: false,
        position: 'topright'
    }).addTo(map);"""

    def _generate_legend_data(self, layers: List[QgsMapLayer]) -> List[Dict]:
        """Extract all legend items from active layers."""
        legend_data = []
        for layer in layers:
            items = self.style_manager.extract_legend_items(layer)
            if items:
                legend_data.append({
                    'layer_name': layer.name(),
                    'items': items
                })
        return legend_data

    def _generate_legend_code(self, legend_data: List[Dict]) -> str:
        """Generate interactive HTML/JS Leaflet Legend control."""
        if not legend_data:
            return "// No legend data available"

        try:
            legend_items_html = []
            for group in legend_data:
                lname = html.escape(str(group.get('layer_name', '')))
                legend_items_html.append(f'<div class="legend-group"><div class="legend-layer-title">{lname}</div>')
                for item in group.get('items', []):
                    label = html.escape(str(item.get('label', '')))
                    color = str(item.get('color', '#3388ff'))
                    gtype = str(item.get('type', 'Polygon'))
                    border_radius = "50%" if gtype == 'Point' else "2px"
                    legend_items_html.append(
                        f'<div class="legend-row">'
                        f'<span class="legend-swatch" style="background:{color}; border-radius:{border_radius};"></span>'
                        f'<span class="legend-text">{label}</span>'
                        f'</div>'
                    )
                legend_items_html.append('</div>')

            content_html = "".join(legend_items_html)
            full_html = (
                '<div class="legend-header">'
                '<span>Légende</span>'
                '<button id="legend-toggle-btn" class="legend-toggle">−</button>'
                '</div>'
                f'<div class="legend-content">{content_html}</div>'
            )
            escaped_html_js = json.dumps(full_html)

            return f"""// Dynamic Legend Control
    var legendControl = L.control({{ position: 'bottomright' }});
    legendControl.onAdd = function() {{
        var div = L.DomUtil.create('div', 'leaflet-legend-box');
        div.innerHTML = {escaped_html_js};
        L.DomEvent.disableClickPropagation(div);
        return div;
    }};
    legendControl.addTo(map);

    document.addEventListener('click', function(e) {{
        if (e.target && e.target.id === 'legend-toggle-btn') {{
            var content = document.querySelector('.legend-content');
            if (content) {{
                if (content.style.display === 'none') {{
                    content.style.display = 'block';
                    e.target.innerText = '−';
                }} else {{
                    content.style.display = 'none';
                    e.target.innerText = '+';
                }}
            }}
        }}
    }});"""
        except Exception as e:
            return f"// Legend generation error: {str(e)}"

    def validate(self) -> tuple:
        """Validate JavaScript generator configuration."""
        errors = []
        if not self.get_config_value('map.center'):
            errors.append("Map center not configured")
        return (len(errors) == 0, errors)
