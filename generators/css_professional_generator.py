"""
Professional CSS Generator - Generate modern WebGIS CSS styles
"""

from typing import Dict, List
from qgis.core import QgsMapLayer

from .base_generator import BaseGenerator


class ProfessionalCSSGenerator(BaseGenerator):
    """Generator for professional WebGIS CSS styles."""

    def __init__(self, config: Dict):
        """Initialize the professional CSS generator.

        :param config: Project configuration
        """
        super().__init__(config)

    def generate(self, layers: List[QgsMapLayer], **kwargs) -> Dict:
        """Generate professional CSS styles.

        :param layers: List of QGIS layers
        :param kwargs: Additional parameters
        :returns: Dictionary with generation results
        """
        results = {
            'success': False,
            'css': '',
            'errors': []
        }

        try:
            css = self._generate_professional_css()
            results['css'] = css
            results['success'] = True

        except Exception as e:
            results['errors'].append(f"Professional CSS generation error: {str(e)}")

        return results

    def _generate_professional_css(self) -> str:
        """Generate professional WebGIS CSS styles.

        :returns: CSS string
        """
        theme = self.get_config_value('theme.name', 'professional')
        primary_color = self.get_config_value('theme.primary_color', '#2c3e50')
        secondary_color = self.get_config_value('theme.secondary_color', '#3498db')

        css = f"""/* ============================================
   PROFESSIONAL WEBGIS CSS - Modern & Elegant
   ============================================ */

/* CSS Variables - Theme System */
:root {{
    --primary-color: {primary_color};
    --secondary-color: {secondary_color};
    --accent-color: #6366f1;
    --success-color: #10b981;
    --warning-color: #f59e0b;
    --danger-color: #ef4444;
    
    --bg-primary: #ffffff;
    --bg-secondary: #f8fafc;
    --bg-tertiary: #f1f5f9;
    --bg-dark: #0f172a;
    --bg-glass: rgba(255, 255, 255, 0.88);
    --bg-glass-card: rgba(255, 255, 255, 0.75);
    --glass-blur: blur(14px);
    
    --text-primary: #0f172a;
    --text-secondary: #64748b;
    --text-light: #ffffff;
    
    --border-color: rgba(0, 0, 0, 0.08);
    --border-glass: rgba(255, 255, 255, 0.5);
    --border-radius: 10px;
    --border-radius-sm: 6px;
    --border-radius-lg: 16px;
    
    --shadow-sm: 0 2px 4px rgba(0,0,0,0.04);
    --shadow-md: 0 6px 18px rgba(0,0,0,0.08);
    --shadow-lg: 0 16px 36px rgba(0,0,0,0.12);
    
    --transition-fast: 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    --transition-normal: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    --transition-slow: 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    
    --header-height: 62px;
    --sidebar-width: 60px;
    --sidebar-expanded-width: 200px;
    --right-panel-width: 340px;
}}

/* Dark Theme */
[data-theme="dark"] {{
    --bg-primary: #0f172a;
    --bg-secondary: #1e293b;
    --bg-tertiary: #334155;
    --bg-dark: #020617;
    --bg-glass: rgba(15, 23, 42, 0.88);
    --bg-glass-card: rgba(30, 41, 59, 0.75);
    
    --text-primary: #f8fafc;
    --text-secondary: #94a3b8;
    --text-light: #ffffff;
    
    --border-color: rgba(255, 255, 255, 0.1);
    --border-glass: rgba(255, 255, 255, 0.08);
    
    --shadow-sm: 0 2px 4px rgba(0,0,0,0.25);
    --shadow-md: 0 6px 18px rgba(0,0,0,0.35);
    --shadow-lg: 0 16px 36px rgba(0,0,0,0.45);
}}

/* ============================================
   RESET & BASE STYLES
   ============================================ */

* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

html, body {{
    height: 100%;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    font-size: 14px;
    line-height: 1.6;
    color: var(--text-primary);
    background-color: var(--bg-primary);
    overflow: hidden;
}}

body {{
    display: flex;
    flex-direction: column;
}}

/* ============================================
   HEADER STYLES
   ============================================ */

.webgis-header {{
    height: var(--header-height);
    background: var(--bg-glass);
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    border-bottom: 1px solid var(--border-color);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 20px;
    box-shadow: var(--shadow-sm);
    z-index: 1000;
    transition: background var(--transition-fast), border-color var(--transition-fast);
}}

.header-left {{
    display: flex;
    align-items: center;
    gap: 16px;
}}

.logo {{
    display: flex;
    align-items: center;
    gap: 10px;
    text-decoration: none;
}}

.logo-icon-wrap {{
    width: 36px;
    height: 36px;
    border-radius: 10px;
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    color: #ffffff;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 17px;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}}

.logo-text-wrap {{
    display: flex;
    align-items: center;
    gap: 6px;
}}

.logo-brand {{
    font-family: 'Outfit', -apple-system, sans-serif;
    font-size: 16px;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.02em;
}}

.logo-badge {{
    font-size: 10px;
    text-transform: uppercase;
    font-weight: 700;
    background: linear-gradient(135deg, var(--secondary-color), var(--accent-color));
    color: #ffffff;
    padding: 2px 6px;
    border-radius: 4px;
}}

.project-info {{
    display: flex;
    flex-direction: column;
    border-left: 1px solid var(--border-color);
    padding-left: 14px;
}}

.project-title {{
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0;
    line-height: 1.2;
}}

.project-subtitle {{
    font-size: 11px;
    color: var(--text-secondary);
    margin: 0;
    line-height: 1.2;
}}

.header-center {{
    flex: 1;
    max-width: 540px;
    margin: 0 20px;
}}

.search-container {{
    position: relative;
    width: 100%;
}}

.search-icon {{
    position: absolute;
    left: 14px;
    top: 50%;
    transform: translateY(-50%);
    color: var(--text-secondary);
    font-size: 14px;
    pointer-events: none;
}}

.search-input {{
    width: 100%;
    padding: 9px 80px 9px 40px;
    border: 1px solid var(--border-color);
    border-radius: 20px;
    background: var(--bg-secondary);
    color: var(--text-primary);
    font-size: 13px;
    transition: all var(--transition-fast);
}}

.search-input:focus {{
    outline: none;
    border-color: var(--secondary-color);
    background: var(--bg-primary);
    box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.15);
}}

.search-badge {{
    position: absolute;
    right: 12px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    background: var(--bg-tertiary);
    color: var(--text-secondary);
    padding: 2px 8px;
    border-radius: 10px;
    pointer-events: none;
}}

.search-results {{
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    box-shadow: var(--shadow-lg);
    margin-top: 6px;
    max-height: 300px;
    overflow-y: auto;
    display: none;
    z-index: 1001;
}}

.search-results.active {{
    display: block;
}}

.search-result-item {{
    padding: 10px 14px;
    cursor: pointer;
    transition: background var(--transition-fast);
    border-bottom: 1px solid var(--border-color);
    font-size: 13px;
}}

.search-result-item:hover {{
    background: var(--bg-secondary);
    color: var(--secondary-color);
}}

.search-result-item:last-child {{
    border-bottom: none;
}}

.header-right {{
    display: flex;
    align-items: center;
    gap: 8px;
}}

.header-btn {{
    width: 36px;
    height: 36px;
    border: 1px solid var(--border-color);
    background: var(--bg-secondary);
    color: var(--text-primary);
    border-radius: 10px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all var(--transition-fast);
    font-size: 14px;
}}

.header-btn:hover {{
    background: var(--primary-color);
    color: #ffffff;
    border-color: var(--primary-color);
    transform: translateY(-2px);
    box-shadow: 0 4px 10px rgba(0,0,0,0.12);
}}

/* ============================================
   MAIN CONTAINER
   ============================================ */

.webgis-container {{
    display: flex;
    flex: 1;
    height: calc(100vh - var(--header-height));
    overflow: hidden;
    position: relative;
}}

/* ============================================
   SIDEBAR STYLES (Floating Glassmorphism)
   ============================================ */

.sidebar {{
    width: var(--sidebar-width);
    background: var(--bg-glass);
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    border-right: 1px solid var(--border-color);
    display: flex;
    flex-direction: column;
    transition: width var(--transition-normal);
    z-index: 100;
    position: relative;
    box-shadow: var(--shadow-sm);
}}

.sidebar.expanded {{
    width: var(--sidebar-expanded-width);
}}

.sidebar-toggle {{
    position: absolute;
    right: -12px;
    top: 50%;
    transform: translateY(-50%);
    width: 24px;
    height: 24px;
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    box-shadow: var(--shadow-sm);
    z-index: 101;
    transition: all var(--transition-fast);
    font-size: 11px;
    color: var(--text-secondary);
}}

.sidebar-toggle:hover {{
    background: var(--primary-color);
    color: #ffffff;
    border-color: var(--primary-color);
}}

.sidebar-nav {{
    display: flex;
    flex-direction: column;
    padding: 12px 0;
    gap: 6px;
}}

.nav-item {{
    display: flex;
    align-items: center;
    padding: 10px 14px;
    cursor: pointer;
    transition: all var(--transition-fast);
    border-radius: var(--border-radius-sm);
    margin: 0 8px;
    color: var(--text-secondary);
    position: relative;
}}

.nav-item:hover {{
    background: var(--bg-secondary);
    color: var(--text-primary);
    transform: translateX(2px);
}}

.nav-item.active {{
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    color: #ffffff;
    box-shadow: 0 4px 10px rgba(37, 99, 235, 0.25);
}}

.nav-item i {{
    font-size: 16px;
    min-width: 24px;
    text-align: center;
}}

.nav-label {{
    margin-left: 12px;
    opacity: 0;
    transition: opacity var(--transition-fast);
    white-space: nowrap;
    font-size: 13px;
    font-weight: 500;
}}

.sidebar.expanded .nav-label {{
    opacity: 1;
}}

/* ============================================
   MAP CONTAINER
   ============================================ */

.map-container {{
    flex: 1;
    position: relative;
    background: var(--bg-secondary);
}}

#map {{
    width: 100%;
    height: 100%;
    z-index: 1;
}}

/* Map Controls Floating Overlay */
.map-controls {{
    position: absolute;
    top: 18px;
    left: 18px;
    display: flex;
    flex-direction: column;
    gap: 12px;
    z-index: 500;
}}

.control-group {{
    display: flex;
    flex-direction: column;
    gap: 4px;
    background: var(--bg-glass);
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    padding: 4px;
    box-shadow: var(--shadow-md);
}}

.control-btn {{
    width: 36px;
    height: 36px;
    border: none;
    background: transparent;
    color: var(--text-primary);
    border-radius: var(--border-radius-sm);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all var(--transition-fast);
    font-size: 13px;
}}

.control-btn:hover {{
    background: var(--primary-color);
    color: #ffffff;
    transform: scale(1.05);
}}

/* Coordinates Display */
.coordinates-display {{
    position: absolute;
    bottom: 18px;
    left: 18px;
    z-index: 500;
    pointer-events: none;
}}

.coord-badge {{
    background: var(--bg-glass);
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    border: 1px solid var(--border-color);
    border-radius: 20px;
    padding: 6px 14px;
    box-shadow: var(--shadow-md);
    font-size: 11px;
    font-weight: 500;
    color: var(--text-secondary);
    display: inline-flex;
    align-items: center;
}}

/* ============================================
   RIGHT PANEL (Glassmorphism Studio)
   ============================================ */

.right-panel {{
    width: var(--right-panel-width);
    background: var(--bg-glass);
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    border-left: 1px solid var(--border-color);
    display: flex;
    flex-direction: column;
    transition: transform var(--transition-normal);
    z-index: 100;
    position: relative;
    box-shadow: var(--shadow-lg);
}}

.right-panel.collapsed {{
    transform: translateX(100%);
}}

.panel-toggle {{
    position: absolute;
    left: -12px;
    top: 50%;
    transform: translateY(-50%);
    width: 24px;
    height: 24px;
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    box-shadow: var(--shadow-sm);
    z-index: 101;
    transition: all var(--transition-fast);
    font-size: 11px;
    color: var(--text-secondary);
}}

.panel-toggle:hover {{
    background: var(--primary-color);
    color: #ffffff;
    border-color: var(--primary-color);
}}

.panel-tabs {{
    display: flex;
    border-bottom: 1px solid var(--border-color);
    background: var(--bg-secondary);
}}

.tab-btn {{
    flex: 1;
    padding: 12px 8px;
    border: none;
    background: transparent;
    color: var(--text-secondary);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    transition: all var(--transition-fast);
    font-size: 13px;
    font-weight: 500;
    border-bottom: 2px solid transparent;
}}

.tab-btn:hover {{
    color: var(--text-primary);
    background: var(--bg-tertiary);
}}

.tab-btn.active {{
    color: var(--secondary-color);
    border-bottom-color: var(--secondary-color);
    background: var(--bg-primary);
    font-weight: 600;
}}

.tab-btn i {{
    font-size: 13px;
}}

.panel-content {{
    flex: 1;
    overflow-y: auto;
    padding: 16px;
}}

.tab-pane {{
    display: none;
}}

.tab-pane.active {{
    display: block;
}}

.panel-section-header {{
    padding-bottom: 10px;
    margin-bottom: 12px;
    border-bottom: 1px solid var(--border-color);
}}

.section-title {{
    font-size: 13px;
    font-weight: 600;
    color: var(--text-primary);
    display: block;
}}

.section-desc {{
    font-size: 11px;
    color: var(--text-secondary);
    display: block;
    margin-top: 2px;
}}

/* Layer List */
.layer-list {{
    display: flex;
    flex-direction: column;
    gap: 10px;
}}

.layer-item {{
    background: var(--bg-glass-card);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    padding: 10px 12px;
    transition: all var(--transition-fast);
}}

.layer-item:hover {{
    box-shadow: var(--shadow-md);
    border-color: rgba(59, 130, 246, 0.4);
    transform: translateY(-1px);
}}

.layer-header {{
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 8px;
}}

.layer-name {{
    flex: 1;
    font-weight: 500;
    font-size: 13px;
    color: var(--text-primary);
}}

.layer-actions {{
    display: flex;
    gap: 5px;
}}

.layer-action-btn {{
    width: 28px;
    height: 28px;
    border: 1px solid var(--border-color);
    background: var(--bg-secondary);
    color: var(--text-secondary);
    border-radius: var(--border-radius-sm);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all var(--transition-fast);
    font-size: 12px;
}}

.layer-action-btn:hover {{
    background: var(--primary-color);
    color: #ffffff;
    border-color: var(--primary-color);
}}

.layer-controls {{
    padding-top: 8px;
    border-top: 1px solid var(--border-color);
}}

.layer-opacity {{
    display: flex;
    align-items: center;
    gap: 10px;
}}

.layer-opacity label {{
    font-size: 11px;
    color: var(--text-secondary);
    min-width: 80px;
}}

.layer-opacity input[type="range"] {{
    flex: 1;
    accent-color: var(--secondary-color);
}}

/* Modal Glassmorphism */
.glass-modal {{
    background: var(--bg-glass);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    color: var(--text-primary);
    border: 1px solid var(--border-color);
    border-radius: 16px;
}}

/* Legend */
.legend-content {{
    display: flex;
    flex-direction: column;
    gap: 15px;
}}

.legend-group {{
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    padding: 12px;
}}

.legend-layer-title {{
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 10px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border-color);
}}

.legend-row {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 6px 0;
    cursor: pointer;
    transition: all var(--transition-fast);
}}

.legend-row:hover {{
    background: var(--bg-tertiary);
    padding: 6px 8px;
    border-radius: var(--border-radius-sm);
}}

.legend-swatch {{
    width: 20px;
    height: 20px;
    border: 1px solid var(--border-color);
    flex-shrink: 0;
}}

.legend-text {{
    font-size: 13px;
    color: var(--text-primary);
}}

/* Basemap Grid */
.basemap-grid {{
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
}}

.basemap-item {{
    background: var(--bg-secondary);
    border: 2px solid var(--border-color);
    border-radius: var(--border-radius);
    padding: 10px;
    cursor: pointer;
    transition: all var(--transition-fast);
    text-align: center;
}}

.basemap-item:hover {{
    border-color: var(--secondary-color);
    transform: translateY(-2px);
    box-shadow: var(--shadow-sm);
}}

.basemap-item.active {{
    border-color: var(--secondary-color);
    background: var(--bg-tertiary);
}}

.basemap-preview {{
    height: 60px;
    background: var(--bg-tertiary);
    border-radius: var(--border-radius-sm);
    margin-bottom: 8px;
    background-size: cover;
    background-position: center;
}}

.basemap-name {{
    font-size: 12px;
    font-weight: 500;
    color: var(--text-primary);
}}

/* ============================================
   POPUP STYLES
   ============================================ */

.leaflet-popup-content-wrapper {{
    border-radius: var(--border-radius);
    box-shadow: var(--shadow-lg);
}}

.leaflet-popup-content {{
    margin: 0;
    min-width: 200px;
}}

.popup-container {{
    padding: 15px;
}}

.popup-title {{
    font-size: 16px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border-color);
    display: flex;
    align-items: center;
    gap: 8px;
}}

.popup-table {{
    width: 100%;
    border-collapse: collapse;
}}

.popup-table tr {{
    border-bottom: 1px solid var(--border-color);
}}

.popup-table tr:last-child {{
    border-bottom: none;
}}

.popup-label {{
    padding: 8px 0;
    font-weight: 500;
    color: var(--text-secondary);
    width: 40%;
}}

.popup-val {{
    padding: 8px 0;
    color: var(--text-primary);
    font-weight: 400;
}}

/* ============================================
   RESPONSIVE DESIGN
   ============================================ */

@media (max-width: 1024px) {{
    .right-panel {{
        position: absolute;
        right: 0;
        top: 0;
        bottom: 0;
        width: 280px;
        transform: translateX(100%);
    }}
    
    .right-panel.active {{
        transform: translateX(0);
    }}
    
    .sidebar {{
        width: var(--sidebar-width);
    }}
    
    .sidebar.expanded {{
        width: var(--sidebar-expanded-width);
    }}
}}

@media (max-width: 768px) {{
    .webgis-header {{
        padding: 0 10px;
    }}
    
    .header-center {{
        display: none;
    }}
    
    .project-info {{
        display: none;
    }}
    
    .logo-text {{
        display: none;
    }}
    
    .sidebar {{
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        z-index: 1000;
        transform: translateX(-100%);
    }}
    
    .sidebar.active {{
        transform: translateX(0);
    }}
    
    .right-panel {{
        width: 100%;
        max-width: 320px;
    }}
    
    .map-controls {{
        top: 10px;
        left: 10px;
    }}
    
    .coordinates-display {{
        bottom: 10px;
        left: 10px;
        font-size: 11px;
    }}
}}

@media (max-width: 480px) {{
    .header-right {{
        gap: 4px;
    }}
    
    .header-btn {{
        width: 32px;
        height: 32px;
        font-size: 14px;
    }}
    
    .control-btn {{
        width: 32px;
        height: 32px;
    }}
    
    .basemap-grid {{
        grid-template-columns: 1fr;
    }}
}}

/* ============================================
   ANIMATIONS
   ============================================ */

@keyframes fadeIn {{
    from {{
        opacity: 0;
    }}
    to {{
        opacity: 1;
    }}
}}

@keyframes slideIn {{
    from {{
        transform: translateX(100%);
    }}
    to {{
        transform: translateX(0);
    }}
}}

@keyframes pulse {{
    0%, 100% {{
        opacity: 1;
    }}
    50% {{
        opacity: 0.5;
    }}
}}

/* ============================================
   UTILITY CLASSES
   ============================================ */

.hidden {{
    display: none !important;
}}

.visible {{
    display: block !important;
}}

.loading {{
    animation: pulse 1.5s infinite;
}}

/* ============================================
   SCROLLBAR STYLING
   ============================================ */

::-webkit-scrollbar {{
    width: 8px;
    height: 8px;
}}

::-webkit-scrollbar-track {{
    background: var(--bg-secondary);
}}

::-webkit-scrollbar-thumb {{
    background: var(--border-color);
    border-radius: 4px;
}}

::-webkit-scrollbar-thumb:hover {{
    background: var(--text-secondary);
}}"""

        return css

    def validate(self) -> tuple:
        """Validate professional CSS generator configuration.

        :returns: Tuple of (is_valid, error_messages)
        """
        errors = []
        return (len(errors) == 0, errors)