"""
CSS Generator - Generate CSS styles for web maps
"""

from typing import Dict, List
from qgis.core import QgsMapLayer

from .base_generator import BaseGenerator


class CSSGenerator(BaseGenerator):
    """Generator for CSS styles."""

    def __init__(self, config: Dict):
        """Initialize the CSS generator.

        :param config: Project configuration
        """
        super().__init__(config)

    def generate(self, layers: List[QgsMapLayer], **kwargs) -> Dict:
        """Generate CSS styles.

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
            template_type = kwargs.get('template', 'basic')
            css = self._generate_css(template_type)
            results['css'] = css
            results['success'] = True

        except Exception as e:
            results['errors'].append(f"CSS generation error: {str(e)}")

        return results

    def _generate_css(self, template_type: str) -> str:
        """Generate CSS based on template type.

        :param template_type: Template type (basic, dashboard, storymap)
        :returns: CSS string
        """
        if template_type == 'basic':
            return self._generate_basic_css()
        elif template_type == 'dashboard':
            return self._generate_dashboard_css()
        elif template_type == 'storymap':
            return self._generate_storymap_css()
        else:
            return self._generate_basic_css()

    def _generate_basic_css(self) -> str:
        """Generate basic CSS styles with rich aesthetics and controls.

        :returns: CSS string
        """
        theme = self.get_config_value('theme', {})
        primary_color = theme.get('primary_color', '#1e293b')
        secondary_color = theme.get('secondary_color', '#3b82f6')
        font_family = theme.get('font_family', "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif")
        panel_bg = theme.get('panel_background', '#ffffff')
        panel_opacity = theme.get('panel_opacity', 0.96)

        css = f"""/* WebGisMapBuilder - Modern Responsive Web Map Styling */
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

html, body {{
    height: 100%;
    width: 100%;
    overflow: hidden;
    font-family: {font_family};
    background-color: #0f172a;
    color: #1e293b;
}}

#map {{
    height: 100%;
    width: 100%;
    z-index: 1;
}}

/* Floating Glassmorphic Header */
.map-floating-header {{
    position: absolute;
    top: 18px;
    left: 70px;
    z-index: 800;
    background: rgba(255, 255, 255, 0.90);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid rgba(0, 0, 0, 0.08);
    border-radius: 14px;
    padding: 8px 16px;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.12);
    pointer-events: auto;
    transition: transform 0.2s ease;
}}
.map-floating-header:hover {{
    transform: translateY(-1px);
    box-shadow: 0 14px 28px -5px rgba(0, 0, 0, 0.16);
}}
.header-brand {{
    display: flex;
    align-items: center;
    gap: 12px;
}}
.brand-icon {{
    width: 34px;
    height: 34px;
    border-radius: 10px;
    background: linear-gradient(135deg, {primary_color}, {secondary_color});
    color: #ffffff;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 15px;
    box-shadow: 0 4px 10px rgba(37, 99, 235, 0.3);
}}
.map-title {{
    font-family: 'Outfit', -apple-system, sans-serif;
    font-size: 14px;
    font-weight: 700;
    color: #0f172a;
    margin: 0;
    line-height: 1.2;
}}
.map-subtitle {{
    font-size: 11px;
    color: #64748b;
    margin: 0;
    line-height: 1.2;
}}

/* Custom Popup Styling */
.leaflet-popup-content-wrapper {{
    border-radius: 12px;
    box-shadow: 0 16px 32px rgba(0, 0, 0, 0.18);
    padding: 0;
    overflow: hidden;
    background: {panel_bg};
    backdrop-filter: blur(10px);
    border: 1px solid rgba(0, 0, 0, 0.08);
}}

.leaflet-popup-content {{
    margin: 0 !important;
    max-width: 360px;
    min-width: 220px;
    font-size: 13px;
}}

.popup-container {{
    display: flex;
    flex-direction: column;
}}

.popup-title {{
    background: {primary_color};
    color: #ffffff;
    font-weight: 600;
    font-size: 14px;
    padding: 10px 14px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    border-bottom: 2px solid {secondary_color};
}}

.popup-table {{
    width: 100%;
    border-collapse: collapse;
    padding: 6px 10px;
}}

.popup-table tr {{
    border-bottom: 1px solid #f1f5f9;
}}

.popup-table tr:last-child {{
    border-bottom: none;
}}

.popup-label {{
    font-weight: 600;
    color: #64748b;
    padding: 6px 12px;
    white-space: nowrap;
    width: 35%;
    font-size: 12px;
}}

.popup-val {{
    color: #1e293b;
    padding: 6px 12px;
    font-size: 12px;
    word-break: break-word;
}}

