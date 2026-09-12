"""
Web Exporter - Export web map as web project structure
"""

import os
from typing import Dict, List
from qgis.core import QgsMapLayer

from .base_exporter import BaseExporter
try:
    from ..generators.geojson_generator import GeoJSONGenerator
    from ..generators.html_generator import HTMLGenerator
    from ..generators.css_generator import CSSGenerator
    from ..generators.js_generator import JavaScriptGenerator
    # Professional generators
    from ..generators.html_professional_generator import ProfessionalHTMLGenerator
    from ..generators.css_professional_generator import ProfessionalCSSGenerator
    from ..generators.js_config_generator import JSConfigGenerator
    from ..generators.js_map_generator import JSMapGenerator
    from ..generators.js_layers_generator import JSLayersGenerator
    from ..generators.js_controls_generator import JSControlsGenerator
    from ..generators.js_search_generator import JSSearchGenerator
    from ..generators.js_filters_generator import JSFiltersGenerator
    from ..generators.js_ui_generator import JSUIGenerator
    from ..generators.js_app_generator import JSAppGenerator
except (ImportError, ValueError):
    from generators.geojson_generator import GeoJSONGenerator
    from generators.html_generator import HTMLGenerator
    from generators.css_generator import CSSGenerator
    from generators.js_generator import JavaScriptGenerator
    # Professional generators
    from generators.html_professional_generator import ProfessionalHTMLGenerator
    from generators.css_professional_generator import ProfessionalCSSGenerator
    from generators.js_config_generator import JSConfigGenerator
    from generators.js_map_generator import JSMapGenerator
    from generators.js_layers_generator import JSLayersGenerator
    from generators.js_controls_generator import JSControlsGenerator
    from generators.js_search_generator import JSSearchGenerator
    from generators.js_filters_generator import JSFiltersGenerator
    from generators.js_ui_generator import JSUIGenerator
    from generators.js_app_generator import JSAppGenerator


