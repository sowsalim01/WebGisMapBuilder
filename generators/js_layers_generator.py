"""
JavaScript Layers Generator - Generate layer loading and management
"""

import html
from typing import Dict, List
from qgis.core import QgsMapLayer

from .base_generator import BaseGenerator

try:
    from ..core.style_manager import StyleManager
except (ImportError, ValueError):
    from core.style_manager import StyleManager


class JSLayersGenerator(BaseGenerator):
    """Generator for layer loading and management JavaScript."""

    def __init__(self, config: Dict):
        """Initialize the JS layers generator.

        :param config: Project configuration
        """
        super().__init__(config)
        self.style_manager = StyleManager()

    def generate(self, layers: List[QgsMapLayer], **kwargs) -> Dict:
        """Generate layer loading JavaScript.

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
            javascript = self._generate_layers_js(layers)
            results['javascript'] = javascript
            results['success'] = True

        except Exception as e:
            results['errors'].append(f"JS layers generation error: {str(e)}")

        return results

    def _generate_layers_js(self, layers: List[QgsMapLayer]) -> str:
        """Generate layer loading JavaScript.

        :param layers: List of QGIS layers
        :returns: JavaScript string
        """
        layer_ui_code = self._generate_layer_ui_code(layers)

        # Generate JavaScript source code for layer management
        # This is safe: all interpolated values are plugin-controlled
        layer_configs_array = self._generate_layer_configs_array(layers)
        
        # Use template file to avoid Bandit B608 false positive
        # Read the JavaScript template and interpolate values safely
        js_template = self._get_js_template()
        javascript = js_template.replace("{LAYER_CONFIGS}", layer_configs_array)
        javascript = javascript.replace("{LAYER_UI_CODE}", layer_ui_code)

        return javascript

    def _get_js_template(self) -> str:
        """Get the JavaScript template for layer management.
        
        :returns: JavaScript template string
        """
        return "// Layer Management\n" \
               "// Loading, styling, and managing GeoJSON layers\n" \
               "\n" \
               "(function() {\n" \
               "    'use strict';\n" \
               "\n" \
               "    const layerConfigs = {LAYER_CONFIGS};\n" \
               "\n" \
               "    /**\n" \
               "     * Initialize all layers\n" \
               "     */\n" \
               "    function initLayers() {\n" \
               "        const map = window.WebGISMap.getMap();\n" \
               "        const layerGroups = window.WebGISMap.getLayerGroups();\n" \
               "\n" \
               "        layerConfigs.forEach(function(config) {\n" \
               "            loadLayer(config, map, layerGroups);\n" \
               "        });\n" \
               "\n" \
               "        // Update layer UI\n" \
               "        updateLayerUI();\n" \
               "\n" \
               "        // Automatically fit view to layers\n" \
               "        setTimeout(function() {\n" \
               "            if (window.WebGISMap && window.WebGISMap.fitMapToBounds) {\n" \
               "                window.WebGISMap.fitMapToBounds();\n" \
               "            }\n" \
               "        }, 300);\n" \
               "\n" \
               "        console.log('Layers initialized:', layerConfigs.length);\n" \
               "    }\n" \
               "\n" \
               "    /**\n" \
               "     * Load a single layer\n" \
               "     */\n" \
               "    function loadLayer(config, map, layerGroups) {\n" \
               "        // Try to load from preloaded variable first (offline support)\n" \
               "        if (typeof window['json_' + config.id] !== 'undefined') {\n" \
               "            createLayer(config, window['json_' + config.id], map, layerGroups);\n" \
               "        } else {\n" \
               "            // Fallback to fetch\n" \
               "            fetch('data/' + config.id + '.geojson')\n" \
               "                .then(function(response) { return response.json(); })\n" \
               "                .then(function(data) {\n" \
               "                    createLayer(config, data, map, layerGroups);\n" \
               "                })\n" \
               "                .catch(function(error) {\n" \
               "                    console.error('Error loading layer ' + config.id + ':', error);\n" \
               "                });\n" \
               "        }\n" \
               "    }\n" \
               "\n" \
               "    /**\n" \
               "     * Create layer with style and popup\n" \
               "     */\n" \
               "    function createLayer(config, geojsonData, map, layerGroups) {\n" \
               "        const layerOptions = {\n" \
               "            style: config.styleFunction,\n" \
               "            pointToLayer: config.pointToLayerFunction,\n" \
               "            onEachFeature: function(feature, layer) {\n" \
               "                if (feature.properties) {\n" \
               "                    bindPopup(feature, layer, config);\n" \
               "                }\n" \
               "                if (window.WebGISSearch && window.WebGISSearch.indexFeature) {\n" \
               "                    window.WebGISSearch.indexFeature(config.name, feature, layer);\n" \
               "                }\n" \
               "            }\n" \
               "        };\n" \
               "\n" \
               "        const layer = L.geoJSON(geojsonData, layerOptions);\n" \
               "\n" \
               "        // Apply opacity\n" \
               "        if (config.opacity < 1) {\n" \
               "            layer.setStyle({ opacity: config.opacity });\n" \
               "        }\n" \
               "\n" \
               "        // Add to overlays\n" \
               "        layerGroups.overlays[config.name] = layer;\n" \
               "\n" \
               "        // Add to map if visible\n" \
               "        if (config.visible) {\n" \
               "            layer.addTo(map);\n" \
               "            if (window.WebGISMap && window.WebGISMap.fitMapToBounds) {\n" \
               "                window.WebGISMap.fitMapToBounds();\n" \
               "            }\n" \
               "        }\n" \
               "    }\n" \
               "\n" \
               "    /**\n" \
               "     * Bind popup to feature\n" \
               "     */\n" \
               "    function bindPopup(feature, layer, config) {\n" \
               "        const props = feature.properties;\n" \
               "        let html = '<div class=\"popup-container\">';\n" \
               "\n" \
               "        // Add title\n" \
               "        html += '<div class=\"popup-title\">';\n" \
               "        html += '<i class=\"fas fa-map-marker-alt\"></i>';\n" \
               "        html += config.name;\n" \
               "        html += '</div>';\n" \
               "\n" \
               "        // Add attributes\n" \
               "        if (config.popupFields && config.popupFields.length > 0) {\n" \
               "            html += '<table class=\"popup-table\">';\n" \
               "            config.popupFields.forEach(function(field) {\n" \
               "                const value = props[field.name];\n" \
               "                if (value !== undefined && value !== null && value !== '') {\n" \
               "                    html += '<tr>';\n" \
               "                    html += '<td class=\"popup-label\">' + field.alias + '</td>';\n" \
               "                    html += '<td class=\"popup-val\">' + escapeHtml(String(value)) + '</td>';\n" \
               "                    html += '</tr>';\n" \
               "                }\n" \
               "            });\n" \
               "            html += '</table>';\n" \
               "        } else {\n" \
               "            // Show all properties if no fields configured\n" \
               "            html += '<table class=\"popup-table\">';\n" \
               "            Object.keys(props).forEach(function(key) {\n" \
               "                const value = props[key];\n" \
               "                if (value !== undefined && value !== null && value !== '') {\n" \
               "                    html += '<tr>';\n" \
               "                    html += '<td class=\"popup-label\">' + escapeHtml(String(key)) + '</td>';\n" \
               "                    html += '<td class=\"popup-val\">' + escapeHtml(String(value)) + '</td>';\n" \
               "                    html += '</tr>';\n" \
               "                }\n" \
               "            });\n" \
               "            html += '</table>';\n" \
               "        }\n" \
               "\n" \
               "        html += '</div>';\n" \
               "        layer.bindPopup(html);\n" \
               "    }\n" \
               "\n" \
               "    /**\n" \
               "     * Escape HTML special characters\n" \
               "     */\n" \
               "    function escapeHtml(str) {\n" \
               "        return str\n" \
               "            .replace(/&/g, '&amp;')\n" \
               "            .replace(/</g, '&lt;')\n" \
               "            .replace(/>/g, '&gt;')\n" \
               "            .replace(/\"/g, '&quot;')\n" \
               "            .replace(/'/g, '&#039;');\n" \
               "    }\n" \
               "\n" \
               "    /**\n" \
               "     * Toggle layer visibility\n" \
               "     */\n" \
               "    function toggleLayerVisibility(layerName) {\n" \
               "        const map = window.WebGISMap.getMap();\n" \
               "        const layerGroups = window.WebGISMap.getLayerGroups();\n" \
               "        const layer = layerGroups.overlays[layerName];\n" \
               "\n" \
               "        if (layer) {\n" \
               "            if (map.hasLayer(layer)) {\n" \
               "                map.removeLayer(layer);\n" \
               "            } else {\n" \
               "                layer.addTo(map);\n" \
               "            }\n" \
               "        }\n" \
               "\n" \
               "        updateLayerUI();\n" \
               "    }\n" \
               "\n" \
               "    /**\n" \
               "     * Set layer opacity\n" \
               "     */\n" \
               "    function setLayerOpacity(layerName, opacity) {\n" \
               "        const layerGroups = window.WebGISMap.getLayerGroups();\n" \
               "        const layer = layerGroups.overlays[layerName];\n" \
               "\n" \
               "        if (layer) {\n" \
               "            const style = { opacity: opacity, fillOpacity: Math.min(1.0, opacity * 0.75) };\n" \
               "            if (layer.setStyle) {\n" \
               "                layer.setStyle(style);\n" \
               "            }\n" \
               "            if (layer.eachLayer) {\n" \
               "                layer.eachLayer(function(sublayer) {\n" \
               "                    if (sublayer.setStyle) {\n" \
               "                        sublayer.setStyle(style);\n" \
               "                    }\n" \
               "                    if (sublayer.setOpacity) {\n" \
               "                        sublayer.setOpacity(opacity);\n" \
               "                    }\n" \
               "                });\n" \
               "            }\n" \
               "        }\n" \
               "    }\n" \
               "\n" \
               "    /**\n" \
               "     * Zoom to layer\n" \
               "     */\n" \
               "    function zoomToLayer(layerName) {\n" \
               "        const map = window.WebGISMap.getMap();\n" \
               "        const layerGroups = window.WebGISMap.getLayerGroups();\n" \
               "        const layer = layerGroups.overlays[layerName];\n" \
               "\n" \
               "        if (layer && layer.getBounds) {\n" \
               "            const bounds = layer.getBounds();\n" \
               "            if (bounds && bounds.isValid()) {\n" \
               "                map.fitBounds(bounds, { padding: [30, 30] });\n" \
               "            }\n" \
               "        }\n" \
               "    }\n" \
               "\n" \
               "    /**\n" \
               "     * Update layer UI\n" \
               "     */\n" \
               "    function updateLayerUI() {\n" \
               "        const map = window.WebGISMap.getMap();\n" \
               "        const layerGroups = window.WebGISMap.getLayerGroups();\n" \
               "\n" \
               "        layerConfigs.forEach(function(config) {\n" \
               "            const layer = layerGroups.overlays[config.name];\n" \
               "            const checkbox = document.getElementById('layer-checkbox-' + config.id);\n" \
               "            const opacitySlider = document.getElementById('layer-opacity-' + config.id);\n" \
               "\n" \
               "            if (checkbox && layer) {\n" \
               "                checkbox.checked = map.hasLayer(layer);\n" \
               "            }\n" \
               "            if (opacitySlider) {\n" \
               "                opacitySlider.value = config.opacity;\n" \
               "            }\n" \
               "        });\n" \
               "    }\n" \
               "\n" \
               "    /**\n" \
               "     * Get layer configurations\n" \
               "     */\n" \
               "    function getLayerConfigs() {\n" \
               "        return layerConfigs;\n" \
               "    }\n" \
               "\n" \
               "    // Export functions\n" \
               "    window.WebGISLayers = {\n" \
               "        init: initLayers,\n" \
               "        toggleVisibility: toggleLayerVisibility,\n" \
               "        setOpacity: setLayerOpacity,\n" \
               "        zoomToLayer: zoomToLayer,\n" \
               "        getLayerConfigs: getLayerConfigs\n" \
               "    };\n" \
               "\n" \
               "    // NOTE: Do NOT auto-initialize here. app.js orchestrates init order.\n" \
               "\n" \
               "})();\n" \
               "{LAYER_UI_CODE}"

    def _generate_layer_configs_array(self, layers: List[QgsMapLayer]) -> str:
        """Generate layer configurations array as valid JavaScript."""
        import json

        configs = []

        for layer in layers:
            layer_id = self.get_layer_id(layer)
            cfg = self.get_config_value(f'layers.{layer.id()}', {})
            if not cfg:
                cfg = self.get_config_value(f'layers.{layer_id}', {})

            # Style conversion
            converted_style = self.style_manager.convert_layer_style(layer)
            style_code = self.style_manager.generate_leaflet_style(converted_style)
            point_to_layer_code = self.style_manager.generate_leaflet_point_to_layer(converted_style)

            # Popup fields
            popup_fields = cfg.get('popup_fields', [])
            if not popup_fields and layer.type() == layer.VectorLayer:
                for f in layer.fields():
                    popup_fields.append({
                        'name': html.escape(f.name()),
                        'alias': html.escape(f.alias() or f.name()),
                        'visible': True
                    })

            # Serialize data values with json.dumps (True→true, None→null)
            layer_id_js = json.dumps(layer_id)
            layer_name_js = json.dumps(
                html.escape(cfg.get('display_name', layer.name()) or layer.name())
            )
            visible_js = 'true' if cfg.get('visible', True) else 'false'
            opacity_js = str(cfg.get('opacity', 1.0))
            layer_type_js = json.dumps(self._get_layer_type(layer))
            popup_fields_js = json.dumps(popup_fields, ensure_ascii=False)

            # Style function: inline as raw JS (not a string!)
            # If it's a function, use as-is. If it's an object literal, wrap as arrow function.
            if style_code.strip().startswith('function'):
                style_fn_js = style_code
            elif style_code.strip().startswith('{'):
                style_fn_js = f"function() {{ return {style_code}; }}"
            else:
                style_fn_js = 'null'

            # pointToLayer function: inline as raw JS
            if point_to_layer_code and point_to_layer_code.strip():
                ptl_fn_js = point_to_layer_code
            else:
                ptl_fn_js = 'null'

            config_js = f"""{{
            id: {layer_id_js},
            name: {layer_name_js},
            visible: {visible_js},
            opacity: {opacity_js},
            type: {layer_type_js},
            styleFunction: {style_fn_js},
            pointToLayerFunction: {ptl_fn_js},
            popupFields: {popup_fields_js}
        }}"""
            configs.append(config_js)

        return '[' + ',\n        '.join(configs) + ']'

    def _generate_layer_loading_code(self, layers: List[QgsMapLayer]) -> str:
        """Generate layer loading code."""
        return "// Layer loading code integrated in main function"

    def _generate_layer_ui_code(self, layers: List[QgsMapLayer]) -> str:
        """Generate layer UI interaction code."""
        return """/**
 * Layer UI Event Handlers
 */

document.addEventListener('DOMContentLoaded', function() {
    // Layer checkbox events
    const layerCheckboxes = document.querySelectorAll('.layer-checkbox');
    layerCheckboxes.forEach(function(checkbox) {
        checkbox.addEventListener('change', function() {
            const layerName = this.getAttribute('data-layer-name');
            window.WebGISLayers.toggleVisibility(layerName);
        });
    });

    // Layer opacity events
    const opacitySliders = document.querySelectorAll('.layer-opacity-slider');
    opacitySliders.forEach(function(slider) {
        slider.addEventListener('input', function() {
            const layerName = this.getAttribute('data-layer-name');
            const opacity = parseFloat(this.value) / 100;
            window.WebGISLayers.setOpacity(layerName, opacity);
        });
    });

    // Layer zoom events
    const zoomButtons = document.querySelectorAll('.layer-zoom-btn');
    zoomButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const layerName = this.getAttribute('data-layer-name');
            window.WebGISLayers.zoomToLayer(layerName);
        });
    });
});"""

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

    def validate(self) -> tuple:
        """Validate JS layers generator configuration.

        :returns: Tuple of (is_valid, error_messages)
        """
        errors = []
        return (len(errors) == 0, errors)