/* Mouse Coordinates Control */
.leaflet-coords-control {{
    background: {panel_bg};
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 500;
    color: #475569;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
    border: 1px solid rgba(0, 0, 0, 0.08);
    pointer-events: none;
}}

/* Fullscreen Button */
.leaflet-fullscreen-btn {{
    background: #ffffff;
    border: none;
    cursor: pointer;
    font-size: 16px;
    font-weight: bold;
    color: #334155;
    width: 34px;
    height: 34px;
    line-height: 34px;
    text-align: center;
    border-radius: 4px;
    box-shadow: 0 1px 5px rgba(0,0,0,0.4);
}}
.leaflet-fullscreen-btn:hover {{
    background: #f8fafc;
    color: {secondary_color};
}}

/* Interactive Legend Control - Professional Consistent Styling */
.leaflet-legend-box {{
    background: {panel_bg};
    border-radius: 8px;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.18);
    border: 1px solid rgba(0, 0, 0, 0.08);
    max-width: 280px;
    max-height: 360px;
    overflow-y: auto;
    font-size: 12px;
}}

.legend-header {{
    background: {primary_color};
    color: #ffffff;
    padding: 8px 12px;
    font-weight: 600;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
}}

.legend-toggle {{
    background: transparent;
    border: none;
    color: #ffffff;
    font-size: 16px;
    font-weight: bold;
    cursor: pointer;
    line-height: 1;
    padding: 0 4px;
}}

.legend-content {{
    padding: 10px 12px;
}}

.legend-group {{
    margin-bottom: 10px;
}}

.legend-group:last-child {{
    margin-bottom: 0;
}}

.legend-layer-title {{
    font-weight: 600;
    color: #334155;
    margin-bottom: 4px;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 2px;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

.legend-row {{
    display: flex;
    align-items: center;
    margin: 4px 0;
}}

.legend-swatch {{
    display: inline-block;
    width: 14px;
    height: 14px;
    margin-right: 8px;
    flex-shrink: 0;
    border: 1px solid rgba(0, 0, 0, 0.2);
}}

.legend-text {{
    color: #475569;
    font-size: 11.5px;
}}

/* Leaflet Legend Control */
.leaflet-legend-title {{
    font-weight: bold;
    color: {primary_color};
    margin-bottom: 5px;
    border-bottom: 2px solid {secondary_color};
    padding-bottom: 5px;
}}

.leaflet-legend-item {{
    margin: 5px 0;
    display: flex;
    align-items: center;
}}

.leaflet-legend-color {{
    width: 20px;
    height: 20px;
    margin-right: 8px;
    border: 1px solid #ccc;
}}

.leaflet-legend-label {{
    color: #555;
}}

/* Custom Layer Switcher */
.leaflet-control-layers {{
    border-radius: 8px !important;
    box-shadow: 0 4px 14px rgba(0,0,0,0.15) !important;
    border: 1px solid rgba(0,0,0,0.06) !important;
    font-size: 12px;
    padding: 8px 10px;
}}

/* Responsive adjustments */
@media (max-width: 640px) {{
    .leaflet-legend-box {{
        max-width: 200px;
        font-size: 11px;
    }}

    .leaflet-popup-content {{
        max-width: 280px;
    }}
}}"""

        return css

    def _generate_dashboard_css(self) -> str:
        """Generate dashboard CSS styles with professional legend styling.

        :returns: CSS string
        """
        theme = self.get_config_value('theme', {})
        primary_color = theme.get('primary_color', '#2c3e50')
        secondary_color = theme.get('secondary_color', '#3498db')
        font_family = theme.get('font_family', "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif")

        css = f"""/* Dashboard Layout */
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

html, body {{
    height: 100%;
    width: 100%;
}}

body {{
    font-family: {font_family};
    font-size: 14px;
    line-height: 1.6;
    color: #333;
}}

.dashboard-container {{
    display: flex;
    flex-direction: column;
    height: 100vh;
}}

.dashboard-header {{
    background: {primary_color};
    color: white;
    padding: 15px 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    z-index: 1000;
}}

.dashboard-header h1 {{
    font-size: 24px;
    font-weight: 600;
    margin: 0;
}}

.dashboard-content {{
    display: flex;
    flex: 1;
    overflow: hidden;
}}

.dashboard-sidebar {{
    width: 300px;
    background: #f8f9fa;
    border-right: 1px solid #ddd;
    overflow-y: auto;
    padding: 20px;
}}

.sidebar-panel {{
    background: white;
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}}

.sidebar-panel h3 {{
    color: {primary_color};
    font-size: 16px;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 2px solid {secondary_color};
}}

.dashboard-main {{
    flex: 1;
    position: relative;
}}

#map {{
    height: 100%;
    width: 100%;
}}

