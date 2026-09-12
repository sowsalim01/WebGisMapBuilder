"""
Main Dialog - Interactive Web Map Designer Dialog for QGIS
"""

import os
import tempfile
from typing import Dict, List, Optional

from qgis.PyQt.QtCore import Qt, pyqtSignal, QUrl
from qgis.PyQt.QtGui import QDesktopServices, QColor, QFont
from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QPushButton, QLabel, QProgressBar, QTextEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QLineEdit, QSpinBox,
    QSlider, QCheckBox, QComboBox, QGroupBox, QFileDialog,
    QMessageBox, QSplitter, QFormLayout, QFrame, QRadioButton,
    QAbstractItemView
)
from qgis.core import QgsProject, QgsMapLayer, QgsVectorLayer

from ..core.plugin import WebGisMapBuilderCore
from ..core.layer_manager import LayerManager
from ..core.config_manager import ConfigManager
from ..core.style_manager import StyleManager
from ..core.validator import ProjectValidator
from ..exporters.web_exporter import WebExporter
from ..exporters.zip_exporter import ZipExporter
from ..exporters.server_exporter import ServerExporter


class WebGisMapBuilderDialog(QDialog):
    """Main studio dialog for WebGisMapBuilder plugin."""

    export_progress = pyqtSignal(int, str)
    export_complete = pyqtSignal(str)
    export_error = pyqtSignal(str)

    def __init__(self, iface):
        """Initialize the main dialog.

        :param iface: QGIS interface instance
        """
        super().__init__()
        self.iface = iface
        self.project = QgsProject.instance()

        # Initialize core managers
        self.core = WebGisMapBuilderCore(iface)
        self.layer_manager = LayerManager()
        self.config_manager = ConfigManager()
        self.style_manager = StyleManager()
        self.validator = ProjectValidator()

        # Load initial project settings
        self.config_manager.load_from_qgis_project()
        self.current_selected_layer_id = None
        self.last_export_dir = None
        self.last_export_html = None

        # Setup complete UI
        self._setup_ui()

        # Connect signals
        self.export_progress.connect(self._on_export_progress)
        self.export_complete.connect(self._on_export_complete)
        self.export_error.connect(self._on_export_error)

        # Populate layer list and UI controls
        self._refresh_project()

    def _setup_ui(self):
        """Build the complete native Qt dialog interface."""
        self.setWindowTitle("WebGisMap Builder - Interactive Web Map Designer")
        self.setMinimumSize(960, 680)
        self.resize(1020, 720)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(14, 14, 14, 14)
        main_layout.setSpacing(10)

        # --- Top Header ---
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 4)

        title_box = QVBoxLayout()
        title_label = QLabel("<h2 style='margin:0; color:#1e293b;'>WebGisMap Builder</h2>")
        subtitle_label = QLabel("<span style='color:#64748b;'>Studio de conception et de publication de cartes web interactives Leaflet</span>")
        title_box.addWidget(title_label)
        title_box.addWidget(subtitle_label)
        header_layout.addLayout(title_box)
        header_layout.addStretch()

        refresh_btn = QPushButton("Actualiser le projet")
        refresh_btn.clicked.connect(self._refresh_project)
        header_layout.addWidget(refresh_btn)
        main_layout.addWidget(header_widget)

        # --- Tab Widget ---
        self.tab_widget = QTabWidget()
        self.layers_tab = self._create_layers_tab()
        self.style_tab = self._create_style_tab()
        self.interaction_tab = self._create_interaction_tab()
        self.preview_tab = self._create_preview_tab()
        self.export_tab = self._create_export_tab()

        self.tab_widget.addTab(self.layers_tab, "1. Couches")
        self.tab_widget.addTab(self.style_tab, "2. Style & Thème")
        self.tab_widget.addTab(self.interaction_tab, "3. Interactivité")
        self.tab_widget.addTab(self.preview_tab, "4. Prévisualisation")
        self.tab_widget.addTab(self.export_tab, "5. Exportation")
        main_layout.addWidget(self.tab_widget)

        # --- Bottom Progress & Status Bar ---
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        main_layout.addWidget(self.progress_bar)

        bottom_layout = QHBoxLayout()
        self.status_label = QLabel("Prêt")
        self.status_label.setStyleSheet("color: #475569; font-weight: 500;")
        bottom_layout.addWidget(self.status_label)
        bottom_layout.addStretch()

        close_btn = QPushButton("Fermer")
        close_btn.clicked.connect(self.close)
        bottom_layout.addWidget(close_btn)
        main_layout.addLayout(bottom_layout)

    # =========================================================================
    # TAB 1: LAYERS
    # =========================================================================
    def _create_layers_tab(self) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout(widget)

        # Left: Layer Table + Reorder & selection buttons
        left_box = QVBoxLayout()
        lbl = QLabel("<b>Couches disponibles dans le projet QGIS :</b>")
        left_box.addWidget(lbl)

        self.layer_table = QTableWidget()
        self.layer_table.setColumnCount(5)
        self.layer_table.setHorizontalHeaderLabels(["Inclure", "Couche", "Type", "Entités", "CRS"])
        self.layer_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.layer_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.layer_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.layer_table.itemSelectionChanged.connect(self._on_layer_selection_changed)
        self.layer_table.itemChanged.connect(self._on_layer_item_changed)
        left_box.addWidget(self.layer_table)

        btn_row = QHBoxLayout()
        btn_sel_all = QPushButton("Tout sélectionner")
        btn_sel_all.clicked.connect(self._select_all_layers)
        btn_desel_all = QPushButton("Tout désélectionner")
        btn_desel_all.clicked.connect(self._deselect_all_layers)
        btn_move_up = QPushButton("Monter ↑")
        btn_move_up.clicked.connect(self._move_layer_up)
        btn_move_down = QPushButton("Descendre ↓")
        btn_move_down.clicked.connect(self._move_layer_down)

        btn_row.addWidget(btn_sel_all)
        btn_row.addWidget(btn_desel_all)
        btn_row.addSpacing(15)
        btn_row.addWidget(btn_move_up)
        btn_row.addWidget(btn_move_down)
        btn_row.addStretch()
        left_box.addLayout(btn_row)

        layout.addLayout(left_box, 3)

        # Right: Properties of Selected Layer
        right_box = QVBoxLayout()
        prop_group = QGroupBox("Propriétés de la couche sélectionnée")
        form = QFormLayout(prop_group)

        self.layer_title_edit = QLineEdit()
        self.layer_title_edit.textChanged.connect(self._on_layer_prop_changed)
        form.addRow("Titre web :", self.layer_title_edit)

        self.layer_visible_chk = QCheckBox("Visible par défaut au chargement")
        self.layer_visible_chk.toggled.connect(self._on_layer_prop_changed)
        form.addRow("Visibilité :", self.layer_visible_chk)

        self.layer_opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.layer_opacity_slider.setRange(0, 100)
        self.layer_opacity_slider.setValue(100)
        self.layer_opacity_label = QLabel("100 %")
        self.layer_opacity_slider.valueChanged.connect(self._on_opacity_slider_changed)
        op_row = QHBoxLayout()
        op_row.addWidget(self.layer_opacity_slider)
        op_row.addWidget(self.layer_opacity_label)
        form.addRow("Opacité :", op_row)

        self.min_zoom_spin = QSpinBox()
        self.min_zoom_spin.setRange(0, 22)
        self.min_zoom_spin.setValue(0)
        self.min_zoom_spin.valueChanged.connect(self._on_layer_prop_changed)
        form.addRow("Zoom min :", self.min_zoom_spin)

        self.max_zoom_spin = QSpinBox()
        self.max_zoom_spin.setRange(0, 22)
        self.max_zoom_spin.setValue(22)
        self.max_zoom_spin.valueChanged.connect(self._on_layer_prop_changed)
        form.addRow("Zoom max :", self.max_zoom_spin)

        right_box.addWidget(prop_group)
        right_box.addStretch()
        layout.addLayout(right_box, 2)

        return widget

    # =========================================================================
    # TAB 2: STYLE & THEME
    # =========================================================================
    def _create_style_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Layer Style Inspection
        style_box = QGroupBox("Style de la couche active (extrait de QGIS)")
        style_layout = QVBoxLayout(style_box)
        self.style_summary_label = QLabel("Sélectionnez une couche dans l'onglet Couches pour inspecter son style.")
        self.style_summary_label.setWordWrap(True)
        self.style_summary_label.setStyleSheet("padding: 8px; background: #f8fafc; border-radius: 4px;")
        style_layout.addWidget(self.style_summary_label)
        layout.addWidget(style_box)

        # Global Theme & Template Settings
        theme_box = QGroupBox("Paramètres généraux & Titre du projet")
        form = QFormLayout(theme_box)

        self.project_title_edit = QLineEdit()
        initial_title = self.config_manager.get_config('project.title') or self.project.title() or self.project.baseName() or "WebGIS Map"
        self.project_title_edit.setText(initial_title)
        self.project_title_edit.setPlaceholderText("Ex: Carte interactive du territoire")
        self.project_title_edit.textChanged.connect(self._on_project_title_changed)
        form.addRow("Titre du projet web :", self.project_title_edit)

        self.theme_combo = QComboBox()
        self.theme_combo.addItem("Professional GIS (Bleu ardoise & moderne)", "professional")
        self.theme_combo.addItem("Dark GIS (Thème sombre élégant)", "dark")
        self.theme_combo.addItem("Minimal Clean (Épuré blanc/gris)", "minimal")
        self.theme_combo.addItem("Light GIS (Clair contemporain)", "light")
        self.theme_combo.addItem("Government (Bleu officiel)", "government")
        self.theme_combo.currentIndexChanged.connect(self._on_theme_changed)
        form.addRow("Thème graphique :", self.theme_combo)

        self.template_combo = QComboBox()
        self.template_combo.addItem("Professional WebGIS (Interface moderne professionnelle)", "professional")
        self.template_combo.addItem("Basic Map (Carte plein écran avec panneaux)", "basic")
        self.template_combo.addItem("Dashboard (En-tête, statistiques & carte)", "dashboard")
        self.template_combo.addItem("Story Map (Narration séquentielle & carte)", "storymap")
        self.template_combo.setCurrentIndex(0)  # Default to professional
        self.template_combo.currentIndexChanged.connect(self._on_template_changed)
        form.addRow("Modèle d'application (Template) :", self.template_combo)

        self.basemap_combo = QComboBox()
        self.basemap_combo.addItem("OpenStreetMap (Standard)", "osm")
        self.basemap_combo.addItem("CartoDB Positron (Fond clair épuré)", "carto_positron")
        self.basemap_combo.addItem("CartoDB Dark (Fond sombre)", "carto_dark")
        self.basemap_combo.addItem("ESRI Imagerie Satellite", "esri_world")
        self.basemap_combo.addItem("OpenTopoMap (Relief)", "opentopomap")
        self.basemap_combo.currentIndexChanged.connect(self._on_basemap_changed)
        form.addRow("Fond de carte par défaut :", self.basemap_combo)

        layout.addWidget(theme_box)
        layout.addStretch()
        return widget

    # =========================================================================
    # TAB 3: INTERACTIVITY & POPUPS
    # =========================================================================
    def _create_interaction_tab(self) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout(widget)

        # Left: Popup fields configuration for selected layer
        popup_box = QGroupBox("Configuration des Popups (Couche sélectionnée)")
        v_popup = QVBoxLayout(popup_box)
        v_popup.addWidget(QLabel("Cochez les champs à afficher dans la fenêtre contextuelle :"))

        self.popup_fields_table = QTableWidget()
        self.popup_fields_table.setColumnCount(3)
        self.popup_fields_table.setHorizontalHeaderLabels(["Afficher", "Attribut", "Libellé / Alias"])
        self.popup_fields_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.popup_fields_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.popup_fields_table.itemChanged.connect(self._on_popup_item_changed)
        v_popup.addWidget(self.popup_fields_table)

        btn_pop_all = QPushButton("Tout cocher")
        btn_pop_all.clicked.connect(self._select_all_popup_fields)
        btn_pop_none = QPushButton("Tout décocher")
        btn_pop_none.clicked.connect(self._deselect_all_popup_fields)
        pop_btn_row = QHBoxLayout()
        pop_btn_row.addWidget(btn_pop_all)
        pop_btn_row.addWidget(btn_pop_none)
        v_popup.addLayout(pop_btn_row)

        layout.addWidget(popup_box, 3)

        # Right: Map Tools & Controls checkboxes
        tools_box = QGroupBox("Outils et Contrôles interactifs de la carte")
        v_tools = QVBoxLayout(tools_box)

        self.chk_layer_control = QCheckBox("Contrôle des couches (L.control.layers)")
        self.chk_layer_control.setChecked(True)
        self.chk_layer_control.toggled.connect(self._on_ui_control_toggled)
        v_tools.addWidget(self.chk_layer_control)

        self.chk_scale = QCheckBox("Barre d'échelle graphique métrique")
        self.chk_scale.setChecked(True)
        self.chk_scale.toggled.connect(self._on_ui_control_toggled)
        v_tools.addWidget(self.chk_scale)

        self.chk_fullscreen = QCheckBox("Bouton Plein écran")
        self.chk_fullscreen.setChecked(True)
        self.chk_fullscreen.toggled.connect(self._on_ui_control_toggled)
        v_tools.addWidget(self.chk_fullscreen)

        self.chk_coords = QCheckBox("Coordonnées de la souris en direct (Lat/Lon)")
        self.chk_coords.setChecked(True)
        self.chk_coords.toggled.connect(self._on_ui_control_toggled)
        v_tools.addWidget(self.chk_coords)

        self.chk_legend = QCheckBox("Légende dynamique dépliable")
        self.chk_legend.setChecked(True)
        self.chk_legend.toggled.connect(self._on_ui_control_toggled)
        v_tools.addWidget(self.chk_legend)

        v_tools.addStretch()
        layout.addWidget(tools_box, 2)

        return widget

    # =========================================================================
    # TAB 4: PREVIEW
    # =========================================================================
    def _create_preview_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        layout.addWidget(QLabel("<b>Prévisualisation locale de la carte web</b>"))

        self.preview_info_label = QLabel(
            "Générez un aperçu temporaire de votre carte web pour tester l'interactivité, "
            "les styles et les popups dans votre navigateur par défaut."
        )
        self.preview_info_label.setWordWrap(True)
        self.preview_info_label.setStyleSheet("padding: 12px; background: #f1f5f9; border-radius: 6px;")
        layout.addWidget(self.preview_info_label)

        btn_row = QHBoxLayout()
        gen_preview_btn = QPushButton("Générer l'aperçu temporaire")
        gen_preview_btn.setStyleSheet("padding: 8px 16px; font-weight: bold;")
        gen_preview_btn.clicked.connect(self._generate_preview)
        btn_row.addWidget(gen_preview_btn)

        self.open_preview_browser_btn = QPushButton("Ouvrir dans le navigateur web")
        self.open_preview_browser_btn.setEnabled(False)
        self.open_preview_browser_btn.setStyleSheet("padding: 8px 16px; background:#2563eb; color:white; font-weight: bold;")
        self.open_preview_browser_btn.clicked.connect(self._open_last_preview)
        btn_row.addWidget(self.open_preview_browser_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        layout.addWidget(QLabel("Journal de prévisualisation :"))
        self.preview_log = QTextEdit()
        self.preview_log.setReadOnly(True)
        self.preview_log.setMaximumHeight(200)
        layout.addWidget(self.preview_log)

        layout.addStretch()
        return widget

    # =========================================================================
    # TAB 5: EXPORT
    # =========================================================================
    def _create_export_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Format Selection
        format_group = QGroupBox("Format d'exportation")
        h_format = QHBoxLayout(format_group)
        self.radio_web = QRadioButton("Dossier Web prêt à l'emploi (HTML / CSS / JS / GeoJSON)")
        self.radio_web.setChecked(True)
        self.radio_zip = QRadioButton("Archive ZIP compressée (.zip)")
        self.radio_server = QRadioButton("Package Serveur (.htaccess, Nginx, Guide)")
        h_format.addWidget(self.radio_web)
        h_format.addWidget(self.radio_zip)
        h_format.addWidget(self.radio_server)
        layout.addWidget(format_group)

        # Output Directory
        dir_group = QGroupBox("Dossier de destination")
        h_dir = QHBoxLayout(dir_group)
        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setPlaceholderText("Sélectionnez le dossier où enregistrer la carte web...")
        default_dir = os.path.join(os.path.expanduser("~"), "WebGisMap_Export")
        self.output_dir_edit.setText(default_dir)
        browse_btn = QPushButton("Parcourir...")
        browse_btn.clicked.connect(self._browse_output_dir)
        h_dir.addWidget(self.output_dir_edit)
        h_dir.addWidget(browse_btn)
        layout.addWidget(dir_group)

        # Action Buttons
        action_row = QHBoxLayout()
        validate_btn = QPushButton("Vérifier et Valider le projet")
        validate_btn.clicked.connect(self._validate_current_project)
        action_row.addWidget(validate_btn)

        self.export_btn = QPushButton("Exporter la carte web")
        self.export_btn.setStyleSheet("background: #16a34a; color: white; padding: 10px 24px; font-weight: bold; font-size: 14px; border-radius: 6px;")
        self.export_btn.clicked.connect(self._execute_export)
        action_row.addWidget(self.export_btn)

        self.open_export_dir_btn = QPushButton("Ouvrir le dossier")
        self.open_export_dir_btn.setEnabled(False)
        self.open_export_dir_btn.clicked.connect(self._open_exported_folder)
        action_row.addWidget(self.open_export_dir_btn)

        self.open_exported_map_btn = QPushButton("Lancer la carte web")
        self.open_exported_map_btn.setEnabled(False)
        self.open_exported_map_btn.setStyleSheet("background: #0284c7; color: white; padding: 8px 16px; font-weight: bold; border-radius: 4px;")
        self.open_exported_map_btn.clicked.connect(self._open_exported_map)
        action_row.addWidget(self.open_exported_map_btn)

        layout.addLayout(action_row)

        # Log Box
        layout.addWidget(QLabel("<b>Rapport et Journal des opérations :</b>"))
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(220)
        layout.addWidget(self.log_text)

        return widget

    # =========================================================================
    # DATA POPULATION & LOGIC
    # =========================================================================
    def _refresh_project(self):
        """Reload layers from the current QGIS project."""
        self.core.load_current_project()
        self.config_manager.load_from_qgis_project()

        current_title = self.config_manager.get_config('project.title') or self.project.title() or self.project.baseName() or "WebGIS Map"
        if hasattr(self, 'project_title_edit'):
            self.project_title_edit.blockSignals(True)
            self.project_title_edit.setText(current_title)
            self.project_title_edit.blockSignals(False)

        layers = list(self.project.mapLayers().values())
        self.layer_table.blockSignals(True)
        self.layer_table.setRowCount(len(layers))

        for row, layer in enumerate(layers):
            # Column 0: CheckBox
            chk_item = QTableWidgetItem()
            chk_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            chk_item.setCheckState(Qt.CheckState.Checked)
            chk_item.setData(Qt.ItemDataRole.UserRole, layer.id())
            self.layer_table.setItem(row, 0, chk_item)

            # Column 1: Name
            name_item = QTableWidgetItem(layer.name())
            name_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            name_item.setData(Qt.ItemDataRole.UserRole, layer.id())
            self.layer_table.setItem(row, 1, name_item)

            # Column 2: Geom Type
            geom_type = "Raster"
            count_str = "-"
            if layer.type() == QgsMapLayer.VectorLayer:
                g = layer.geometryType()
                geom_map = {0: "Point", 1: "Ligne", 2: "Polygone", 3: "Inconnu", 4: "Table"}
                geom_type = geom_map.get(g, "Vecteur")
                count_str = str(layer.featureCount())

            type_item = QTableWidgetItem(geom_type)
            type_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self.layer_table.setItem(row, 2, type_item)

            # Column 3: Feature count
            cnt_item = QTableWidgetItem(count_str)
            cnt_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self.layer_table.setItem(row, 3, cnt_item)

            # Column 4: CRS
            crs_item = QTableWidgetItem(layer.crs().authid())
            crs_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self.layer_table.setItem(row, 4, crs_item)

            # Initialize config in LayerManager
            self.layer_manager.get_layer_config(layer.id(), layer)
            self.core.select_layer(layer.id(), True)

        self.layer_table.blockSignals(False)

        if layers:
            self.layer_table.selectRow(0)

        self._log(f"Projet QGIS actualisé : {len(layers)} couche(s) détectée(s).")

    def _on_layer_selection_changed(self):
        """Update property panel and popup table when user clicks a row."""
        selected_items = self.layer_table.selectedItems()
        if not selected_items:
            return

        row = selected_items[0].row()
        item = self.layer_table.item(row, 1)
        if not item:
            return

        layer_id = item.data(Qt.ItemDataRole.UserRole)
        self.current_selected_layer_id = layer_id
        layer = self.project.mapLayer(layer_id)
        if not layer:
            return

        cfg = self.layer_manager.get_layer_config(layer_id, layer)

        # Update layer properties panel
        self.layer_title_edit.blockSignals(True)
        self.layer_visible_chk.blockSignals(True)
        self.layer_opacity_slider.blockSignals(True)
        self.min_zoom_spin.blockSignals(True)
        self.max_zoom_spin.blockSignals(True)

        self.layer_title_edit.setText(cfg.get('display_name', layer.name()))
        self.layer_visible_chk.setChecked(cfg.get('visible', True))
        opacity_pct = int(cfg.get('opacity', 1.0) * 100)
        self.layer_opacity_slider.setValue(opacity_pct)
        self.layer_opacity_label.setText(f"{opacity_pct} %")
        self.min_zoom_spin.setValue(cfg.get('min_zoom', 0))
        self.max_zoom_spin.setValue(cfg.get('max_zoom', 22))

        self.layer_title_edit.blockSignals(False)
        self.layer_visible_chk.blockSignals(False)
        self.layer_opacity_slider.blockSignals(False)
        self.min_zoom_spin.blockSignals(False)
        self.max_zoom_spin.blockSignals(False)

        # Update Style tab summary
        style_desc = f"<b>Couche :</b> {layer.name()}<br>"
        if layer.type() == QgsMapLayer.VectorLayer:
            renderer = layer.renderer()
            style_desc += f"<b>Type de rendu QGIS :</b> {renderer.type() if renderer else 'Défaut'}<br>"
            legend_items = self.style_manager.extract_legend_items(layer)
            if legend_items:
                style_desc += "<b>Éléments de légende :</b><br>"
                for li in legend_items[:8]:
                    style_desc += f"&nbsp;&nbsp;• <span style='color:{li.get('color')};'>■</span> {li.get('label')}<br>"
        else:
            style_desc += "<b>Couche Raster</b>"

        self.style_summary_label.setText(style_desc)

        # Update Popup table in Interaction tab
        self._populate_popup_fields_table(layer, cfg)

    def _populate_popup_fields_table(self, layer: QgsMapLayer, cfg: Dict):
        """Populate the popup fields table for the given layer."""
        self.popup_fields_table.blockSignals(True)

        if layer.type() != QgsMapLayer.VectorLayer:
            self.popup_fields_table.setRowCount(0)
            self.popup_fields_table.blockSignals(False)
            return

        fields = layer.fields()
        configured_popup_fields = cfg.get('popup_fields', [])
        conf_dict = {pf['name']: pf for pf in configured_popup_fields if isinstance(pf, dict)}

        self.popup_fields_table.setRowCount(len(fields))
        for row, f in enumerate(fields):
            fname = f.name()
            falias = f.alias() or fname
            visible = True

            if fname in conf_dict:
                visible = conf_dict[fname].get('visible', True)
                falias = conf_dict[fname].get('alias', falias)

            # Col 0: CheckBox
            chk_item = QTableWidgetItem()
            chk_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            chk_item.setCheckState(Qt.CheckState.Checked if visible else Qt.CheckState.Unchecked)
            chk_item.setData(Qt.ItemDataRole.UserRole, fname)
            self.popup_fields_table.setItem(row, 0, chk_item)

            # Col 1: Name
            name_item = QTableWidgetItem(fname)
            name_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.popup_fields_table.setItem(row, 1, name_item)

            # Col 2: Alias (editable)
            alias_item = QTableWidgetItem(falias)
            alias_item.setData(Qt.ItemDataRole.UserRole, fname)
            self.popup_fields_table.setItem(row, 2, alias_item)

        self.popup_fields_table.blockSignals(False)

    def _on_layer_item_changed(self, item: QTableWidgetItem):
        """Handle checkbox inclusion changes in layer table."""
        if item.column() == 0:
            layer_id = item.data(Qt.ItemDataRole.UserRole)
            is_checked = (item.checkState() == Qt.CheckState.Checked)
            self.core.select_layer(layer_id, is_checked)

    def _on_layer_prop_changed(self):
        """Save changes to the active layer's configuration."""
        if not self.current_selected_layer_id:
            return

        config_update = {
            'display_name': self.layer_title_edit.text().strip(),
            'visible': self.layer_visible_chk.isChecked(),
            'opacity': self.layer_opacity_slider.value() / 100.0,
            'min_zoom': self.min_zoom_spin.value(),
            'max_zoom': self.max_zoom_spin.value()
        }
        self.layer_manager.set_layer_config(self.current_selected_layer_id, config_update)

    def _on_opacity_slider_changed(self, val: int):
        self.layer_opacity_label.setText(f"{val} %")
        self._on_layer_prop_changed()

    def _on_popup_item_changed(self, item: QTableWidgetItem):
        """Handle changes in the popup fields table."""
        if not self.current_selected_layer_id:
            return

        popup_fields = []
        for r in range(self.popup_fields_table.rowCount()):
            chk_item = self.popup_fields_table.item(r, 0)
            alias_item = self.popup_fields_table.item(r, 2)
            fname = chk_item.data(Qt.ItemDataRole.UserRole)
            alias = alias_item.text().strip() if alias_item else fname
            visible = (chk_item.checkState() == Qt.CheckState.Checked)
            popup_fields.append({
                'name': fname,
                'alias': alias or fname,
                'visible': visible
            })

        self.layer_manager.set_layer_config(self.current_selected_layer_id, {'popup_fields': popup_fields})

    def _select_all_popup_fields(self):
        self.popup_fields_table.blockSignals(True)
        for r in range(self.popup_fields_table.rowCount()):
            self.popup_fields_table.item(r, 0).setCheckState(Qt.CheckState.Checked)
        self.popup_fields_table.blockSignals(False)
        self._on_popup_item_changed(self.popup_fields_table.item(0, 0))

    def _deselect_all_popup_fields(self):
        self.popup_fields_table.blockSignals(True)
        for r in range(self.popup_fields_table.rowCount()):
            self.popup_fields_table.item(r, 0).setCheckState(Qt.CheckState.Unchecked)
        self.popup_fields_table.blockSignals(False)
        self._on_popup_item_changed(self.popup_fields_table.item(0, 0))

    def _select_all_layers(self):
        self.layer_table.blockSignals(True)
        for r in range(self.layer_table.rowCount()):
            item = self.layer_table.item(r, 0)
            item.setCheckState(Qt.CheckState.Checked)
            self.core.select_layer(item.data(Qt.ItemDataRole.UserRole), True)
        self.layer_table.blockSignals(False)

    def _deselect_all_layers(self):
        self.layer_table.blockSignals(True)
        for r in range(self.layer_table.rowCount()):
            item = self.layer_table.item(r, 0)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.core.select_layer(item.data(Qt.ItemDataRole.UserRole), False)
        self.layer_table.blockSignals(False)

    def _move_layer_up(self):
        row = self.layer_table.currentRow()
        if row > 0:
            self.layer_table.blockSignals(True)
            self._swap_rows(row, row - 1)
            self.layer_table.selectRow(row - 1)
            self.layer_table.blockSignals(False)

    def _move_layer_down(self):
        row = self.layer_table.currentRow()
        if row >= 0 and row < self.layer_table.rowCount() - 1:
            self.layer_table.blockSignals(True)
            self._swap_rows(row, row + 1)
            self.layer_table.selectRow(row + 1)
            self.layer_table.blockSignals(False)

    def _swap_rows(self, r1: int, r2: int):
        for col in range(self.layer_table.columnCount()):
            it1 = self.layer_table.takeItem(r1, col)
            it2 = self.layer_table.takeItem(r2, col)
            self.layer_table.setItem(r1, col, it2)
            self.layer_table.setItem(r2, col, it1)

    def _on_project_title_changed(self, text: str):
        title = text.strip() or "WebGIS Map"
        self.config_manager.set_config('project.title', title)

    def _on_theme_changed(self):
        theme_name = self.theme_combo.currentData()
        themes = self.config_manager.get_available_themes()
        if theme_name in themes:
            self.config_manager.set_config('theme', themes[theme_name])

    def _on_template_changed(self):
        self.config_manager.set_config('template', self.template_combo.currentData())

    def _on_basemap_changed(self):
        provider = self.basemap_combo.currentData()
        providers = self.config_manager.get_basemap_providers()
        if provider in providers:
            cfg = providers[provider].copy()
            cfg['provider'] = provider
            self.config_manager.set_config('basemap', cfg)

    def _on_ui_control_toggled(self):
        self.config_manager.set_config('ui.show_layer_control', self.chk_layer_control.isChecked())
        self.config_manager.set_config('ui.show_scale_control', self.chk_scale.isChecked())
        self.config_manager.set_config('ui.show_fullscreen', self.chk_fullscreen.isChecked())
        self.config_manager.set_config('ui.show_mouse_position', self.chk_coords.isChecked())
        self.config_manager.set_config('ui.show_legend', self.chk_legend.isChecked())

    def _browse_output_dir(self):
        path = QFileDialog.getExistingDirectory(self, "Choisir le dossier d'exportation", self.output_dir_edit.text())
        if path:
            self.output_dir_edit.setText(path)

    def _collect_export_config(self) -> Dict:
        """Synchronize layer configs into main project configuration dictionary."""
        config = self.config_manager.get_config().copy()
        if hasattr(self, 'template_combo') and self.template_combo.currentData():
            config['template'] = self.template_combo.currentData()
        if hasattr(self, 'theme_combo') and self.theme_combo.currentData():
            theme_name = self.theme_combo.currentData()
            themes = self.config_manager.get_available_themes()
            if theme_name in themes:
                config['theme'] = themes[theme_name]

        # Ensure project title is set
        if 'project' not in config:
            config['project'] = {}
        if hasattr(self, 'project_title_edit') and self.project_title_edit.text().strip():
            config['project']['title'] = self.project_title_edit.text().strip()
        elif not config['project'].get('title'):
            config['project']['title'] = self.project.title() or self.project.baseName() or "WebGIS Map"

        config['layers'] = {}

        for row in range(self.layer_table.rowCount()):
            layer_id = self.layer_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            config['layers'][layer_id] = self.layer_manager.get_layer_config(layer_id)

        return config

    def _get_active_layers_in_order(self) -> List[QgsMapLayer]:
        """Return selected QGIS layers in the table order."""
        ordered_layers = []
        for r in range(self.layer_table.rowCount()):
            chk_item = self.layer_table.item(r, 0)
            if chk_item.checkState() == Qt.CheckState.Checked:
                lid = chk_item.data(Qt.ItemDataRole.UserRole)
                layer = self.project.mapLayer(lid)
                if layer:
                    ordered_layers.append(layer)
        return ordered_layers

    # =========================================================================
    # PREVIEW & EXPORT ACTIONS
    # =========================================================================
    def _generate_preview(self):
        """Generate a temporary web map export and enable browser preview."""
        layers = self._get_active_layers_in_order()
        if not layers:
            QMessageBox.warning(self, "Avertissement", "Veuillez sélectionner au moins une couche à prévisualiser.")
            return

        temp_dir = os.path.join(tempfile.gettempdir(), "webgismap_preview")
        os.makedirs(temp_dir, exist_ok=True)

        config = self._collect_export_config()
        exporter = WebExporter(config)
        exporter.set_output_directory(temp_dir)

        self.preview_log.append("Génération de l'aperçu temporaire...")
        result = exporter.export(layers)

        if result['success']:
            self.last_export_dir = temp_dir
            self.last_export_html = os.path.join(temp_dir, 'index.html')
            self.open_preview_browser_btn.setEnabled(True)
            self.preview_log.append("✅ Aperçu généré avec succès !")
            self.preview_log.append(f"Emplacement : {self.last_export_html}")
            # Automatically open preview
            self._open_last_preview()
        else:
            self.preview_log.append("❌ Échec de l'aperçu :")
            for err in result.get('errors', []):
                self.preview_log.append(f"  • {err}")

    def _open_last_preview(self):
        if self.last_export_html and os.path.exists(self.last_export_html):
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.last_export_html))

    def _validate_current_project(self):
        """Validate current setup and display detailed report."""
        layers = self._get_active_layers_in_order()
        config = self._collect_export_config()
        is_valid, errors, warnings, info = self.validator.validate_project(layers, config)

        report = self.validator.get_validation_report()
        self._log("--- RAPPORT DE VALIDATION ---")
        self._log(report)
        self._log("-----------------------------")

        if is_valid:
            QMessageBox.information(self, "Validation réussie", "Le projet est prêt pour l'exportation.")
        else:
            QMessageBox.warning(self, "Erreurs de validation", "Des erreurs ont été détectées. Consultez le journal pour plus de détails.")

    def _execute_export(self):
        """Run the final web map export."""
        layers = self._get_active_layers_in_order()
        if not layers:
            QMessageBox.warning(self, "Avertissement", "Veuillez sélectionner au moins une couche.")
            return

        out_dir = self.output_dir_edit.text().strip()
        if not out_dir:
            QMessageBox.warning(self, "Avertissement", "Veuillez définir un dossier de sortie valide.")
            return

        os.makedirs(out_dir, exist_ok=True)
        config = self._collect_export_config()

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.export_btn.setEnabled(False)
        self._log("Début de l'exportation...")

        # Choose exporter
        if self.radio_zip.isChecked():
            exporter = ZipExporter(config)
        elif self.radio_server.isChecked():
            exporter = ServerExporter(config)
        else:
            exporter = WebExporter(config)

        exporter.set_output_directory(out_dir)
        exporter.set_progress_callback(lambda val, msg: self.export_progress.emit(val, msg))

        # Run export
        result = exporter.export(layers)

        if result['success']:
            self.export_complete.emit(out_dir)
        else:
            err_msg = "\n".join(result.get('errors', ['Erreur inconnue']))
            self.export_error.emit(err_msg)

    def _on_export_progress(self, val: int, msg: str):
        self.progress_bar.setValue(val)
        self.status_label.setText(msg)
        self._log(f"[{val}%] {msg}")

    def _on_export_complete(self, out_path: str):
        self.progress_bar.setValue(100)
        self.export_btn.setEnabled(True)
        self.status_label.setText("Exportation terminée avec succès.")
        self._log(f"✅ Exportation réussie dans : {out_path}")

        self.last_export_dir = out_path
        self.last_export_html = os.path.join(out_path, 'index.html')
        self.open_export_dir_btn.setEnabled(True)
        if os.path.exists(self.last_export_html):
            self.open_exported_map_btn.setEnabled(True)

        QMessageBox.information(self, "Exportation terminée", f"La carte web a été générée avec succès dans :\n{out_path}")

    def _on_export_error(self, err_msg: str):
        self.progress_bar.setVisible(False)
        self.export_btn.setEnabled(True)
        self.status_label.setText("Échec de l'exportation.")
        self._log(f"❌ Erreur : {err_msg}")
        QMessageBox.critical(self, "Erreur d'exportation", f"L'exportation a échoué :\n{err_msg}")

    def _open_exported_folder(self):
        if self.last_export_dir and os.path.exists(self.last_export_dir):
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.last_export_dir))

    def _open_exported_map(self):
        if self.last_export_html and os.path.exists(self.last_export_html):
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.last_export_html))

    def _log(self, message: str):
        self.log_text.append(message)