class WebExporter(BaseExporter):
    """Exporter for web project structure."""

    def __init__(self, config: Dict):
        """Initialize the web exporter.

        :param config: Project configuration
        """
        super().__init__(config)

    def export(self, layers: List[QgsMapLayer], **kwargs) -> Dict:
        """Export web map as web project.

        :param layers: List of QGIS layers
        :param kwargs: Additional parameters
        :returns: Dictionary with export results
        """
        results = {
            'success': False,
            'output_dir': '',
            'files': [],
            'errors': []
        }

        if self.output_dir is None:
            results['errors'].append("Output directory not set")
            return results

        try:
            template_type = kwargs.get('template', self.config.get('template', 'basic'))
            use_professional = template_type == 'professional'

            self._update_progress(5, "Creating output directory structure")

            # Create directory structure
            if not self._create_directory_structure(use_professional):
                results['errors'].append("Failed to create directory structure")
                return results

            self._update_progress(10, "Exporting layer data to GeoJSON")

            # Export layer data
            geojson_result = self._export_geojson(layers)
            if not geojson_result['success']:
                results['errors'].extend(geojson_result['errors'])
                return results

            if use_professional:
                # Use professional generators
                self._update_progress(40, "Generating professional HTML template")

                html_result = self._generate_professional_html(layers)
                if not html_result['success']:
                    results['errors'].extend(html_result['errors'])
                    return results

                self._update_progress(60, "Generating professional CSS styles")

                css_result = self._generate_professional_css(layers)
                if not css_result['success']:
                    results['errors'].extend(css_result['errors'])
                    return results

                self._update_progress(70, "Generating modular JavaScript")

                js_result = self._generate_professional_javascript(layers)
                if not js_result['success']:
                    results['errors'].extend(js_result['errors'])
                    return results
            else:
                # Use basic generators
                self._update_progress(40, "Generating HTML template")

                html_result = self._generate_html(layers, template_type)
                if not html_result['success']:
                    results['errors'].extend(html_result['errors'])
                    return results

                self._update_progress(60, "Generating CSS styles")

                css_result = self._generate_css(layers, template_type)
                if not css_result['success']:
                    results['errors'].extend(css_result['errors'])
                    return results

                self._update_progress(80, "Generating JavaScript code")

                js_result = self._generate_javascript(layers, template_type)
                if not js_result['success']:
                    results['errors'].extend(js_result['errors'])
                    return results

            self._update_progress(90, "Copying assets and finalizing")

            # Copy assets if needed
            self._copy_assets()

            self._update_progress(100, "Export completed successfully")

            results['success'] = True
            results['output_dir'] = self.output_dir
            results['files'] = self._get_exported_files()

        except Exception as e:
            results['errors'].append(f"Export error: {str(e)}")

        return results

    def _create_directory_structure(self, use_professional: bool = False) -> bool:
        """Create the web project directory structure.

        :param use_professional: Whether to use professional structure
        :returns: True if successful
        """
        directories = [
            self.output_dir,
            os.path.join(self.output_dir, 'data')
        ]

        if use_professional:
            # Professional structure
            directories.extend([
                os.path.join(self.output_dir, 'assets', 'css'),
                os.path.join(self.output_dir, 'assets', 'js'),
                os.path.join(self.output_dir, 'assets', 'icons')
            ])
        else:
            # Basic structure
            directories.extend([
                os.path.join(self.output_dir, 'css'),
                os.path.join(self.output_dir, 'js'),
                os.path.join(self.output_dir, 'assets')
            ])

        for directory in directories:
            if not self.create_directory(directory):
                return False

        return True

    def _export_geojson(self, layers: List[QgsMapLayer]) -> Dict:
        """Export layers to GeoJSON format.

        :param layers: List of QGIS layers
        :returns: Dictionary with export results
        """
        generator = GeoJSONGenerator(self.config)
        generator.set_output_directory(self.output_dir)
        return generator.generate(layers)

    def _generate_html(self, layers: List[QgsMapLayer], template_type: str = 'basic') -> Dict:
        """Generate HTML template.

        :param layers: List of QGIS layers
        :param template_type: Template type to use
        :returns: Dictionary with generation results
        """
        try:
            generator = HTMLGenerator(self.config)
            result = generator.generate(layers, template=template_type)

            if result['success']:
                html_path = os.path.join(self.output_dir, 'index.html')
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(result['html'])

            return result
        except Exception as e:
            return {'success': False, 'errors': [f"HTML generation error: {str(e)}"]}

    def _generate_css(self, layers: List[QgsMapLayer], template_type: str = 'basic') -> Dict:
        """Generate CSS styles.

        :param layers: List of QGIS layers
        :param template_type: Template type to use
        :returns: Dictionary with generation results
        """
        try:
            generator = CSSGenerator(self.config)
            result = generator.generate(layers, template=template_type)

            if result['success']:
                css_path = os.path.join(self.output_dir, 'css', 'style.css')
                with open(css_path, 'w', encoding='utf-8') as f:
                    f.write(result['css'])

            return result
        except Exception as e:
            return {'success': False, 'errors': [f"CSS generation error: {str(e)}"]}

    def _generate_javascript(self, layers: List[QgsMapLayer], template_type: str = 'basic') -> Dict:
        """Generate JavaScript code.

        :param layers: List of QGIS layers
        :param template_type: Template type to use
        :returns: Dictionary with generation results
        """
        try:
            generator = JavaScriptGenerator(self.config)
            result = generator.generate(layers, template=template_type)

            if result['success']:
                js_path = os.path.join(self.output_dir, 'js', 'app.js')
                with open(js_path, 'w', encoding='utf-8') as f:
                    f.write(result['javascript'])

            return result
        except Exception as e:
            return {'success': False, 'errors': [f"JavaScript generation error: {str(e)}"]}

    def _generate_professional_html(self, layers: List[QgsMapLayer]) -> Dict:
        """Generate professional HTML template.

        :param layers: List of QGIS layers
        :returns: Dictionary with generation results
        """
        try:
            generator = ProfessionalHTMLGenerator(self.config)
            result = generator.generate(layers)

            if result['success']:
                html_path = os.path.join(self.output_dir, 'index.html')
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(result['html'])

            return result
        except Exception as e:
            return {'success': False, 'errors': [f"Professional HTML generation error: {str(e)}"]}

    def _generate_professional_css(self, layers: List[QgsMapLayer]) -> Dict:
        """Generate professional CSS styles.

        :param layers: List of QGIS layers
        :returns: Dictionary with generation results
        """
        try:
            generator = ProfessionalCSSGenerator(self.config)
            result = generator.generate(layers)

            if result['success']:
                css_path = os.path.join(self.output_dir, 'assets', 'css', 'professional.css')
                with open(css_path, 'w', encoding='utf-8') as f:
                    f.write(result['css'])

            return result
        except Exception as e:
            return {'success': False, 'errors': [f"Professional CSS generation error: {str(e)}"]}

    def _generate_professional_javascript(self, layers: List[QgsMapLayer]) -> Dict:
        """Generate modular professional JavaScript.

        :param layers: List of QGIS layers
        :returns: Dictionary with generation results
        """
        try:
            errors = []

            # Generate config.js
            config_generator = JSConfigGenerator(self.config)
            config_result = config_generator.generate(layers)
            if config_result['success']:
                config_path = os.path.join(self.output_dir, 'assets', 'js', 'config.js')
                with open(config_path, 'w', encoding='utf-8') as f:
                    f.write(config_result['javascript'])
            else:
                errors.extend(config_result['errors'])

            # Generate map.js
            map_generator = JSMapGenerator(self.config)
            map_result = map_generator.generate(layers)
            if map_result['success']:
                map_path = os.path.join(self.output_dir, 'assets', 'js', 'map.js')
                with open(map_path, 'w', encoding='utf-8') as f:
                    f.write(map_result['javascript'])
            else:
                errors.extend(map_result['errors'])

            # Generate layers.js
            layers_generator = JSLayersGenerator(self.config)
            layers_result = layers_generator.generate(layers)
            if layers_result['success']:
                layers_path = os.path.join(self.output_dir, 'assets', 'js', 'layers.js')
                with open(layers_path, 'w', encoding='utf-8') as f:
                    f.write(layers_result['javascript'])
            else:
                errors.extend(layers_result['errors'])

            # Generate controls.js
            controls_generator = JSControlsGenerator(self.config)
            controls_result = controls_generator.generate(layers)
            if controls_result['success']:
                controls_path = os.path.join(self.output_dir, 'assets', 'js', 'controls.js')
                with open(controls_path, 'w', encoding='utf-8') as f:
                    f.write(controls_result['javascript'])
            else:
                errors.extend(controls_result['errors'])

            # Generate search.js
            search_generator = JSSearchGenerator(self.config)
            search_result = search_generator.generate(layers)
            if search_result['success']:
                search_path = os.path.join(self.output_dir, 'assets', 'js', 'search.js')
                with open(search_path, 'w', encoding='utf-8') as f:
                    f.write(search_result['javascript'])
            else:
                errors.extend(search_result['errors'])

            # Generate filters.js
            filters_generator = JSFiltersGenerator(self.config)
            filters_result = filters_generator.generate(layers)
            if filters_result['success']:
                filters_path = os.path.join(self.output_dir, 'assets', 'js', 'filters.js')
                with open(filters_path, 'w', encoding='utf-8') as f:
                    f.write(filters_result['javascript'])
            else:
                errors.extend(filters_result['errors'])

            # Generate ui.js
            ui_generator = JSUIGenerator(self.config)
            ui_result = ui_generator.generate(layers)
            if ui_result['success']:
                ui_path = os.path.join(self.output_dir, 'assets', 'js', 'ui.js')
                with open(ui_path, 'w', encoding='utf-8') as f:
                    f.write(ui_result['javascript'])
            else:
                errors.extend(ui_result['errors'])

            # Generate app.js
            app_generator = JSAppGenerator(self.config)
            app_result = app_generator.generate(layers)
            if app_result['success']:
                app_path = os.path.join(self.output_dir, 'assets', 'js', 'app.js')
                with open(app_path, 'w', encoding='utf-8') as f:
                    f.write(app_result['javascript'])
            else:
                errors.extend(app_result['errors'])

            if errors:
                return {'success': False, 'errors': errors}
            else:
                return {'success': True, 'errors': []}

        except Exception as e:
            return {'success': False, 'errors': [f"Professional JavaScript generation error: {str(e)}"]}

    def _copy_assets(self):
        """Copy additional assets to output directory."""
        # This is a placeholder for copying icons, images, etc.
        # In a full implementation, you would copy assets from the plugin
        pass

    def _get_exported_files(self) -> List[str]:
        """Get list of exported files.

        :returns: List of file paths
        """
        files = []

        for root, dirs, filenames in os.walk(self.output_dir):
            for filename in filenames:
                files.append(os.path.join(root, filename))

        return files

    def validate(self) -> tuple:
        """Validate web exporter configuration.

        :returns: Tuple of (is_valid, error_messages)
        """
        errors = []

        if self.output_dir is None:
            errors.append("Output directory not set")

        if not self.get_config_value('project.title'):
            errors.append("Project title is required")

        if not self.get_config_value('map.center'):
            errors.append("Map center is required")

        return (len(errors) == 0, errors)