/* Legend Styles - Professional Consistent Styling */
.legend {{
    background: white;
    padding: 12px;
    border-radius: 6px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    font-size: 13px;
}}

.legend-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 8px;
    border-bottom: 2px solid {secondary_color};
    margin-bottom: 10px;
    font-weight: bold;
    color: {primary_color};
}}

.legend-toggle {{
    background: none;
    border: none;
    cursor: pointer;
    font-size: 16px;
    color: {secondary_color};
    padding: 0 8px;
}}

.legend-content {{
    max-height: 300px;
    overflow-y: auto;
}}

.legend-group {{
    margin-bottom: 12px;
}}

.legend-layer-title {{
    font-weight: 600;
    color: {primary_color};
    margin-bottom: 6px;
    font-size: 14px;
    padding-bottom: 4px;
    border-bottom: 1px solid #eee;
}}

.legend-row {{
    display: flex;
    align-items: center;
    margin: 4px 0;
    padding: 3px 0;
}}

.legend-swatch {{
    width: 16px;
    height: 16px;
    margin-right: 8px;
    border: 1px solid #ccc;
    flex-shrink: 0;
}}

.legend-text {{
    color: #555;
    font-size: 12px;
    word-break: break-word;
}}

/* Leaflet Legend Control */
.leaflet-legend-box {{
    background: white;
    padding: 10px;
    border-radius: 4px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.3);
    font-size: 12px;
}}

.leaflet-legend-title {{
    font-weight: bold;
    color: {primary_color};
    margin-bottom: 5px;
    border-bottom: 2px solid {secondary_color};
    padding-bottom: 5px;
}}

.leaflet-legend-item {{
    margin: 5px 0;
    display: flex;
    align-items: center;
}}

.leaflet-legend-color {{
    width: 20px;
    height: 20px;
    margin-right: 8px;
    border: 1px solid #ccc;
}}

.leaflet-legend-label {{
    color: #555;
}}

/* Custom Popup Styling */
.leaflet-popup-content-wrapper {{
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}}

.leaflet-popup-content {{
    margin: 12px;
    max-width: 350px;
}}

.popup-header {{
    font-weight: bold;
    color: {primary_color};
    margin-bottom: 8px;
    padding-bottom: 8px;
    border-bottom: 2px solid {secondary_color};
    font-size: 16px;
}}

.popup-field {{
    margin: 6px 0;
    font-size: 13px;
}}

.popup-label {{
    font-weight: 600;
    color: {primary_color};
    margin-right: 4px;
}}

.popup-value {{
    color: #555;
}}

/* Responsive Dashboard */
@media (max-width: 1024px) {{
    .dashboard-sidebar {{
        width: 250px;
    }}
}}

@media (max-width: 768px) {{
    .dashboard-content {{
        flex-direction: column;
    }}

    .dashboard-sidebar {{
        width: 100%;
        max-height: 200px;
        border-right: none;
        border-bottom: 1px solid #ddd;
    }}

    .dashboard-header h1 {{
        font-size: 20px;
    }}

    .legend {{
        font-size: 12px;
    }}

    .leaflet-popup-content {{
        max-width: 280px;
    }}
}}"""

        return css

    def _generate_storymap_css(self) -> str:
        """Generate story map CSS styles with professional legend styling.

        :returns: CSS string
        """
        theme = self.get_config_value('theme', {})
        primary_color = theme.get('primary_color', '#2c3e50')
        secondary_color = theme.get('secondary_color', '#3498db')
        font_family = theme.get('font_family', "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif")

        css = f"""/* Story Map Layout - Professional Styling */
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

html, body {{
    height: 100%;
    width: 100%;
}}

body {{
    font-family: {font_family};
    font-size: 16px;
    line-height: 1.8;
    color: #333;
}}

.storymap-container {{
    display: flex;
    height: 100vh;
    position: relative;
}}

#map {{
    flex: 1;
    height: 100%;
}}

.storymap-sidebar {{
    width: 400px;
    background: white;
    box-shadow: -2px 0 8px rgba(0,0,0,0.1);
    overflow-y: auto;
    z-index: 1000;
}}

.storymap-header {{
    padding: 30px 30px 20px 30px;
    border-bottom: 2px solid {secondary_color};
    background: linear-gradient(135deg, {primary_color}, {secondary_color});
    color: white;
}}

.storymap-header h1 {{
    color: white;
    font-size: 24px;
    margin-bottom: 8px;
}}

.storymap-header p {{
    color: rgba(255, 255, 255, 0.9);
    font-size: 14px;
    margin: 0;
}}

.storymap-sections {{
    padding: 30px;
}}

.storymap-section {{
    padding: 30px 0;
    border-bottom: 1px solid #eee;
    cursor: pointer;
    transition: all 0.3s ease;
}}

