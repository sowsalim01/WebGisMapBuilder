"""
JavaScript Search Generator - Generate search functionality
"""

import html
from typing import Dict, List
from qgis.core import QgsMapLayer

from .base_generator import BaseGenerator


class JSSearchGenerator(BaseGenerator):
    """Generator for search functionality JavaScript."""

    def __init__(self, config: Dict):
        """Initialize the JS search generator.

        :param config: Project configuration
        """
        super().__init__(config)

    def generate(self, layers: List[QgsMapLayer], **kwargs) -> Dict:
        """Generate search functionality JavaScript.

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
            javascript = self._generate_search_js(layers)
            results['javascript'] = javascript
            results['success'] = True

        except Exception as e:
            results['errors'].append(f"JS search generation error: {str(e)}")

        return results

    def _generate_search_js(self, layers: List[QgsMapLayer]) -> str:
        """Generate search functionality JavaScript.

        :param layers: List of QGIS layers
        :returns: JavaScript string
        """
        layer_search_data = self._generate_layer_search_data(layers)

        javascript = f"""/**
 * Global Search Functionality
 * Search across layers, features, attributes, and locations
 */

(function() {{
    'use strict';

    let searchIndex = [];
    let searchInitialized = false;

    function escapeHtml(str) {{
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }}

    /**
     * Index a feature from a loaded layer
     */
    function indexFeature(layerName, feature, layerRef) {{
        if (!feature || !feature.properties) return;
        const props = feature.properties;
        const keys = Object.keys(props);
        if (keys.length === 0) return;

        // Determine best title/label
        const priorityFields = ['nom', 'name', 'title', 'titre', 'label', 'libelle', 'designation', 'commune', 'ville', 'id', 'code'];
        let title = '';
        for (let i = 0; i < priorityFields.length; i++) {{
            const match = keys.find(function(k) {{ return k.toLowerCase() === priorityFields[i]; }});
            if (match && props[match] !== null && props[match] !== undefined && String(props[match]).trim() !== '') {{
                title = String(props[match]).trim();
                break;
            }}
        }}
        if (!title) {{
            for (let i = 0; i < keys.length; i++) {{
                const val = props[keys[i]];
                if (val !== null && val !== undefined && String(val).trim() !== '') {{
                    title = String(val).trim();
                    break;
                }}
            }}
        }}
        if (!title) title = layerName + ' #' + (searchIndex.length + 1);

        // Build full search terms from all properties
        const searchTerms = [title, layerName];
        keys.forEach(function(k) {{
            const v = props[k];
            if (v !== null && v !== undefined) {{
                searchTerms.push(String(v));
            }}
        }});
        const searchText = searchTerms.join(' ').toLowerCase();

        searchIndex.push({{
            title: title,
            layerName: layerName,
            text: searchText,
            layerRef: layerRef,
            feature: feature,
            properties: props
        }});
    }}

    /**
     * Initialize search functionality
     */
    function initSearch() {{
        if (searchInitialized) return;
        searchInitialized = true;
        buildSearchIndex();
        setupSearchUI();
        console.log('Search initialized');
    }}

    /**
     * Build initial search index from layer schemas
     */
    function buildSearchIndex() {{
        {layer_search_data}
    }}

    /**
     * Setup search UI
     */
    function setupSearchUI() {{
        const searchInput = document.getElementById('global-search');
        const searchResultsDiv = document.getElementById('search-results');

        if (!searchInput || !searchResultsDiv) return;

        let debounceTimer = null;

        // Search on input with small debounce
        searchInput.addEventListener('input', function(e) {{
            clearTimeout(debounceTimer);
            const query = e.target.value.trim();
            if (query.length >= 2) {{
                debounceTimer = setTimeout(function() {{
                    performSearch(query);
                }}, 150);
            }} else {{
                searchResultsDiv.classList.remove('active');
                searchResultsDiv.innerHTML = '';
            }}
        }});

        // Clear results on click outside
        document.addEventListener('click', function(e) {{
            if (!searchInput.contains(e.target) && !searchResultsDiv.contains(e.target)) {{
                searchResultsDiv.classList.remove('active');
            }}
        }});

        // Handle keyboard navigation
        searchInput.addEventListener('keydown', function(e) {{
            if (e.key === 'Escape') {{
                searchResultsDiv.classList.remove('active');
            }} else if (e.key === 'Enter') {{
                e.preventDefault();
                const firstItem = searchResultsDiv.querySelector('.search-result-item[data-index]');
                if (firstItem) {{
                    firstItem.click();
                }}
            }}
        }});
    }}

    /**
     * Perform search
     */
    function performSearch(query) {{
        const searchResultsDiv = document.getElementById('search-results');
        if (!searchResultsDiv) return;

        const lowerQuery = query.toLowerCase().trim();
        if (lowerQuery.length < 2) {{
            searchResultsDiv.classList.remove('active');
            return;
        }}

        // Filter local search index
        const results = searchIndex.filter(function(item) {{
            return item.text.includes(lowerQuery);
        }});

        displaySearchResults(results, query);
    }}

    /**
     * Display search results
     */
    function displaySearchResults(results, query) {{
        const searchResultsDiv = document.getElementById('search-results');
        if (!searchResultsDiv) return;

        let html = '';

        if (results.length === 0) {{
            html += '<div class="p-3 text-center text-muted small">';
            html += '<i class="fas fa-search-location mb-1 d-block fs-5 opacity-50"></i>';
            html += 'Aucune entité trouvée dans les couches';
            html += '</div>';
        }} else {{
            const maxResults = 10;
            const shown = results.slice(0, maxResults);

            shown.forEach(function(item, index) {{
                html += '<div class="search-result-item" data-index="' + index + '" style="cursor: pointer;">';
                html += '  <div class="d-flex align-items-center justify-content-between">';
                html += '    <div class="search-item-info text-truncate" style="max-width: 320px;">';
                html += '      <strong class="d-block text-truncate">' + escapeHtml(item.title) + '</strong>';
                html += '      <small class="text-muted"><i class="fas fa-layer-group me-1"></i>' + escapeHtml(item.layerName) + '</small>';
                html += '    </div>';
                html += '    <span class="badge bg-primary-subtle text-primary rounded-pill small ms-2"><i class="fas fa-crosshairs me-1"></i>Zoom</span>';
                html += '  </div>';
                html += '</div>';
            }});

            if (results.length > maxResults) {{
                html += '<div class="px-3 py-1 text-muted small bg-light border-top text-center">';
                html += '+ ' + (results.length - maxResults) + ' autres résultats...';
                html += '</div>';
            }}
        }}

        // Nominatim Geocoding Fallback Option
        html += '<div class="search-result-item bg-light border-top" id="search-nominatim-btn" style="cursor: pointer;">';
        html += '  <div class="d-flex align-items-center gap-2 text-primary small py-1">';
        html += '    <i class="fas fa-globe"></i>';
        html += '    <span>Rechercher <strong>"' + escapeHtml(query) + '"</strong> sur la carte mondiale</span>';
        html += '  </div>';
        html += '</div>';

        searchResultsDiv.innerHTML = html;
        searchResultsDiv.classList.add('active');

        // Click handlers on local results
        const items = searchResultsDiv.querySelectorAll('.search-result-item[data-index]');
        items.forEach(function(el) {{
            el.addEventListener('click', function() {{
                const idx = parseInt(this.getAttribute('data-index'), 10);
                const selected = results[idx];
                if (selected) {{
                    selectSearchResult(selected);
                }}
                searchResultsDiv.classList.remove('active');
            }});
        }});

        // Click handler on Nominatim option
        const nominatimBtn = document.getElementById('search-nominatim-btn');
        if (nominatimBtn) {{
            nominatimBtn.addEventListener('click', function() {{
                nominatimBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Recherche mondiale...';
                searchLocation(query).then(function(places) {{
                    if (places && places.length > 0) {{
                        const map = window.WebGISMap.getMap();
                        const p = places[0];
                        map.setView([p.lat, p.lng], 14);
                        L.popup()
                            .setLatLng([p.lat, p.lng])
                            .setContent('<div class="fw-bold p-1"><i class="fas fa-map-pin text-danger me-1"></i>' + escapeHtml(p.name) + '</div>')
                            .openOn(map);
                    }} else {{
                        alert('Lieu non trouvé');
                    }}
                    searchResultsDiv.classList.remove('active');
                }}).catch(function(err) {{
                    console.error('Nominatim search error:', err);
                    searchResultsDiv.classList.remove('active');
                }});
            }});
        }}
    }}

    /**
     * Select search result and zoom to feature
     */
    function selectSearchResult(item) {{
        const map = window.WebGISMap.getMap();
        if (!map) return;

        // If it's a layer-only target
        if (item.isLayerTarget) {{
            if (window.WebGISLayers && window.WebGISLayers.zoomToLayer) {{
                window.WebGISLayers.zoomToLayer(item.layerName);
            }}
            return;
        }}

        // Ensure parent layer is visible
        const layerGroups = window.WebGISMap.getLayerGroups();
        if (layerGroups && layerGroups.overlays) {{
            const parentLayer = layerGroups.overlays[item.layerName];
            if (parentLayer && !map.hasLayer(parentLayer)) {{
                parentLayer.addTo(map);
                const chk = document.querySelector('.layer-checkbox[id*="' + item.layerName + '"]');
                if (chk) chk.checked = true;
            }}
        }}

        // Zoom to feature
        if (item.layerRef) {{
            if (item.layerRef.getBounds) {{
                try {{
                    const b = item.layerRef.getBounds();
                    if (b && typeof b.isValid === 'function' && b.isValid()) {{
                        map.fitBounds(b, {{ padding: [60, 60], maxZoom: 16 }});
                    }}
                }} catch (e) {{}}
            }} else if (item.layerRef.getLatLng) {{
                map.setView(item.layerRef.getLatLng(), 16);
            }}

            // Open popup with slight delay for smooth pan
            setTimeout(function() {{
                if (item.layerRef.openPopup) {{
                    item.layerRef.openPopup();
                }}
            }}, 250);
        }}
    }}

    /**
     * Add location search (Nominatim)
     */
    function searchLocation(query) {{
        return fetch('https://nominatim.openstreetmap.org/search?format=json&q=' + encodeURIComponent(query))
            .then(function(response) {{ return response.json(); }})
            .then(function(data) {{
                return data.map(function(item) {{
                    return {{
                        name: item.display_name,
                        value: item.display_name,
                        lat: parseFloat(item.lat),
                        lng: parseFloat(item.lon),
                        layer: 'Location'
                    }};
                }});
            }});
    }}

    // Export functions
    window.WebGISSearch = {{
        init: initSearch,
        indexFeature: indexFeature,
        performSearch: performSearch,
        searchLocation: searchLocation
    }};

    // NOTE: Do NOT auto-initialize here. app.js orchestrates init order.

}})();"""

        return javascript

    def _generate_layer_search_data(self, layers: List[QgsMapLayer]) -> str:
        """Generate search data from layer names."""
        import json
        search_data = []

        for layer in layers:
            layer_name = html.escape(layer.name())
            layer_name_js = json.dumps(layer_name)

            if layer.type() == layer.VectorLayer:
                search_data.append(
                    f"        searchIndex.push({{ title: {layer_name_js}, layerName: {layer_name_js}, text: {layer_name_js}.toLowerCase(), isLayerTarget: true }});"
                )

        return "\n".join(search_data) if search_data else "        // No initial layer targets"

    def validate(self) -> tuple:
        """Validate JS search generator configuration.

        :returns: Tuple of (is_valid, error_messages)
        """
        errors = []
        return (len(errors) == 0, errors)