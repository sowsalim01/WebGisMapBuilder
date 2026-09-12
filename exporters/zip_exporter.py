"""
ZIP Exporter - Export web map as ZIP archive
"""

import os
import shutil
import zipfile
from typing import Dict, List
from qgis.core import QgsMapLayer

from .base_exporter import BaseExporter
from .web_exporter import WebExporter


class ZipExporter(BaseExporter):
    """Exporter for ZIP archive export."""

    def __init__(self, config: Dict):
        """Initialize the ZIP exporter.

        :param config: Project configuration
        """
        super().__init__(config)

    def export(self, layers: List[QgsMapLayer], **kwargs) -> Dict:
        """Export web map as ZIP archive.

        :param layers: List of QGIS layers
        :param kwargs: Additional parameters
        :returns: Dictionary with export results
        """
        results = {
            'success': False,
            'output_file': '',
            'errors': []
        }

        if self.output_dir is None:
            results['errors'].append("Output directory not set")
            return results

        try:
            self._update_progress(5, "Creating temporary directory")

            # Create temporary directory for web export
            temp_dir = os.path.join(self.output_dir, 'temp_web_export')
            if not self.create_directory(temp_dir):
                results['errors'].append("Failed to create temporary directory")
                return results

            self._update_progress(10, "Exporting web project")

            # Export web project to temporary directory
            web_exporter = WebExporter(self.config)
            web_exporter.set_output_directory(temp_dir)
            web_exporter.set_progress_callback(self.progress_callback)

            web_result = web_exporter.export(layers, **kwargs)
            if not web_result['success']:
                results['errors'].extend(web_result['errors'])
                return results

            self._update_progress(90, "Creating ZIP archive")

            # Create ZIP archive
            project_name = self.clean_filename(self.get_config_value('project.title', 'webmap'))
            zip_filename = f"{project_name}.zip"
            zip_path = os.path.join(self.output_dir, zip_filename)

            if self._create_zip_archive(temp_dir, zip_path):
                results['success'] = True
                results['output_file'] = zip_path
            else:
                results['errors'].append("Failed to create ZIP archive")

            self._update_progress(95, "Cleaning up temporary files")

            # Clean up temporary directory
            self._cleanup_temp_directory(temp_dir)

            self._update_progress(100, "ZIP export completed successfully")

        except Exception as e:
            results['errors'].append(f"ZIP export error: {str(e)}")

        return results

    def _create_zip_archive(self, source_dir: str, zip_path: str) -> bool:
        """Create ZIP archive from directory.

        :param source_dir: Source directory
        :param zip_path: Output ZIP file path
        :returns: True if successful
        """
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(source_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, source_dir)
                        zipf.write(file_path, arcname)

            return True

        except Exception as e:
            print(f"Error creating ZIP archive: {e}")
            return False

    def _cleanup_temp_directory(self, temp_dir: str):
        """Clean up temporary directory.

        :param temp_dir: Temporary directory path
        """
        try:
            shutil.rmtree(temp_dir)
        except Exception as e:
            print(f"Error cleaning up temporary directory: {e}")

    def validate(self) -> tuple:
        """Validate ZIP exporter configuration.

        :returns: Tuple of (is_valid, error_messages)
        """
        errors = []

        if self.output_dir is None:
            errors.append("Output directory not set")

        if not self.get_config_value('project.title'):
            errors.append("Project title is required")

        return (len(errors) == 0, errors)
