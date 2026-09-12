"""
JavaScript App Generator - Generate main application JavaScript
"""

from typing import Dict, List
from qgis.core import QgsMapLayer

from .base_generator import BaseGenerator


class JSAppGenerator(BaseGenerator):
    """Generator for main application JavaScript."""

    def __init__(self, config: Dict):
        """Initialize the JS app generator.

        :param config: Project configuration
        """
        super().__init__(config)

    def generate(self, layers: List[QgsMapLayer], **kwargs) -> Dict:
        """Generate main application JavaScript.

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
            javascript = self._generate_app_js()
            results['javascript'] = javascript
            results['success'] = True

        except Exception as e:
            results['errors'].append(f"JS app generation error: {str(e)}")

        return results

    def _generate_app_js(self) -> str:
        """Generate main application JavaScript.

        :returns: JavaScript string
        """
        javascript = """/**
 * WebGIS Professional - Main Application
 * WebGisMapBuilder Generated Application
 */

(function() {
    'use strict';

    /**
     * Application state
     */
    const AppState = {
        initialized: false,
        loading: false,
        currentTool: 'map',
        theme: 'light'
    };

    /**
     * Initialize application
     */
    function initApp() {
        console.log('WebGIS Professional - Initializing...');

        // Show loading state
        showLoading();

        // Initialize components in order
        Promise.all([
            initMap(),
            initUI(),
            initLayers(),
            initControls(),
            initSearch(),
            initFilters()
        ]).then(function() {
            AppState.initialized = true;
            hideLoading();
            if (window.WebGISMap && window.WebGISMap.fitMapToBounds) {
                setTimeout(function() {
                    window.WebGISMap.fitMapToBounds();
                }, 200);
            }
            console.log('WebGIS Professional - Ready');
        }).catch(function(error) {
            console.error('Initialization error:', error);
            hideLoading();
            showError('Erreur lors de l\\'initialisation de l\\'application');
        });
    }

    /**
     * Initialize map
     */
    function initMap() {
        return new Promise(function(resolve) {
            if (window.WebGISMap && window.WebGISMap.init) {
                window.WebGISMap.init();
                resolve();
            } else {
                setTimeout(function() {
                    initMap().then(resolve);
                }, 100);
            }
        });
    }

    /**
     * Initialize UI
     */
    function initUI() {
        return new Promise(function(resolve) {
            if (window.WebGISUI && window.WebGISUI.init) {
                window.WebGISUI.init();
                resolve();
            } else {
                setTimeout(function() {
                    initUI().then(resolve);
                }, 100);
            }
        });
    }

    /**
     * Initialize layers
     */
    function initLayers() {
        return new Promise(function(resolve) {
            if (window.WebGISLayers && window.WebGISLayers.init) {
                window.WebGISLayers.init();
                resolve();
            } else {
                setTimeout(function() {
                    initLayers().then(resolve);
                }, 100);
            }
        });
    }

    /**
     * Initialize controls
     */
    function initControls() {
        return new Promise(function(resolve) {
            if (window.WebGISControls && window.WebGISControls.init) {
                window.WebGISControls.init();
                resolve();
            } else {
                setTimeout(function() {
                    initControls().then(resolve);
                }, 100);
            }
        });
    }

    /**
     * Initialize search
     */
    function initSearch() {
        return new Promise(function(resolve) {
            if (window.WebGISSearch && window.WebGISSearch.init) {
                window.WebGISSearch.init();
                resolve();
            } else {
                setTimeout(function() {
                    initSearch().then(resolve);
                }, 100);
            }
        });
    }

    /**
     * Initialize filters
     */
    function initFilters() {
        return new Promise(function(resolve) {
            if (window.WebGISFilters && window.WebGISFilters.init) {
                window.WebGISFilters.init();
                resolve();
            } else {
                setTimeout(function() {
                    initFilters().then(resolve);
                }, 100);
            }
        });
    }

    /**
     * Show loading state
     */
    function showLoading() {
        AppState.loading = true;
        document.body.classList.add('loading');
    }

    /**
     * Hide loading state
     */
    function hideLoading() {
        AppState.loading = false;
        document.body.classList.remove('loading');
    }

    /**
     * Show error message
     */
    function showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        errorDiv.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: #e74c3c;
            color: white;
            padding: 20px;
            border-radius: 8px;
            z-index: 10000;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        `;
        document.body.appendChild(errorDiv);

        setTimeout(function() {
            errorDiv.remove();
        }, 5000);
    }

    /**
     * Get application state
     */
    function getState() {
        return AppState;
    }

    /**
     * Set current tool
     */
    function setCurrentTool(tool) {
        AppState.currentTool = tool;
    }

    /**
     * Get current tool
     */
    function getCurrentTool() {
        return AppState.currentTool;
    }

    // Export application API
    window.WebGISApp = {
        init: initApp,
        getState: getState,
        setCurrentTool: setCurrentTool,
        getCurrentTool: getCurrentTool
    };

    // Auto-initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initApp);
    } else {
        initApp();
    }

    // Handle page visibility changes
    document.addEventListener('visibilitychange', function() {
        if (document.visibilityState === 'visible' && AppState.initialized) {
            const map = window.WebGISMap.getMap();
            if (map) {
                map.invalidateSize();
            }
        }
    });

    // Handle before unload
    window.addEventListener('beforeunload', function() {
        console.log('WebGIS Professional - Shutting down');
    });

})();"""

        return javascript

    def validate(self) -> tuple:
        """Validate JS app generator configuration.

        :returns: Tuple of (is_valid, error_messages)
        """
        errors = []
        return (len(errors) == 0, errors)