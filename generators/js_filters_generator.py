"""
JavaScript Filters Generator - Generate filter functionality
"""

from typing import Dict, List
from qgis.core import QgsMapLayer

from .base_generator import BaseGenerator


class JSFiltersGenerator(BaseGenerator):
    """Generator for filter functionality JavaScript."""

    def __init__(self, config: Dict):
        """Initialize the JS filters generator.

        :param config: Project configuration
        """
        super().__init__(config)

    def generate(self, layers: List[QgsMapLayer], **kwargs) -> Dict:
        """Generate filter functionality JavaScript.

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
            javascript = self._generate_filters_js(layers)
            results['javascript'] = javascript
            results['success'] = True

        except Exception as e:
            results['errors'].append(f"JS filters generation error: {str(e)}")

        return results

    def _generate_filters_js(self, layers: List[QgsMapLayer]) -> str:
        """Generate filter functionality JavaScript.

        :param layers: List of QGIS layers
        :returns: JavaScript string
        """
        filter_definitions = self._generate_filter_definitions(layers)

        javascript = f"""/**
 * Dynamic Filter System
 * Generate and manage filters based on layer attributes
 */

(function() {{
    'use strict';

    let activeFilters = {{}};
    let filtersInitialized = false;

    /**
     * Initialize filter system
     */
    function initFilters() {{
        if (filtersInitialized) return;
        filtersInitialized = true;
        generateFilterUI();
        setupFilterEvents();
        console.log('Filters initialized');
    }}

    /**
     * Generate filter UI based on layer attributes
     */
    function generateFilterUI() {{
        {filter_definitions}
    }}

    /**
     * Setup filter event handlers
     */
    function setupFilterEvents() {{
        // Filter dropdown changes
        document.querySelectorAll('.filter-select').forEach(function(select) {{
            select.addEventListener('change', function() {{
                applyFilters();
            }});
        }});

        // Filter checkbox changes
        document.querySelectorAll('.filter-checkbox').forEach(function(checkbox) {{
            checkbox.addEventListener('change', function() {{
                applyFilters();
            }});
        }});
    }}

    /**
     * Apply active filters to layers
     */
    function applyFilters() {{
        const map = window.WebGISMap.getMap();
        const layerGroups = window.WebGISMap.getLayerGroups();

        Object.keys(activeFilters).forEach(function(layerId) {{
            const layer = layerGroups.overlays[layerId];
            const filters = activeFilters[layerId];

            if (layer && filters) {{
                layer.eachLayer(function(sublayer) {{
                    if (sublayer.feature && sublayer.feature.properties) {{
                        const props = sublayer.feature.properties;
                        let visible = true;

                        // Apply each filter
                        Object.keys(filters).forEach(function(field) {{
                            const filterValue = filters[field];
                            if (filterValue && filterValue !== 'all') {{
                                if (String(props[field]) !== filterValue) {{
                                    visible = false;
                                }}
                            }}
                        }});

                        if (visible) {{
                            if (!map.hasLayer(sublayer)) {{
                                sublayer.addTo(map);
                            }}
                        }} else {{
                            if (map.hasLayer(sublayer)) {{
                                map.removeLayer(sublayer);
                            }}
                        }}
                    }}
                }});
            }}
        }});
    }}

    /**
     * Add filter for a layer
     */
    function addFilter(layerId, field, value) {{
        if (!activeFilters[layerId]) {{
            activeFilters[layerId] = {{}};
        }}
        activeFilters[layerId][field] = value;
    }}

    /**
     * Remove filter for a layer
     */
    function removeFilter(layerId, field) {{
        if (activeFilters[layerId]) {{
            delete activeFilters[layerId][field];
        }}
    }}

    /**
     * Clear all filters for a layer
     */
    function clearLayerFilters(layerId) {{
        delete activeFilters[layerId];
    }}

    /**
     * Clear all filters
     */
    function clearAllFilters() {{
        activeFilters = {{}};
        applyFilters();
    }}

    /**
     * Get unique values for a field
     */
    function getUniqueValues(layerId, field) {{
        const layerGroups = window.WebGISMap.getLayerGroups();
        const layer = layerGroups.overlays[layerId];
        const values = new Set();

        if (layer) {{
            layer.eachLayer(function(sublayer) {{
                if (sublayer.feature && sublayer.feature.properties) {{
                    const value = sublayer.feature.properties[field];
                    if (value !== undefined && value !== null) {{
                        values.add(String(value));
                    }}
                }}
            }});
        }}

        return Array.from(values).sort();
    }}

    // Export functions
    window.WebGISFilters = {{
        init: initFilters,
        addFilter: addFilter,
        removeFilter: removeFilter,
        clearLayerFilters: clearLayerFilters,
        clearAllFilters: clearAllFilters,
        getUniqueValues: getUniqueValues
    }};

    // Auto-initialize when filters tab is activated
    document.addEventListener('DOMContentLoaded', function() {{
        const filtersTab = document.querySelector('[data-tool="filters"]');
        if (filtersTab) {{
            filtersTab.addEventListener('click', function() {{
                setTimeout(initFilters, 100);
            }});
        }}
    }});

}})();"""

        return javascript

    def _generate_filter_definitions(self, layers: List[QgsMapLayer]) -> str:
        """Generate filter definitions from layers."""
        filter_code = []

        for layer in layers:
            if layer.type() == layer.VectorLayer:
                layer_id = self.get_layer_id(layer)
                layer_name = layer.name()

                # Get first few string fields for filtering
                string_fields = []
                for field in layer.fields():
                    if field.typeName() in ['String', 'QString']:
                        string_fields.append(field.name())
                        if len(string_fields) >= 3:  # Limit to 3 fields per layer
                            break

                for field in string_fields:
                    filter_code.append(f"""
        // Filter for {layer_name} - {field}
        const filterSelect_{layer_id}_{field} = document.getElementById('filter-{layer_id}-{field}');
        if (filterSelect_{layer_id}_{field}) {{
            const uniqueValues = window.WebGISFilters.getUniqueValues('{layer_id}', '{field}');
            uniqueValues.forEach(function(value) {{
                const option = document.createElement('option');
                option.value = value;
                option.textContent = value;
                filterSelect_{layer_id}_{field}.appendChild(option);
            }});
        }}""")

        return "\n".join(filter_code) if filter_code else "        // No filters available"

    def validate(self) -> tuple:
        """Validate JS filters generator configuration.

        :returns: Tuple of (is_valid, error_messages)
        """
        errors = []
        return (len(errors) == 0, errors)