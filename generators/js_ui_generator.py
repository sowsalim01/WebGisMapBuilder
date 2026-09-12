"""
JavaScript UI Generator - Generate user interface JavaScript
"""

import html
import json
from typing import Dict, List
from qgis.core import QgsMapLayer

from .base_generator import BaseGenerator

try:
    from ..core.style_manager import StyleManager
except (ImportError, ValueError):
    from core.style_manager import StyleManager


class JSUIGenerator(BaseGenerator):
    """Generator for user interface JavaScript."""

    def __init__(self, config: Dict):
        """Initialize the JS UI generator.

        :param config: Project configuration
        """
        super().__init__(config)
        self.style_manager = StyleManager()

    def generate(self, layers: List[QgsMapLayer], **kwargs) -> Dict:
        """Generate user interface JavaScript.

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
            javascript = self._generate_ui_js(layers)
            results['javascript'] = javascript
            results['success'] = True

        except Exception as e:
            results['errors'].append(f"JS UI generation error: {str(e)}")

        return results

    def _generate_ui_js(self, layers: List[QgsMapLayer]) -> str:
        """Generate user interface JavaScript.

        :param layers: List of QGIS layers
        :returns: JavaScript string
        """
        layer_ui_data = self._generate_layer_ui_data(layers)
        basemap_ui_data = self._generate_basemap_ui_data()
        legend_ui_data = self._generate_legend_ui_data(layers)

        javascript = f"""/**
 * User Interface Management
 * Sidebar, panels, tabs, theme, and responsive behavior
 */

