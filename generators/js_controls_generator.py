"""
JavaScript Controls Generator - Generate map controls JavaScript
"""

from typing import Dict, List
from qgis.core import QgsMapLayer

from .base_generator import BaseGenerator


class JSControlsGenerator(BaseGenerator):
    """Generator for map controls JavaScript."""

    def __init__(self, config: Dict):
        """Initialize the JS controls generator.

        :param config: Project configuration
        """
        super().__init__(config)

    def generate(self, layers: List[QgsMapLayer], **kwargs) -> Dict:
        """Generate map controls JavaScript.

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
            javascript = self._generate_controls_js()
            results['javascript'] = javascript
            results['success'] = True

        except Exception as e:
            results['errors'].append(f"JS controls generation error: {str(e)}")

        return results

    def _generate_controls_js(self) -> str:
        """Generate map controls JavaScript.

        :returns: JavaScript string
        """
        ui_config = self.get_config_value('ui', {})

        javascript = f"""/**
 * Map Controls
 * Zoom, scale, fullscreen, and other map controls
 */

(function() {{
    'use strict';

    /**
     * Scale control
     */
    {self._generate_scale_control_code(ui_config.get('show_scale_control', True))}

    let controlsInitialized = false;

    /**
     * Initialize map controls
     */
    function initControls() {{
        if (controlsInitialized) return;

        const map = window.WebGISMap ? window.WebGISMap.getMap() : null;
        if (!map) {{
            console.warn('Map not available for controls, retrying...');
            setTimeout(initControls, 200);
            return;
        }}

        controlsInitialized = true;

        // Scale control
        {self._generate_scale_control(ui_config.get('show_scale_control', True))}

        // Zoom controls
        initZoomControls();

        // Fullscreen control
        initFullscreenControl();

        // Location control
        initLocationControl();

        // Measure controls
        initMeasureControls();

        console.log('Controls initialized');
    }}

    /**
     * Initialize zoom controls
     */
    function initZoomControls() {{
        const map = window.WebGISMap.getMap();

        // Zoom in button
        const zoomInBtn = document.getElementById('zoom-in');
        if (zoomInBtn) {{
            zoomInBtn.addEventListener('click', function() {{
                map.zoomIn();
            }});
        }}

        // Zoom out button
        const zoomOutBtn = document.getElementById('zoom-out');
        if (zoomOutBtn) {{
            zoomOutBtn.addEventListener('click', function() {{
                map.zoomOut();
            }});
        }}

        // Home button
        const homeBtn = document.getElementById('home');
        if (homeBtn) {{
            homeBtn.addEventListener('click', function() {{
                if (window.WebGISMap && window.WebGISMap.fitMapToBounds) {{
                    window.WebGISMap.fitMapToBounds();
                }} else if (typeof WebGISConfig !== 'undefined') {{
                    const config = WebGISConfig.map;
                    map.setView(config.center, config.zoom);
                }}
            }});
        }}
    }}

    /**
     * Initialize fullscreen control
     */
    function initFullscreenControl() {{
        const fullscreenBtn = document.getElementById('fullscreen-btn');
        if (fullscreenBtn) {{
            fullscreenBtn.addEventListener('click', function() {{
                if (!document.fullscreenElement) {{
                    document.documentElement.requestFullscreen().catch(function(err) {{
                        console.error('Fullscreen error:', err);
                    }});
                }} else {{
                    if (document.exitFullscreen) {{
                        document.exitFullscreen();
                    }}
                }}
            }});

            // Update icon on fullscreen change
            document.addEventListener('fullscreenchange', function() {{
                const icon = fullscreenBtn.querySelector('i');
                if (document.fullscreenElement) {{
                    icon.classList.remove('fa-expand');
                    icon.classList.add('fa-compress');
                }} else {{
                    icon.classList.remove('fa-compress');
                    icon.classList.add('fa-expand');
                }}
            }});
        }}
    }}

    /**
     * Initialize location control
     */
    function initLocationControl() {{
        const locateBtn = document.getElementById('locate');
        if (locateBtn && 'geolocation' in navigator) {{
            locateBtn.addEventListener('click', function() {{
                locateBtn.classList.add('loading');
                navigator.geolocation.getCurrentPosition(
                    function(position) {{
                        const map = window.WebGISMap.getMap();
                        const lat = position.coords.latitude;
                        const lng = position.coords.longitude;
                        map.setView([lat, lng], 15);

                        // Add marker
                        L.marker([lat, lng]).addTo(map)
                            .bindPopup('Votre position')
                            .openPopup();

                        locateBtn.classList.remove('loading');
                    }},
                    function(error) {{
                        console.error('Geolocation error:', error);
                        locateBtn.classList.remove('loading');
                        alert("Impossible d'obtenir votre position");
                    }},
                    {{ enableHighAccuracy: true }}
                );
            }});
        }} else if (locateBtn) {{
            locateBtn.style.display = 'none';
        }}
    }}

    /**
     * Initialize measure controls
     */
    function initMeasureControls() {{
        const map = window.WebGISMap.getMap();

        // Distance measurement
        const distanceBtn = document.getElementById('measure-distance');
        if (distanceBtn) {{
            distanceBtn.addEventListener('click', function() {{
                toggleDistanceMeasurement();
            }});
        }}

        // Area measurement
        const areaBtn = document.getElementById('measure-area');
        if (areaBtn) {{
            areaBtn.addEventListener('click', function() {{
                toggleAreaMeasurement();
            }});
        }}
    }}

    /**
     * Toggle distance measurement
     */
    function toggleDistanceMeasurement() {{
        // Simple distance measurement implementation
        const map = window.WebGISMap.getMap();
        let measuring = false;
        let points = [];
        let markers = [];
        let lines = [];

        function addMarker(latlng) {{
            const marker = L.marker(latlng, {{
                draggable: true
            }}).addTo(map);

            marker.on('drag', function() {{
                updateMeasurement();
            }});

            markers.push(marker);
            points.push(latlng);

            if (points.length > 1) {{
                const line = L.polyline(points, {{
                    color: '#e74c3c',
                    weight: 3
                }}).addTo(map);
                lines.push(line);
            }}

            updateMeasurement();
        }}

        function updateMeasurement() {{
            let totalDistance = 0;
            for (let i = 1; i < points.length; i++) {{
                totalDistance += points[i-1].distanceTo(points[i]);
            }}

            if (markers.length > 0) {{
                const lastMarker = markers[markers.length - 1];
                lastMarker.bindPopup('Distance: ' + totalDistance.toFixed(2) + ' m').openPopup();
            }}
        }}

        function clearMeasurement() {{
            markers.forEach(function(m) {{ map.removeLayer(m); }});
            lines.forEach(function(l) {{ map.removeLayer(l); }});
            markers = [];
            lines = [];
            points = [];
        }}

        map.on('click', function(e) {{
            if (measuring) {{
                addMarker(e.latlng);
            }}
        }});

        measuring = !measuring;
        distanceBtn.classList.toggle('active', measuring);

        if (!measuring) {{
            clearMeasurement();
        }}
    }}

    /**
     * Toggle area measurement
     */
    function toggleAreaMeasurement() {{
        // Similar implementation for area measurement
        console.log('Area measurement toggled');
    }}

    // Export functions
    window.WebGISControls = {{
        init: initControls
    }};

    // NOTE: Do NOT auto-initialize here. app.js orchestrates init order.

}})();"""

        return javascript

    def _generate_scale_control_code(self, show: bool) -> str:
        """Generate scale control code."""
        if show:
            return """function addScaleControl() {
        const map = window.WebGISMap.getMap();
        L.control.scale({
            metric: true,
            imperial: false,
            position: 'bottomleft'
        }).addTo(map);
    }"""
        else:
            return """function addScaleControl() {
        // Scale control disabled
    }"""

    def _generate_scale_control(self, show: bool) -> str:
        """Generate scale control initialization."""
        if show:
            return "addScaleControl();"
        else:
            return "// Scale control disabled"

    def validate(self) -> tuple:
        """Validate JS controls generator configuration.

        :returns: Tuple of (is_valid, error_messages)
        """
        errors = []
        return (len(errors) == 0, errors)