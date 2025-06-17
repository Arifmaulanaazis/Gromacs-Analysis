from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import os, sys
import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib import cm
import subprocess
import time
import numpy as np
from cycler import cycler


class PlotStyleDialog(QDialog):
    def __init__(self, compounds, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Customize Plot Styles")
        self.setMinimumWidth(500)
        
        # Available style options
        self.line_styles = ['-', '--', '-.', ':', 'None']
        self.markers = ['None', '.', 'o', 'v', '^', '<', '>', 's', 'p', '*', 'h', 'H', '+', 'x', 'D', 'd']
        self.colors = ['blue', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan', 'magenta', 'yellow', 'black', 'red']
        
        # Store compounds and their styles
        self.compounds = compounds
        self.styles = {}
        
        # Initialize with default styles - solid lines and better colors
        for i, compound in enumerate(compounds):
            self.styles[compound] = {
                'line_style': '-',  # Default to solid line
                'marker': self.markers[(i+1) % len(self.markers)],
                'color': self.colors[i % len(self.colors)]
            }
        
        # Create layout
        layout = QVBoxLayout()
        
        # Add instructions
        instruction = QLabel("Customize the plot style for each compound:")
        instruction.setStyleSheet("font-weight: bold;")
        layout.addWidget(instruction)
        
        # Create a scroll area for many compounds
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # Add a row for each compound
        for compound in compounds:
            group_box = QGroupBox(compound)
            group_layout = QGridLayout()
            
            # Line style selector
            group_layout.addWidget(QLabel("Line Style:"), 0, 0)
            line_combo = QComboBox()
            line_combo.addItems(self.line_styles)
            line_combo.setCurrentText(self.styles[compound]['line_style'])
            line_combo.currentTextChanged.connect(lambda text, c=compound: self.update_style(c, 'line_style', text))
            group_layout.addWidget(line_combo, 0, 1)
            
            # Marker selector
            group_layout.addWidget(QLabel("Marker:"), 1, 0)
            marker_combo = QComboBox()
            marker_combo.addItems(self.markers)
            marker_combo.setCurrentText(self.styles[compound]['marker'])
            marker_combo.currentTextChanged.connect(lambda text, c=compound: self.update_style(c, 'marker', text))
            group_layout.addWidget(marker_combo, 1, 1)
            
            # Color selector
            group_layout.addWidget(QLabel("Color:"), 2, 0)
            color_combo = QComboBox()
            for color in self.colors:
                color_combo.addItem(color)
                # Set the background color of the item
                color_combo.setItemData(color_combo.count()-1, QColor(color), Qt.BackgroundRole)
            color_combo.setCurrentText(self.styles[compound]['color'])
            color_combo.currentTextChanged.connect(lambda text, c=compound: self.update_style(c, 'color', text))
            group_layout.addWidget(color_combo, 2, 1)
            
            # Preview button
            preview_button = QPushButton("Preview")
            preview_button.clicked.connect(lambda _, c=compound: self.show_preview(c))
            group_layout.addWidget(preview_button, 3, 0, 1, 2)
            
            group_box.setLayout(group_layout)
            scroll_layout.addWidget(group_box)
        
        scroll_content.setLayout(scroll_layout)
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        # Add buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def update_style(self, compound, style_type, value):
        self.styles[compound][style_type] = value
    
    def show_preview(self, compound):
        style = self.styles[compound]
        
        # Create a small preview plot
        preview = QDialog(self)
        preview.setWindowTitle(f"Preview for {compound}")
        preview.setFixedSize(300, 200)
        
        layout = QVBoxLayout()
        
        fig = plt.figure(figsize=(4, 3))
        ax = fig.add_subplot(111)
        
        # Create sample data
        x = np.linspace(0, 10, 50)
        y = np.sin(x)
        
        # Plot with the selected style
        line_style = style['line_style']
        marker = style['marker']
        color = style['color']
        
        # Handle 'None' values
        if line_style == 'None':
            line_style = ''
        if marker == 'None':
            marker = ''
            
        ax.plot(x, y, label=compound, 
                linestyle=line_style, 
                marker=marker, 
                color=color,
                markevery=5)
        
        ax.set_title(f"Style Preview: {compound}")
        ax.legend()
        
        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(preview.close)
        layout.addWidget(close_button)
        
        preview.setLayout(layout)
        preview.exec_()
    
    def get_styles(self):
        return self.styles


class SampleSelectionDialog(QDialog):
    def __init__(self, samples, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Samples to Display")
        self.setMinimumWidth(400)
        
        # Store samples and their visibility
        self.samples = samples
        self.visibility = {sample: True for sample in samples}  # All visible by default
        
        # Create layout
        layout = QVBoxLayout()
        
        # Add instructions
        instruction = QLabel("Select which samples to display in the plot:")
        instruction.setStyleSheet("font-weight: bold;")
        layout.addWidget(instruction)
        
        # Create a scroll area for many samples
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # Add a checkbox for each sample
        for sample in samples:
            checkbox = QCheckBox(sample)
            checkbox.setChecked(True)
            checkbox.stateChanged.connect(lambda state, s=sample: self.update_visibility(s, state))
            scroll_layout.addWidget(checkbox)
        
        # Add select/deselect all buttons
        buttons_layout = QHBoxLayout()
        select_all = QPushButton("Select All")
        select_all.clicked.connect(self.select_all)
        deselect_all = QPushButton("Deselect All")
        deselect_all.clicked.connect(self.deselect_all)
        buttons_layout.addWidget(select_all)
        buttons_layout.addWidget(deselect_all)
        scroll_layout.addLayout(buttons_layout)
        
        scroll_content.setLayout(scroll_layout)
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        # Add buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def update_visibility(self, sample, state):
        self.visibility[sample] = (state == Qt.Checked)
    
    def select_all(self):
        for sample in self.samples:
            self.visibility[sample] = True
        # Update all checkboxes
        for i in range(self.layout().itemAt(1).widget().widget().layout().count() - 1):  # -1 for the buttons layout
            item = self.layout().itemAt(1).widget().widget().layout().itemAt(i)
            if isinstance(item.widget(), QCheckBox):
                item.widget().setChecked(True)
    
    def deselect_all(self):
        for sample in self.samples:
            self.visibility[sample] = False
        # Update all checkboxes
        for i in range(self.layout().itemAt(1).widget().widget().layout().count() - 1):  # -1 for the buttons layout
            item = self.layout().itemAt(1).widget().widget().layout().itemAt(i)
            if isinstance(item.widget(), QCheckBox):
                item.widget().setChecked(False)
    
    def get_visibility(self):
        return self.visibility


class Analisis_Gromacs(QtWidgets.QWidget):
    def __init__(self, path_folder_kerja):
        super().__init__()
        self.path_folder_kerja = path_folder_kerja
        self.path_icon = os.path.dirname(os.path.realpath(__file__))
        self.setObjectName("self")
        self.resize(804, 655)
        
        # Set up a nicer plotting style
        plt.style.use('ggplot')
        
        # Create figure with higher DPI for better quality
        self.figure = plt.figure(figsize=(6, 4), dpi=120)
        self.canvas = FigureCanvas(self.figure)

        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        self.pushButton = QtWidgets.QPushButton(self)
        self.pushButton.setMaximumSize(QtCore.QSize(100, 16777215))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.analisis)
        self.gridLayout.addWidget(self.pushButton, 0, 0, 1, 1)
        self.pushButton_2 = QtWidgets.QPushButton(self)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.clicked.connect(self.save)
        self.gridLayout.addWidget(self.pushButton_2, 0, 1, 1, 1, QtCore.Qt.AlignLeft)
        
        # Add customize button
        self.customize_button = QtWidgets.QPushButton(self)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.customize_button.setFont(font)
        self.customize_button.setText("Customize")
        self.customize_button.clicked.connect(self.customize_plot)
        self.gridLayout.addWidget(self.customize_button, 0, 2, 1, 1, QtCore.Qt.AlignLeft)
        
        # Add select samples button
        self.select_samples_button = QtWidgets.QPushButton(self)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.select_samples_button.setFont(font)
        self.select_samples_button.setText("Select Samples")
        self.select_samples_button.clicked.connect(self.select_samples)
        self.gridLayout.addWidget(self.select_samples_button, 0, 3, 1, 1, QtCore.Qt.AlignLeft)
        
        self.label = QtWidgets.QLabel(self)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 4, 1, 1, QtCore.Qt.AlignRight)
        self.comboBox = QtWidgets.QComboBox(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox.sizePolicy().hasHeightForWidth())
        self.comboBox.setSizePolicy(sizePolicy)
        self.comboBox.setMaximumSize(QtCore.QSize(500, 16777215))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.comboBox.setFont(font)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.currentIndexChanged.connect(self.combo_berubah)
        self.gridLayout.addWidget(self.comboBox, 0, 5, 1, 1)
        self.widget = QtWidgets.QWidget(self)
        self.widget.setObjectName("widget")
        self.gridLayout.addWidget(self.widget, 1, 0, 1, 6)

        self.verticalLayout = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout.setObjectName("verticalLayout")

        
        
        self.verticalLayout.addWidget(self.canvas)
        self.setLayout(self.verticalLayout)
        

        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Form", "Analisis Gromacs"))
        self.pushButton.setText(_translate("Form", "Analisis"))
        self.pushButton_2.setText(_translate("Form", "Simpan"))
        self.label.setText(_translate("Form", "DATA"))
        self.comboBox.setItemText(0, _translate("Form", "RMSD"))
        self.comboBox.setItemText(1, _translate("Form", "Radius of gyration (total and around axes)"))
        self.comboBox.setItemText(2, _translate("Form", "Hydrogen Bonds"))
        self.comboBox.setItemText(3, _translate("Form", "Solvent Accessible Surface Area (SASA)"))
        self.comboBox.setItemText(4, _translate("Form", "RMSD Protein-Ligand"))
        self.comboBox.setItemText(5, _translate("Form", "RMS fluctuation Atom (RMSF atom)"))
        self.comboBox.setItemText(6, _translate("Form", "RMS fluctuation Residue (RMSF Residue)"))

        QtCore.QMetaObject.connectSlotsByName(self)
        
        # Enhanced styling for plots
        self.title_font = {'fontname':'Arial', 'size':'22', 'color':'black', 'weight':'bold', 'verticalalignment':'bottom'}
        self.axis_font = {'fontname':'Arial', 'size':'16', 'weight':'bold'}
        self.tick_font = {'fontname':'Arial', 'size':'12'}
        self.legend_font = {'size':'14', 'family':'Arial'}
        
        # Define a custom color cycle with vibrant colors (avoiding red as default)
        self.color_cycle = cycler(color=['#1f77b4', '#2ca02c', '#ff7f0e', '#9467bd', 
                                         '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', 
                                         '#17becf', '#1a55FF', '#8B008B', '#d62728'])
        
        # Line styles and markers for differentiation (solid lines by default)
        self.line_styles = ['-', '-', '-', '-', '-', '-', '-']
        self.markers = ['o', 's', '^', 'D', 'v', '<', '>', 'p']
        
        # Store current xvg files, custom styles, and sample visibility
        self.current_xvg_files = []
        self.custom_styles = {}
        self.sample_visibility = {}

        if os.path.exists(self.path_folder_kerja + "/RMSD"):
            self.pushButton.hide()
            self.pushButton_2.show()
            self.customize_button.show()
            self.select_samples_button.show()

            xvg_listawal = [self.path_folder_kerja + "/RMSD/" + data1 for data1 in os.listdir(self.path_folder_kerja + "/RMSD") if data1.endswith(".xvg")]
            self.current_xvg_files = xvg_listawal
            
            # Initialize all samples as visible
            samples = [os.path.basename(xvg).split('.')[0] for xvg in xvg_listawal]
            self.sample_visibility = {sample: True for sample in samples}
            
            self.plot_data(xvg_listawal)

        else:
            self.pushButton.show()
            self.pushButton_2.hide()
            self.customize_button.hide()
            self.select_samples_button.hide()
            
    def select_samples(self):
        """Open dialog to select which samples to display"""
        if not self.current_xvg_files:
            QMessageBox.warning(self, "No Data", "No plot data available to select samples from")
            return
            
        # Extract compound names from file paths
        compounds = [os.path.basename(xvg).split('.')[0] for xvg in self.current_xvg_files]
        
        # Show the sample selection dialog
        dialog = SampleSelectionDialog(compounds, self)
        
        # Pre-set the checkboxes based on current visibility
        for i in range(dialog.layout().itemAt(1).widget().widget().layout().count() - 1):  # -1 for the buttons layout
            item = dialog.layout().itemAt(1).widget().widget().layout().itemAt(i)
            if isinstance(item.widget(), QCheckBox):
                sample = item.widget().text()
                if sample in self.sample_visibility:
                    item.widget().setChecked(self.sample_visibility[sample])
        
        if dialog.exec_() == QDialog.Accepted:
            # Get the visibility settings
            self.sample_visibility = dialog.get_visibility()
            
            # Get the current plot type
            current_type = self.comboBox.currentText()
            
            # Replot with updated visibility
            self.combo_berubah()
            
    def customize_plot(self):
        """Open dialog to customize plot styles"""
        if not self.current_xvg_files:
            QMessageBox.warning(self, "No Data", "No plot data available to customize")
            return
            
        # Extract compound names from file paths
        compounds = [os.path.basename(xvg).split('.')[0] for xvg in self.current_xvg_files]
        
        # Show the customization dialog
        dialog = PlotStyleDialog(compounds, self)
        if dialog.exec_() == QDialog.Accepted:
            # Get the custom styles
            self.custom_styles = dialog.get_styles()
            # Replot with custom styles
            self.plot_data(self.current_xvg_files)


    def save(self):
        path_simpan = QtWidgets.QFileDialog.getSaveFileName(self, "Simpan Gambar", "", "PNG (*.png);;JPG (*.jpg);;PDF (*.pdf);;SVG (*.svg)")
        if path_simpan[0]:
            self.figure.savefig(path_simpan[0], dpi=500, bbox_inches='tight')
            QMessageBox.information(self, "Berhasil", f"Plot berhasil disimpan ke {path_simpan[0]}")


    def plot_data(self, xvg_files):
        """Enhanced plotting function with better styling and custom styles"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Apply the custom color cycle
        ax.set_prop_cycle(self.color_cycle)
        
        # Store the current xvg files
        self.current_xvg_files = xvg_files
        
        # Initialize sample visibility if needed
        if not self.sample_visibility:
            samples = [os.path.basename(xvg).split('.')[0] for xvg in xvg_files]
            self.sample_visibility = {sample: True for sample in samples}
        
        # Track plot data for statistics
        all_y_data = []
        
        # Track if any samples are visible
        visible_count = 0
        
        for i, xvg in enumerate(xvg_files):
            if not os.path.exists(xvg):
                continue
                
            # Check if this sample should be visible
            sample_name = os.path.basename(xvg).split('.')[0]
            if sample_name in self.sample_visibility and not self.sample_visibility[sample_name]:
                continue  # Skip this sample if it's set to be hidden
                
            visible_count += 1

            # Read raw data and metadata
            with open(xvg, "r") as f:
                lines = f.readlines()

            raw_data = []
            title = ""
            x_label = ""
            y_label = ""

            for line in lines:
                if not line.startswith("@") and not line.startswith("#"):
                    parts = line.split()
                    raw_data.append((float(parts[0]), float(parts[1])))
                else:
                    # Detect plot type and labels
                    if "Radius of gyration (total and around axes)" in line:
                        title = "Radius of gyration (total and around axes)"
                        x_label = "Time (ps)"
                        y_label = "Radius of gyration/Rg (nm)"
                    elif "Hydrogen bonds" in line:
                        title = "Number of hydrogen bonds"
                        x_label = "Time (ps)"
                        y_label = "Hbonds"
                    elif "Solvent Accessible Surface" in line:
                        title = "Solvent Accessible Surface"
                        x_label = "Time (ps)"
                        y_label = "Area (nm²)"
                    elif "rmsf_rec.xvg" in line:
                        title = "RMS fluctuation Residue"
                        x_label = "Residue"
                        y_label = "RMSF (nm)"
                    elif "rmsf_atom.xvg" in line:
                        title = "RMS fluctuation Atom"
                        x_label = "Atom"
                        y_label = "RMSF (nm)"
                    elif "rmsd_pro_lig.xvg" in line:
                        title = "RMSD Protein-Ligand"
                        x_label = "Time (ns)"
                        y_label = "RMSD (nm)"
                    elif "rmsd.xvg" in line:
                        title = "RMSD"
                        x_label = "Time (ns)"
                        y_label = "RMSD (nm)"

            # If no numerical data, skip
            if not raw_data:
                continue

            base_label = os.path.basename(xvg).split('.')[0]

            # Handle RMS fluctuation Residue grouping
            if title == "RMS fluctuation Residue":
                # Split into segments where residue number resets or decreases
                segments = []
                seg = []
                prev_res = None
                for res, val in raw_data:
                    if prev_res is not None and res <= prev_res:
                        segments.append(seg)
                        seg = []
                    seg.append((res, val))
                    prev_res = res
                if seg:
                    segments.append(seg)

                # Plot each segment with its own label (Residue A, B, ...)
                for idx, seg in enumerate(segments):
                    xs, ys = zip(*seg)
                    seg_label = f"{base_label} - Residue {chr(ord('A') + idx)}"
                    all_y_data.append(list(ys))

                    # Use custom style if available
                    if base_label in self.custom_styles:
                        style = self.custom_styles[base_label]
                        line_style = '' if style['line_style'] == 'None' else style['line_style']
                        marker = '' if style['marker'] == 'None' else style['marker']
                        color = style['color']
                        ax.plot(xs, ys, label=seg_label, linewidth=1.5,
                               linestyle=line_style, marker=marker, color=color,
                               markevery=max(1, len(xs)//20), markersize=4)
                    else:
                        line_style = self.line_styles[i % len(self.line_styles)]
                        marker = self.markers[i % len(self.markers)]
                        ax.plot(xs, ys, label=seg_label, linewidth=1.5,
                               linestyle=line_style, marker=marker,
                               markevery=max(1, len(xs)//20), markersize=4)

                # Skip default plotting for this file
                continue

            # For all other plots
            y_vals = [val for _, val in raw_data]
            all_y_data.append(y_vals)
            
            # Plot single series
            label = base_label
            if label in self.custom_styles:
                style = self.custom_styles[label]
                line_style = '' if style['line_style'] == 'None' else style['line_style']
                marker = '' if style['marker'] == 'None' else style['marker']
                color = style['color']
                xs, ys = zip(*raw_data)
                ax.plot(xs, ys, label=label, linewidth=1.5,
                       linestyle=line_style, marker=marker, color=color,
                       markevery=max(1, len(xs)//20), markersize=4)
            else:
                xs, ys = zip(*raw_data)
                line_style = self.line_styles[i % len(self.line_styles)]
                marker = self.markers[i % len(self.markers)]
                ax.plot(xs, ys, label=label, linewidth=1.5,
                       linestyle=line_style, marker=marker,
                       markevery=max(1, len(xs)//20), markersize=4)
        
        # Display a message if no samples are visible
        if visible_count == 0:
            ax.text(0.5, 0.5, "No samples selected for display", 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=14)
            self.canvas.draw()
            return

        # Set title and labels with enhanced styling
        ax.set_title(title, **self.title_font)
        ax.set_xlabel(x_label, **self.axis_font)
        ax.set_ylabel(y_label, **self.axis_font)
        
        # Customize ticks
        ax.tick_params(axis='both', which='major', labelsize=12)
        
        # Add grid for better readability
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Add legend with enhanced styling if multiple series
        if visible_count > 1:
            ax.legend(loc='best', frameon=True, fancybox=True, shadow=True, fontsize=12)
        
        # Add a light background color to the plot area
        ax.set_facecolor('#f8f9fa')
        
        # Add a border around the plot
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_color('black')
            spine.set_linewidth(1.0)
        
        # Tight layout to make sure everything fits
        self.figure.tight_layout()
        
        # Draw the canvas
        self.canvas.draw()



    def combo_berubah(self):
        try:
            list_data_xvg = []
            opsisekarang = self.comboBox.currentText()
            if opsisekarang == "RMSD":
                list_data_xvg = [self.path_folder_kerja + "/RMSD/" + data1 for data1 in os.listdir(self.path_folder_kerja + "/RMSD") if data1.endswith(".xvg")]

            elif opsisekarang == "Radius of gyration (total and around axes)":
                list_data_xvg = [self.path_folder_kerja + "/gyration/" + data1 for data1 in os.listdir(self.path_folder_kerja + "/gyration") if data1.endswith(".xvg")]

            elif opsisekarang == "Hydrogen Bonds":
                list_data_xvg = [self.path_folder_kerja + "/hbond/" + data1 for data1 in os.listdir(self.path_folder_kerja + "/hbond") if data1.endswith(".xvg")]

            elif opsisekarang == "Solvent Accessible Surface Area (SASA)":
                list_data_xvg = [self.path_folder_kerja + "/sasa/" + data1 for data1 in os.listdir(self.path_folder_kerja + "/sasa") if data1.endswith(".xvg")]

            elif opsisekarang == "RMSD Protein-Ligand":
                list_data_xvg = [self.path_folder_kerja + "/rmsd_pro_lig/" + data1 for data1 in os.listdir(self.path_folder_kerja + "/rmsd_pro_lig") if data1.endswith(".xvg")]

            elif opsisekarang == "RMS fluctuation Atom (RMSF atom)":
                list_data_xvg = [self.path_folder_kerja + "/rmsf_atom/" + data1 for data1 in os.listdir(self.path_folder_kerja + "/rmsf_atom") if data1.endswith(".xvg")]

            elif opsisekarang == "RMS fluctuation Residue (RMSF Residue)":
                list_data_xvg = [self.path_folder_kerja + "/rmsf_rec/" + data1 for data1 in os.listdir(self.path_folder_kerja + "/rmsf_rec") if data1.endswith(".xvg")]

            # Store current xvg files before plotting
            self.current_xvg_files = list_data_xvg
            
            # Make sure sample visibility is maintained across different data types
            # by using the same sample names (folder names)
            samples = [os.path.basename(xvg).split('.')[0] for xvg in list_data_xvg]
            for sample in samples:
                if sample not in self.sample_visibility:
                    self.sample_visibility[sample] = True
            
            self.plot_data(list_data_xvg)

        except Exception as e:
            print(f"Error: {e}")
            pass

    def analisis(self):
        path_gmx = f'{str(self.path_icon)}/gromacs/bin/gmx'
        path_kerja = f'{self.path_folder_kerja}'

        try:
            os.mkdir(f'{path_kerja}/RMSD')
        except:
            pass
        try:
            os.mkdir(f'{path_kerja}/gyration')
        except: 
            pass
        try:
            os.mkdir(f'{path_kerja}/hbond')
        except:
            pass
        try:
            os.mkdir(f'{path_kerja}/sasa')
        except:
            pass
        try:
            os.mkdir(f'{path_kerja}/rmsd_pro_lig')
        except:
            pass
        try:
            os.mkdir(f'{path_kerja}/rmsf_atom')
        except:
            pass
        try:
            os.mkdir(f'{path_kerja}/rmsf_rec')
        except:
            pass

        # Show a progress dialog
        progress = QProgressDialog("Melakukan analisis...", "Batal", 0, 8, self)
        progress.setWindowTitle("Analisis GROMACS")
        progress.setWindowModality(Qt.WindowModal)
        progress.show()
        QApplication.processEvents()

        # Buat Analisis
        progress.setValue(1)
        progress.setLabelText("Mengkonversi trajectory...")
        QApplication.processEvents()
        perintah_1 = [f'{path_gmx}', 'trjconv', '-s', f'{path_kerja}/step5_1.tpr', '-f', f'{path_kerja}/step5_1.xtc', '-o', f'{path_kerja}/analisis.xtc', '-pbc', 'mol', '-ur', 'compact']
        p1 = subprocess.Popen(perintah_1, stdin=subprocess.PIPE)
        p1.communicate(input=b'0\n')

        # Buat RMSD
        progress.setValue(2)
        progress.setLabelText("Menghitung RMSD...")
        QApplication.processEvents()
        perintah_2 = [f'{path_gmx}', 'rms', '-s', f'{path_kerja}/step5_1.tpr', '-f', f'{path_kerja}/analisis.xtc', '-o', f'{path_kerja}/RMSD/rmsd.xvg', '-tu', 'ns']
        p2 = subprocess.Popen(perintah_2, stdin=subprocess.PIPE)
        p2.communicate(input=b'4\n4\n')

        # Buat RMSD Protein-Ligan
        progress.setValue(3)
        progress.setLabelText("Menghitung RMSD Protein-Ligand...")
        QApplication.processEvents()
        perintah_3 = [f'{path_gmx}', 'rms', '-s', f'{path_kerja}/step5_1.tpr', '-f', f'{path_kerja}/analisis.xtc', '-o', f'{path_kerja}/rmsd_pro_lig/rmsd_pro_lig.xvg', '-tu', 'ns']
        p3 = subprocess.Popen(perintah_3, stdin=subprocess.PIPE)
        p3.communicate(input=b'1\n13\n')

        # Buat RMSF
        progress.setValue(4)
        progress.setLabelText("Menghitung RMSF Atom...")
        QApplication.processEvents()
        perintah_4 = [f'{path_gmx}', 'rmsf', '-s', f'{path_kerja}/step5_1.tpr', '-f', f'{path_kerja}/analisis.xtc', '-o', f'{path_kerja}/rmsf_atom/rmsf_atom.xvg']
        p4 = subprocess.Popen(perintah_4, stdin=subprocess.PIPE)
        p4.communicate(input=b'4\n')

        # Buat RMSF Reseptor
        progress.setValue(5)
        progress.setLabelText("Menghitung RMSF Residu...")
        QApplication.processEvents()
        perintah_5 = [f'{path_gmx}', 'rmsf', '-s', f'{path_kerja}/step5_1.tpr', '-f', f'{path_kerja}/analisis.xtc', '-res', '-o', f'{path_kerja}/rmsf_rec/rmsf_rec.xvg']
        p5 = subprocess.Popen(perintah_5, stdin=subprocess.PIPE)
        p5.communicate(input=b'4\n')

        # Buat Gyration
        progress.setValue(6)
        progress.setLabelText("Menghitung Radius of Gyration...")
        QApplication.processEvents()
        perintah_6 = [f'{path_gmx}', 'gyrate', '-s', f'{path_kerja}/step5_1.tpr', '-f', f'{path_kerja}/step5_1.xtc', '-o', f'{path_kerja}/gyration/gyration.xvg']
        p6 = subprocess.Popen(perintah_6, stdin=subprocess.PIPE)
        p6.communicate(input=b'4\n')

        # Buat SASA
        progress.setValue(7)
        progress.setLabelText("Menghitung SASA...")
        QApplication.processEvents()
        perintah_7 = [f'{path_gmx}', 'sasa', '-s', f'{path_kerja}/step5_1.tpr', '-f', f'{path_kerja}/step5_1.xtc', '-o', f'{path_kerja}/sasa/sasa.xvg']
        p7 = subprocess.Popen(perintah_7, stdin=subprocess.PIPE)
        p7.communicate(input=b'4\n')

        # Buat H-Bond
        progress.setValue(8)
        progress.setLabelText("Menghitung Hydrogen Bonds...")
        QApplication.processEvents()
        perintah_8 = [f'{path_gmx}', 'hbond', '-s', f'{path_kerja}/step5_1.tpr', '-f', f'{path_kerja}/step5_1.xtc', '-num', f'{path_kerja}/hbond/hbond.xvg']
        p8 = subprocess.Popen(perintah_8, stdin=subprocess.PIPE)
        p8.communicate(input=b'1\n13\n')

        progress.close()

        if p1.returncode == 0 and p2.returncode == 0 and p3.returncode == 0 and p4.returncode == 0 and p5.returncode == 0 and p6.returncode == 0 and p7.returncode == 0 and p8.returncode == 0:
            self.pushButton.hide()
            self.pushButton_2.show()
            self.customize_button.show()
            self.select_samples_button.show()
            
            xvg_files = [self.path_folder_kerja + "/RMSD/" + data1 for data1 in os.listdir(self.path_folder_kerja + "/RMSD") if data1.endswith(".xvg")]
            self.current_xvg_files = xvg_files
            
            # Initialize all samples as visible
            samples = [os.path.basename(xvg).split('.')[0] for xvg in xvg_files]
            self.sample_visibility = {sample: True for sample in samples}
            
            self.plot_data(xvg_files)
            QMessageBox.information(self, "Sukses", "Analisis selesai dan berhasil!")
        else:
            QMessageBox.warning(self, "Error", "Terjadi kesalahan saat melakukan analisis!")