.storymap-section:last-child {{
    border-bottom: none;
}}

.storymap-section:hover {{
    background: #f8f9fa;
}}

.storymap-section.active {{
    border-left: 4px solid {secondary_color};
    background: linear-gradient(135deg, rgba(52, 152, 219, 0.1), rgba(52, 152, 219, 0.05));
}}

.storymap-section h2 {{
    color: {primary_color};
    font-size: 24px;
    margin-bottom: 15px;
}}

.storymap-section p {{
    color: #555;
    line-height: 1.8;
    margin-bottom: 15px;
}}

.storymap-section img {{
    max-width: 100%;
    height: auto;
    border-radius: 8px;
    margin: 15px 0;
}}

/* ============================================
   PROFESSIONAL LEGEND STYLES
   ============================================ */

/* Legend Container */
.legend {{
    background: white;
    padding: 12px;
    border-radius: 6px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    font-size: 13px;
    max-width: 280px;
}}

.legend-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 8px;
    border-bottom: 2px solid {secondary_color};
    margin-bottom: 10px;
    font-weight: bold;
    color: {primary_color};
}}

.legend-toggle {{
    background: none;
    border: none;
    cursor: pointer;
    font-size: 16px;
    color: {secondary_color};
    padding: 0 8px;
}}

.legend-content {{
    max-height: 300px;
    overflow-y: auto;
}}

.legend-group {{
    margin-bottom: 12px;
}}

.legend-layer-title {{
    font-weight: 600;
    color: {primary_color};
    margin-bottom: 6px;
    font-size: 14px;
    padding-bottom: 4px;
    border-bottom: 1px solid #eee;
}}

.legend-row {{
    display: flex;
    align-items: center;
    margin: 4px 0;
    padding: 3px 0;
}}

.legend-swatch {{
    width: 16px;
    height: 16px;
    margin-right: 8px;
    border: 1px solid #ccc;
    flex-shrink: 0;
}}

.legend-text {{
    color: #555;
    font-size: 12px;
    word-break: break-word;
}}

/* Leaflet Legend Control */
.leaflet-legend-box {{
    background: white;
    padding: 10px;
    border-radius: 4px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.3);
    font-size: 12px;
}}

.leaflet-legend-title {{
    font-weight: bold;
    color: {primary_color};
    margin-bottom: 5px;
    border-bottom: 2px solid {secondary_color};
    padding-bottom: 5px;
}}

.leaflet-legend-item {{
    margin: 5px 0;
    display: flex;
    align-items: center;
}}

.leaflet-legend-color {{
    width: 20px;
    height: 20px;
    margin-right: 8px;
    border: 1px solid #ccc;
}}

.leaflet-legend-label {{
    color: #555;
}}

/* Custom Popup Styling */
.leaflet-popup-content-wrapper {{
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}}

.leaflet-popup-content {{
    margin: 12px;
    max-width: 350px;
}}

.popup-header {{
    font-weight: bold;
    color: {primary_color};
    margin-bottom: 8px;
    padding-bottom: 8px;
    border-bottom: 2px solid {secondary_color};
    font-size: 16px;
}}

.popup-field {{
    margin: 6px 0;
    font-size: 13px;
}}

.popup-label {{
    font-weight: 600;
    color: {primary_color};
    margin-right: 4px;
}}

.popup-value {{
    color: #555;
}}

/* Responsive Story Map */
@media (max-width: 1024px) {{
    .storymap-sidebar {{
        width: 350px;
    }}
}}

@media (max-width: 768px) {{
    .storymap-container {{
        flex-direction: column;
    }}

    .storymap-sidebar {{
        width: 100%;
        max-height: 40vh;
        box-shadow: 0 -2px 8px rgba(0,0,0,0.1);
    }}

    .storymap-sections {{
        padding: 20px;
    }}

    .storymap-section h2 {{
        font-size: 20px;
    }}

    .legend {{
        max-width: 240px;
        font-size: 12px;
    }}
}}

@media (max-width: 480px) {{
    .storymap-sections {{
        padding: 15px;
    }}

    .storymap-section h2 {{
        font-size: 18px;
    }}

    .storymap-section p {{
        font-size: 14px;
    }}

    .legend {{
        max-width: 200px;
        font-size: 11px;
    }}

    .legend-swatch {{
        width: 14px;
        height: 14px;
    }}
}}"""

        return css

    def validate(self) -> tuple:
        """Validate CSS generator configuration.

        :returns: Tuple of (is_valid, error_messages)
        """
        errors = []

        # CSS generation is generally flexible, so minimal validation
        theme = self.get_config_value('theme', {})
        if not theme:
            errors.append("Theme configuration is missing")

        return (len(errors) == 0, errors)