(function() {{
    'use strict';

    let uiInitialized = false;

    /**
     * Initialize UI
     */
    function initUI() {{
        if (uiInitialized) return;
        uiInitialized = true;

        initSidebar();
        initRightPanel();
        initTabs();
        initTheme();
        initLayerUI();
        initBasemapUI();
        initLegendUI();
        initModals();
        initResponsive();
        console.log('UI initialized');
    }}

    /**
     * Initialize help and info modal
     */
    function initModals() {{
        const helpBtn = document.getElementById('help-btn');
        const settingsBtn = document.getElementById('settings-btn');
        const modalEl = document.getElementById('infoModal');

        function openModal() {{
            if (modalEl && typeof bootstrap !== 'undefined' && bootstrap.Modal) {{
                const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
                modal.show();
            }} else if (modalEl) {{
                modalEl.style.display = 'block';
                modalEl.classList.add('show');
            }}
        }}

        if (helpBtn) helpBtn.addEventListener('click', openModal);
        if (settingsBtn) settingsBtn.addEventListener('click', openModal);
    }}

    /**
     * Initialize sidebar
     */
    function initSidebar() {{
        const sidebar = document.getElementById('sidebar');
        const sidebarToggle = document.getElementById('sidebar-toggle');
        const navItems = document.querySelectorAll('.nav-item');

        // Toggle sidebar
        if (sidebarToggle) {{
            sidebarToggle.addEventListener('click', function() {{
                sidebar.classList.toggle('expanded');
                const icon = sidebarToggle.querySelector('i');
                if (sidebar.classList.contains('expanded')) {{
                    icon.classList.remove('fa-chevron-left');
                    icon.classList.add('fa-chevron-right');
                }} else {{
                    icon.classList.remove('fa-chevron-right');
                    icon.classList.add('fa-chevron-left');
                }}
            }});
        }}

        // Nav item clicks
        navItems.forEach(function(item) {{
            item.addEventListener('click', function() {{
                navItems.forEach(function(i) {{ i.classList.remove('active'); }});
                this.classList.add('active');

                const tool = this.getAttribute('data-tool');
                handleToolSelection(tool);
            }});
        }});
    }}

    /**
     * Handle tool selection
     */
    function handleToolSelection(tool) {{
        const map = window.WebGISMap.getMap();

        switch(tool) {{
            case 'map':
                // Default map view
                break;
            case 'search':
                const searchInput = document.getElementById('global-search');
                if (searchInput) {{
                    searchInput.focus();
                }}
                break;
            case 'filters':
                // Open filters panel
                const rightPanel = document.getElementById('right-panel');
                const filtersTab = document.querySelector('[data-tab="layers"]');
                if (rightPanel && filtersTab) {{
                    rightPanel.classList.remove('collapsed');
                    filtersTab.click();
                }}
                break;
            case 'location':
                const locateBtn = document.getElementById('locate');
                if (locateBtn) {{
                    locateBtn.click();
                }}
                break;
            case 'measure':
                const distanceBtn = document.getElementById('measure-distance');
                if (distanceBtn) {{
                    distanceBtn.click();
                }}
                break;
            case 'draw':
                enableDrawMode();
                break;
            case 'print':
                printMap();
                break;
            case 'share':
                shareMap();
                break;
        }}
    }}

    /**
     * Initialize right panel
     */
    function initRightPanel() {{
        const rightPanel = document.getElementById('right-panel');
        const panelToggle = document.getElementById('panel-toggle');

        if (panelToggle) {{
            panelToggle.addEventListener('click', function() {{
                rightPanel.classList.toggle('collapsed');
                const icon = panelToggle.querySelector('i');
                if (rightPanel.classList.contains('collapsed')) {{
                    icon.classList.remove('fa-chevron-right');
                    icon.classList.add('fa-chevron-left');
                }} else {{
                    icon.classList.remove('fa-chevron-left');
                    icon.classList.add('fa-chevron-right');
                }}
            }});
        }}
    }}

    /**
     * Initialize tabs
     */
    function initTabs() {{
        const tabBtns = document.querySelectorAll('.tab-btn');
        const tabPanes = document.querySelectorAll('.tab-pane');

        tabBtns.forEach(function(btn) {{
            btn.addEventListener('click', function() {{
                const tabId = this.getAttribute('data-tab');

                // Update buttons
                tabBtns.forEach(function(b) {{ b.classList.remove('active'); }});
                this.classList.add('active');

                // Update panes
                tabPanes.forEach(function(pane) {{ pane.classList.remove('active'); }});
                const targetPane = document.getElementById(tabId + '-tab');
                if (targetPane) {{
                    targetPane.classList.add('active');
                }}
            }});
        }});
    }}

    /**
     * Initialize theme toggle
     */
    function initTheme() {{
        const themeToggle = document.getElementById('theme-toggle');
        const html = document.documentElement;

        // Load saved theme
        const savedTheme = localStorage.getItem('webgis-theme') || 'light';
        html.setAttribute('data-theme', savedTheme);
        updateThemeIcon(savedTheme);

        if (themeToggle) {{
            themeToggle.addEventListener('click', function() {{
                const currentTheme = html.getAttribute('data-theme');
                const newTheme = currentTheme === 'light' ? 'dark' : 'light';

                html.setAttribute('data-theme', newTheme);
                localStorage.setItem('webgis-theme', newTheme);
                updateThemeIcon(newTheme);
            }});
        }}
    }}

    /**
     * Update theme icon
     */
    function updateThemeIcon(theme) {{
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {{
            const icon = themeToggle.querySelector('i');
            if (theme === 'dark') {{
                icon.classList.remove('fa-moon');
                icon.classList.add('fa-sun');
            }} else {{
                icon.classList.remove('fa-sun');
                icon.classList.add('fa-moon');
            }}
        }}
    }}

    /**
     * Initialize layer UI
     */
    function initLayerUI() {{
        const layerList = document.getElementById('layer-list');
        if (layerList) {{
            layerList.innerHTML = '';
        }}
        {layer_ui_data}
    }}

    /**
     * Initialize basemap UI
     */
    function initBasemapUI() {{
        {basemap_ui_data}
    }}

    /**
     * Initialize legend UI
     */
    function initLegendUI() {{
        const legendContainer = document.getElementById('legend-container') || document.getElementById('legend-content');
        if (legendContainer) {{
            legendContainer.innerHTML = '';
        }}
        {legend_ui_data}
    }}

    /**
     * Enable draw mode
     */
    function enableDrawMode() {{
        console.log('Draw mode enabled');
        // Implement draw functionality with Leaflet.draw
    }}

    /**
     * Print map
     */
    function printMap() {{
        window.print();
    }}

    /**
     * Share map
     */
    function shareMap() {{
        const url = window.location.href;
        if (navigator.share) {{
            navigator.share({{
                title: (typeof WebGISConfig !== 'undefined' ? WebGISConfig.project.title : 'WebGIS Map'),
                url: url
            }});
        }} else {{
            // Fallback: copy to clipboard
            navigator.clipboard.writeText(url).then(function() {{
                alert('URL copiée dans le presse-papier');
            }});
        }}
    }}

    /**
     * Initialize responsive behavior
     */
    function initResponsive() {{
        // Handle window resize
        window.addEventListener('resize', function() {{
            const map = window.WebGISMap.getMap();
            if (map) {{
                map.invalidateSize();
            }}
        }});

        // Mobile sidebar toggle
        if (window.innerWidth <= 768) {{
            const sidebar = document.getElementById('sidebar');
            if (sidebar) {{
                sidebar.classList.add('collapsed');
            }}
        }}
    }}

    /**
     * Hide/show panels for fullscreen mode
     */
    function togglePanels() {{
        const sidebar = document.getElementById('sidebar');
        const rightPanel = document.getElementById('right-panel');
        const header = document.querySelector('.webgis-header');

        sidebar.classList.toggle('hidden');
        rightPanel.classList.toggle('hidden');
        header.classList.toggle('hidden');

        // Invalidate map size after transition
        setTimeout(function() {{
            const map = window.WebGISMap.getMap();
            if (map) {{
                map.invalidateSize();
            }}
        }}, 300);
    }}

    // Export functions
    window.WebGISUI = {{
        init: initUI,
        togglePanels: togglePanels
    }};

    // NOTE: Do NOT auto-initialize here. app.js orchestrates init order.

}})();"""

        return javascript

    def _generate_layer_ui_data(self, layers: List[QgsMapLayer]) -> str:
        """Generate layer UI data with direct event binding."""
        layer_code = []

        for layer in layers:
            layer_id = self.get_layer_id(layer)
            layer_name = layer.name()
            cfg = self.get_config_value(f'layers.{layer.id()}', {})
            if not cfg:
                cfg = self.get_config_value(f'layers.{layer_id}', {})

            layer_name_esc = html.escape(layer_name)
            layer_name_js = json.dumps(layer_name_esc)
            layer_id_js = json.dumps(layer_id)
            is_checked = 'checked' if cfg.get('visible', True) else ''
            opacity_val = int(cfg.get('opacity', 1.0) * 100)

            layer_code.append(f"""
        // Layer: {layer_name_esc}
        (function() {{
            const layerItem = document.createElement('div');
            layerItem.className = 'layer-item';
            layerItem.innerHTML = `
                <div class="layer-header">
                    <label class="form-check form-switch m-0 d-flex align-items-center gap-2 flex-grow-1" style="cursor:pointer;">
                        <input type="checkbox" class="form-check-input layer-checkbox m-0" id="layer-checkbox-{layer_id}" {is_checked}>
                        <span class="layer-name">{layer_name_esc}</span>
                    </label>
                    <div class="layer-actions">
                        <button class="layer-action-btn layer-zoom-btn" title="Zoomer sur la couche">
                            <i class="fas fa-crosshairs"></i>
                        </button>
                    </div>
                </div>
                <div class="layer-controls">
                    <div class="layer-opacity">
                        <label>Opacité: <span class="opacity-val">{opacity_val}%</span></label>
                        <input type="range" class="layer-opacity-slider form-range" min="0" max="100" value="{opacity_val}">
                    </div>
                </div>
            `;

            const chk = layerItem.querySelector('.layer-checkbox');
            if (chk) {{
                chk.addEventListener('change', function() {{
                    window.WebGISLayers.toggleVisibility({layer_name_js});
                }});
            }}

            const zoomBtn = layerItem.querySelector('.layer-zoom-btn');
            if (zoomBtn) {{
                zoomBtn.addEventListener('click', function() {{
                    window.WebGISLayers.zoomToLayer({layer_name_js});
                }});
            }}

            const slider = layerItem.querySelector('.layer-opacity-slider');
            const opacityLabel = layerItem.querySelector('.opacity-val');
            if (slider) {{
                slider.addEventListener('input', function() {{
                    const val = parseFloat(this.value) / 100;
                    if (opacityLabel) opacityLabel.textContent = this.value + '%';
                    window.WebGISLayers.setOpacity({layer_name_js}, val);
                }});
            }}

            const layerList = document.getElementById('layer-list');
            if (layerList) {{
                layerList.appendChild(layerItem);
            }}
        }})();""")

        return "\n".join(layer_code) if layer_code else "        // No layers to display"

    def _generate_basemap_ui_data(self) -> str:
        """Generate basemap UI data."""
        return """        const basemapGrid = document.getElementById('basemap-grid');
        if (basemapGrid) {
            basemapGrid.innerHTML = '';
            const basemaps = [
                { name: 'OpenStreetMap', id: 'osm', preview: 'https://a.tile.openstreetmap.org/0/0/0.png' },
                { name: 'CartoDB Positron', id: 'carto_positron', preview: 'https://a.basemaps.cartocdn.com/light_all/0/0/0.png' },
                { name: 'CartoDB Dark', id: 'carto_dark', preview: 'https://a.basemaps.cartocdn.com/dark_all/0/0/0.png' },
                { name: 'ESRI World Imagery', id: 'esri_world', preview: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/0/0/0' }
            ];

            basemaps.forEach(function(basemap) {
                const basemapItem = document.createElement('div');
                basemapItem.className = 'basemap-item';
                basemapItem.setAttribute('data-basemap', basemap.id);
                basemapItem.innerHTML = `
                    <div class="basemap-preview" style="background-image: url('${basemap.preview}')"></div>
                    <div class="basemap-name">${escapeHtml(basemap.name)}</div>
                `;

                basemapItem.addEventListener('click', function() {
                    document.querySelectorAll('.basemap-item').forEach(function(item) {
                        item.classList.remove('active');
                    });
                    this.classList.add('active');
                    window.WebGISMap.changeBasemap(basemap.name);
                });

                basemapGrid.appendChild(basemapItem);
            });

            // Set default active
            const defaultBasemap = (typeof WebGISConfig !== 'undefined' && WebGISConfig.basemap) ? WebGISConfig.basemap.default : 'osm';
            const defaultItem = document.querySelector(`[data-basemap="${defaultBasemap}"]`);
            if (defaultItem) {
                defaultItem.classList.add('active');
            }
        }

        /**
         * Escape HTML special characters
         */
        function escapeHtml(str) {
            return str
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;')
                .replace(/'/g, '&#039;');
        }"""

    def _generate_legend_ui_data(self, layers: List[QgsMapLayer]) -> str:
        """Generate dynamic legend UI data from active layer styles."""
        legend_html = []
        for layer in layers:
            items = self.style_manager.extract_legend_items(layer)
            if items:
                lname = html.escape(layer.name())
                legend_html.append(f'<div class="legend-group"><div class="legend-layer-title">{lname}</div>')
                for item in items:
                    lbl = html.escape(str(item.get('label', '')))
                    col = str(item.get('color', '#3388ff'))
                    gtype = str(item.get('type', 'Polygon'))
                    radius = "50%" if gtype == 'Point' else "3px"
                    legend_html.append(
                        f'<div class="legend-row">'
                        f'<span class="legend-swatch" style="background:{col}; border-radius:{radius};"></span>'
                        f'<span class="legend-text">{lbl}</span>'
                        f'</div>'
                    )
                legend_html.append('</div>')

        if not legend_html:
            escaped_content = json.dumps('<p class="text-muted small p-2">Aucune donnée de légende disponible.</p>')
        else:
            escaped_content = json.dumps("".join(legend_html))

        return f"""        const legendContent = document.getElementById('legend-content');
        if (legendContent) {{
            legendContent.innerHTML = {escaped_content};
        }}"""

    def validate(self) -> tuple:
        """Validate JS UI generator configuration.

        :returns: Tuple of (is_valid, error_messages)
        """
        errors = []
        return (len(errors) == 0, errors)