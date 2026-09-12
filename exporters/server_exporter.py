"""
Server Exporter - Export web map for server deployment
"""

import os
from typing import Dict, List
from qgis.core import QgsMapLayer

from .base_exporter import BaseExporter
from .web_exporter import WebExporter


class ServerExporter(BaseExporter):
    """Exporter for server deployment export."""

    def __init__(self, config: Dict):
        """Initialize the server exporter.

        :param config: Project configuration
        """
        super().__init__(config)

    def export(self, layers: List[QgsMapLayer], **kwargs) -> Dict:
        """Export web map for server deployment.

        :param layers: List of QGIS layers
        :param kwargs: Additional parameters
        :returns: Dictionary with export results
        """
        results = {
            'success': False,
            'output_dir': '',
            'deployment_files': [],
            'errors': []
        }

        if self.output_dir is None:
            results['errors'].append("Output directory not set")
            return results

        try:
            self._update_progress(5, "Creating server-ready directory structure")

            # Create server-ready directory structure
            if not self._create_server_structure():
                results['errors'].append("Failed to create server structure")
                return results

            self._update_progress(10, "Exporting web project")

            # Export web project
            web_exporter = WebExporter(self.config)
            web_exporter.set_output_directory(self.output_dir)
            web_exporter.set_progress_callback(self.progress_callback)

            web_result = web_exporter.export(layers, **kwargs)
            if not web_result['success']:
                results['errors'].extend(web_result['errors'])
                return results

            self._update_progress(70, "Creating server configuration files")

            # Create server configuration files
            self._create_server_config()

            self._update_progress(80, "Creating deployment documentation")

            # Create deployment documentation
            self._create_deployment_docs()

            self._update_progress(90, "Optimizing for server deployment")

            # Optimize for server deployment
            self._optimize_for_server()

            self._update_progress(100, "Server export completed successfully")

            results['success'] = True
            results['output_dir'] = self.output_dir
            results['deployment_files'] = self._get_deployment_files()

        except Exception as e:
            results['errors'].append(f"Server export error: {str(e)}")

        return results

    def _create_server_structure(self) -> bool:
        """Create server-ready directory structure.

        :returns: True if successful
        """
        directories = [
            self.output_dir,
            os.path.join(self.output_dir, 'css'),
            os.path.join(self.output_dir, 'js'),
            os.path.join(self.output_dir, 'data'),
            os.path.join(self.output_dir, 'assets'),
            os.path.join(self.output_dir, 'server_config')
        ]

        for directory in directories:
            if not self.create_directory(directory):
                return False

        return True

    def _create_server_config(self):
        """Create server configuration files."""
        # Create .htaccess for Apache
        htaccess_content = r"""# Apache configuration for web map
<IfModule mod_rewrite.c>
    RewriteEngine On
    RewriteBase /
    RewriteRule ^index\.html$ - [L]
    RewriteCond %{REQUEST_FILENAME} !-f
    RewriteCond %{REQUEST_FILENAME} !-d
    RewriteRule . /index.html [L]
</IfModule>

# Enable compression
<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE text/html text/css application/javascript
</IfModule>

# Cache static assets
<IfModule mod_expires.c>
    ExpiresActive On
    ExpiresByType text/css "access plus 1 year"
    ExpiresByType application/javascript "access plus 1 year"
    ExpiresByType image/png "access plus 1 year"
    ExpiresByType image/jpeg "access plus 1 year"
</IfModule>
"""

        htaccess_path = os.path.join(self.output_dir, '.htaccess')
        with open(htaccess_path, 'w', encoding='utf-8') as f:
            f.write(htaccess_content)

        # Create nginx configuration
        nginx_content = r"""# Nginx configuration for web map
server {
    listen 80;
    server_name localhost;

    root /var/www/webmap;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    gzip on;
    gzip_types text/css application/javascript;
}
"""

        nginx_path = os.path.join(self.output_dir, 'server_config', 'nginx.conf')
        with open(nginx_path, 'w', encoding='utf-8') as f:
            f.write(nginx_content)

    def _create_deployment_docs(self):
        """Create deployment documentation."""
        project_title = self.get_config_value('project.title', 'Web Map')

        readme_content = f"""# {project_title} - Deployment Guide

## Quick Start

### Apache Deployment
1. Upload all files to your web server
2. Ensure .htaccess is enabled
3. Configure your virtual host
4. Access the web map

### Nginx Deployment
1. Upload all files to your web server
2. Use the provided nginx.conf
3. Restart nginx
4. Access the web map

### Static Hosting (GitHub Pages, Netlify, etc.)
1. Upload all files to the hosting service
2. Configure the service to serve index.html
3. Access the web map

## Requirements
- Web server (Apache, Nginx, or static hosting)
- No server-side processing required
- Works with HTTPS and HTTP

## Configuration
- Edit js/app.js for custom JavaScript
- Edit css/style.css for custom styles
- Modify data/*.geojson for data updates

## Support
For issues and questions, please refer to the WebGisMapBuilder documentation.
"""

        readme_path = os.path.join(self.output_dir, 'README.md')
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)

    def _optimize_for_server(self):
        """Optimize files for server deployment."""
        # This is a placeholder for optimization steps
        # In a full implementation, you might:
        # - Minify CSS and JavaScript
        # - Optimize images
        # - Generate cache manifests
        pass

    def _get_deployment_files(self) -> List[str]:
        """Get list of deployment-related files.

        :returns: List of file paths
        """
        files = []

        for root, dirs, filenames in os.walk(self.output_dir):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                # Include all files except temporary ones
                if 'temp' not in file_path:
                    files.append(file_path)

        return files

    def validate(self) -> tuple:
        """Validate server exporter configuration.

        :returns: Tuple of (is_valid, error_messages)
        """
        errors = []

        if self.output_dir is None:
            errors.append("Output directory not set")

        if not self.get_config_value('project.title'):
            errors.append("Project title is required")

        return (len(errors) == 0, errors)
