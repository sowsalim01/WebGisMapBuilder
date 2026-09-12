"""
JavaScript Map Generator - Generate Leaflet map initialization
"""

from typing import Dict, List
from qgis.core import QgsMapLayer

from .base_generator import BaseGenerator


class JSMapGenerator(BaseGenerator):
    """Generator for Leaflet map initialization JavaScript."""

    def __init__(self, config: Dict):
        """Initialize the JS map generator.

        :param config: Project configuration
        """
        super().__init__(config)

    def generate(self, layers: List[QgsMapLayer], **kwargs) -> Dict:
        """Generate Leaflet map JavaScript.

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
            javascript = self._generate_map_js(layers)
            results['javascript'] = javascript
            results['success'] = True

        except Exception as e:
            results['errors'].append(f"JS map generation error: {str(e)}")

        return results

    def _generate_map_js(self, layers: List[QgsMapLayer]) -> str:
        """Generate Leaflet map initialization JavaScript.

        :param layers: List of QGIS layers
        :returns: JavaScript string
        """
        javascript = """/**
 * Leaflet Map Initialization
 * Main map setup and basemap management
 */

(function() {
    'use strict';

    // Global map instance
    let map = null;
    let currentBasemap = null;
    let layerGroups = {
        baseLayers: {},
        overlays: {}
    };

    /**
     * Initialize the Leaflet map
     */
    function initMap() {
        const config = WebGISConfig.map;

        map = L.map('map', {
            center: config.center,
            zoom: config.zoom,
            minZoom: config.minZoom,
            maxZoom: config.maxZoom,
            zoomControl: WebGISConfig.ui.showZoomControl
        });

        // Fit to initial bounds if configured
        if (config.bounds && Array.isArray(config.bounds)) {
            try {
                map.fitBounds(config.bounds, { padding: [40, 40] });
            } catch (e) {}
        }

        // Initialize basemaps
        initBasemaps();

        // Set default basemap
        setDefaultBasemap();

        // Initialize layer groups
        initLayerGroups();

        // Add event listeners
        addMapEventListeners();

        console.log('Map initialized successfully');
    }

    /**
     * Initialize basemap layers
     */
    function initBasemaps() {
        const providers = WebGISConfig.basemap.providers;

        layerGroups.baseLayers = {
            'OpenStreetMap': L.tileLayer(providers.osm.url, {
                attribution: providers.osm.attribution,
                maxZoom: providers.osm.maxZoom
            }),
            'CartoDB Positron': L.tileLayer(providers.carto_positron.url, {
                attribution: providers.carto_positron.attribution,
                maxZoom: providers.carto_positron.maxZoom
            }),
            'CartoDB Dark': L.tileLayer(providers.carto_dark.url, {
                attribution: providers.carto_dark.attribution,
                maxZoom: providers.carto_dark.maxZoom
            }),
            'ESRI World Imagery': L.tileLayer(providers.esri_world.url, {
                attribution: providers.esri_world.attribution,
                maxZoom: providers.esri_world.maxZoom
            }),
            'OpenTopoMap': L.tileLayer(providers.opentopomap.url, {
                attribution: providers.opentopomap.attribution,
                maxZoom: providers.opentopomap.maxZoom
            })
        };
    }

    /**
     * Set default basemap
     */
    function setDefaultBasemap() {
        const defaultProvider = WebGISConfig.basemap.default;
        const basemapNames = {
            'osm': 'OpenStreetMap',
            'carto_positron': 'CartoDB Positron',
            'carto_dark': 'CartoDB Dark',
            'esri_world': 'ESRI World Imagery',
            'opentopomap': 'OpenTopoMap'
        };

        const basemapName = basemapNames[defaultProvider] || 'OpenStreetMap';
        currentBasemap = layerGroups.baseLayers[basemapName];

        if (currentBasemap) {
            currentBasemap.addTo(map);
        }
    }

    /**
     * Initialize layer groups
     */
    function initLayerGroups() {
        layerGroups.overlays = {};
    }

    /**
     * Add map event listeners
     */
    function addMapEventListeners() {
        // Update coordinates on mouse move
        map.on('mousemove', function(e) {
            updateCoordinates(e.latlng);
        });

        // Fit bounds when layers are loaded
        map.on('layeradd', function() {
            fitMapToBounds();
        });
    }

    /**
     * Update coordinates display
     */
    function updateCoordinates(latlng) {
        const latDisplay = document.getElementById('lat-display');
        const lngDisplay = document.getElementById('lng-display');

        if (latDisplay && lngDisplay) {
            latDisplay.textContent = `Lat: ${latlng.lat.toFixed(5)}`;
            lngDisplay.textContent = `Lon: ${latlng.lng.toFixed(5)}`;
        }
    }

    /**
     * Fit map to layer bounds
     */
    function fitMapToBounds() {
        if (!map) return;
        let bounds = null;

        Object.values(layerGroups.overlays).forEach(function(layer) {
            if (map.hasLayer(layer) && layer.getBounds) {
                try {
                    const b = layer.getBounds();
                    if (b && typeof b.isValid === 'function' && b.isValid()) {
                        bounds = bounds ? bounds.extend(b) : b;
                    }
                } catch (e) {}
            }
        });

        if (bounds && typeof bounds.isValid === 'function' && bounds.isValid()) {
            map.fitBounds(bounds, { padding: [40, 40], maxZoom: 16 });
        } else if (typeof WebGISConfig !== 'undefined' && WebGISConfig.map && WebGISConfig.map.bounds) {
            try {
                map.fitBounds(WebGISConfig.map.bounds, { padding: [40, 40] });
            } catch (e) {}
        }
    }

    /**
     * Change basemap
     */
    function changeBasemap(basemapName) {
        if (currentBasemap) {
            map.removeLayer(currentBasemap);
        }

        if (layerGroups.baseLayers[basemapName]) {
            currentBasemap = layerGroups.baseLayers[basemapName];
            currentBasemap.addTo(map);
        }
    }

    /**
     * Zoom to specific location
     */
    function zoomToLocation(lat, lng, zoom) {
        map.setView([lat, lng], zoom || map.getZoom());
    }

    /**
     * Zoom to layer bounds
     */
    function zoomToLayer(layerId) {
        const layer = layerGroups.overlays[layerId];
        if (layer && layer.getBounds) {
            const bounds = layer.getBounds();
            if (bounds && bounds.isValid()) {
                map.fitBounds(bounds, { padding: [30, 30] });
            }
        }
    }

    /**
     * Get map instance
     */
    function getMap() {
        return map;
    }

    /**
     * Get layer groups
     */
    function getLayerGroups() {
        return layerGroups;
    }

    /**
     * Get current basemap
     */
    function getCurrentBasemap() {
        return currentBasemap;
    }

    // Export functions to global scope
    window.WebGISMap = {
        init: initMap,
        fitMapToBounds: fitMapToBounds,
        changeBasemap: changeBasemap,
        zoomToLocation: zoomToLocation,
        zoomToLayer: zoomToLayer,
        getMap: getMap,
        getLayerGroups: getLayerGroups,
        getCurrentBasemap: getCurrentBasemap
    };

    // NOTE: Do NOT auto-initialize here. app.js orchestrates init order.

})();"""

        return javascript

    def validate(self) -> tuple:
        """Validate JS map generator configuration.

        :returns: Tuple of (is_valid, error_messages)
        """
        errors = []
        return (len(errors) == 0, errors)