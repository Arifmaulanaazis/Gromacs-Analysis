import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from main import Analisis_Gromacs
import os
import shutil

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GROMACS Analysis Tool | Copyright (c) Titan Digitalsoft 2025")
        self.setMinimumSize(900, 700)
        self.folders = []  # List to store selected folders
        
        # Set window icon if available
        icon_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QtGui.QIcon(icon_path))
        
        # Create central widget
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QtWidgets.QVBoxLayout(central_widget)
        
        # Header with title
        header_label = QtWidgets.QLabel("GROMACS Molecular Dynamics Analysis")
        header_font = QtGui.QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header_label.setFont(header_font)
        header_label.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(header_label)
        
        # Description
        desc_label = QtWidgets.QLabel("Add multiple folders to compare GROMACS simulation data")
        desc_label.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(desc_label)
        
        # Folder selection
        folder_layout = QtWidgets.QHBoxLayout()
        self.folder_edit = QtWidgets.QLineEdit()
        self.folder_edit.setPlaceholderText("Select simulation folder...")
        folder_button = QtWidgets.QPushButton("Browse...")
        folder_button.clicked.connect(self.select_folder)
        add_button = QtWidgets.QPushButton("Add Folder")
        add_button.clicked.connect(self.add_folder)
        folder_layout.addWidget(self.folder_edit, 7)
        folder_layout.addWidget(folder_button, 1)
        folder_layout.addWidget(add_button, 1)
        main_layout.addLayout(folder_layout)
        
        # List of added folders
        folder_list_label = QtWidgets.QLabel("Added Folders:")
        folder_list_label.setFont(QtGui.QFont("Arial", 10, QtGui.QFont.Bold))
        main_layout.addWidget(folder_list_label)
        
        self.folder_list = QtWidgets.QListWidget()
        self.folder_list.setMinimumHeight(150)
        self.folder_list.setAlternatingRowColors(True)
        self.folder_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        main_layout.addWidget(self.folder_list)
        
        # Buttons for list management
        list_buttons_layout = QtWidgets.QHBoxLayout()
        remove_button = QtWidgets.QPushButton("Remove Selected")
        remove_button.clicked.connect(self.remove_selected_folders)
        clear_button = QtWidgets.QPushButton("Clear All")
        clear_button.clicked.connect(self.clear_folders)
        list_buttons_layout.addWidget(remove_button)
        list_buttons_layout.addWidget(clear_button)
        main_layout.addLayout(list_buttons_layout)
        
        # Start analysis button
        start_button = QtWidgets.QPushButton("Start Analysis")
        start_button.setMinimumHeight(40)
        button_font = QtGui.QFont()
        button_font.setPointSize(12)
        button_font.setBold(True)
        start_button.setFont(button_font)
        start_button.clicked.connect(self.start_analysis)
        main_layout.addWidget(start_button)
        
        # Status label
        self.status_label = QtWidgets.QLabel("")
        self.status_label.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(self.status_label)
        
        # Add stretch to push everything to the top
        main_layout.addStretch(1)
        
        # Footer with info
        footer_label = QtWidgets.QLabel("GROMACS Analysis Tool - Enhanced Plotting | Copyright (c) Titan Digitalsoft 2025")
        footer_label.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(footer_label)
    
    def select_folder(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Simulation Folder")
        if folder:
            self.folder_edit.setText(folder)
            
            # Check if this is a valid GROMACS simulation folder
            if os.path.exists(os.path.join(folder, "step5_1.tpr")) and os.path.exists(os.path.join(folder, "step5_1.xtc")):
                self.status_label.setText("✓ Valid GROMACS simulation folder detected")
                self.status_label.setStyleSheet("color: green")
            else:
                self.status_label.setText("⚠ Missing required GROMACS files (step5_1.tpr and step5_1.xtc)")
                self.status_label.setStyleSheet("color: red")
    
    def add_folder(self):
        folder = self.folder_edit.text()
        if not folder:
            QtWidgets.QMessageBox.warning(self, "Error", "Please select a folder first")
            return
            
        if not os.path.exists(folder):
            QtWidgets.QMessageBox.warning(self, "Error", "Selected folder does not exist")
            return
            
        # Check if folder is already in the list
        for i in range(self.folder_list.count()):
            if self.folder_list.item(i).data(QtCore.Qt.UserRole) == folder:
                QtWidgets.QMessageBox.warning(self, "Error", "This folder is already in the list")
                return
                
        # Add folder to list
        item = QtWidgets.QListWidgetItem(os.path.basename(folder))
        item.setData(QtCore.Qt.UserRole, folder)  # Store full path as user data
        self.folder_list.addItem(item)
        self.folders.append(folder)
        self.folder_edit.clear()
        
        # Update status
        self.status_label.setText(f"Added folder: {os.path.basename(folder)}")
        self.status_label.setStyleSheet("color: green")
    
    def remove_selected_folders(self):
        selected_items = self.folder_list.selectedItems()
        if not selected_items:
            return
            
        for item in selected_items:
            folder = item.data(QtCore.Qt.UserRole)
            row = self.folder_list.row(item)
            self.folder_list.takeItem(row)
            self.folders.remove(folder)
            
        self.status_label.setText(f"Removed {len(selected_items)} folder(s)")
    
    def clear_folders(self):
        if self.folder_list.count() == 0:
            return
            
        reply = QtWidgets.QMessageBox.question(
            self, "Confirm Clear", "Are you sure you want to clear all folders?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            self.folder_list.clear()
            self.folders = []
            self.status_label.setText("All folders cleared")
    
    def prepare_comparison_folder(self):
        """Create a temporary folder with organized data for comparison"""
        # Create a temporary comparison folder
        temp_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "comparison_temp")
        
        # Remove old temp dir if exists
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                print(f"Error removing old temp dir: {e}")
        
        # Create necessary directories
        try:
            os.makedirs(temp_dir)
            os.makedirs(os.path.join(temp_dir, "RMSD"))
            os.makedirs(os.path.join(temp_dir, "gyration"))
            os.makedirs(os.path.join(temp_dir, "hbond"))
            os.makedirs(os.path.join(temp_dir, "sasa"))
            os.makedirs(os.path.join(temp_dir, "rmsd_pro_lig"))
            os.makedirs(os.path.join(temp_dir, "rmsf_atom"))
            os.makedirs(os.path.join(temp_dir, "rmsf_rec"))
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to create temporary directory: {e}")
            return None
        
        # Copy files with appropriate naming
        progress = QtWidgets.QProgressDialog("Preparing files for comparison...", "Cancel", 0, len(self.folders), self)
        progress.setWindowTitle("Preparing Comparison")
        progress.setWindowModality(QtCore.Qt.WindowModal)
        progress.show()
        
        for i, folder in enumerate(self.folders):
            progress.setValue(i)
            if progress.wasCanceled():
                return None
                
            folder_name = os.path.basename(folder)
            
            # Copy each analysis file with folder name as prefix
            data_types = {
                "RMSD": "rmsd.xvg",
                "gyration": "gyration.xvg",
                "hbond": "hbond.xvg",
                "sasa": "sasa.xvg",
                "rmsd_pro_lig": "rmsd_pro_lig.xvg",
                "rmsf_atom": "rmsf_atom.xvg",
                "rmsf_rec": "rmsf_rec.xvg"
            }
            
            for data_type, filename in data_types.items():
                src_path = os.path.join(folder, data_type, filename)
                if os.path.exists(src_path):
                    dst_path = os.path.join(temp_dir, data_type, f"{folder_name}.xvg")
                    try:
                        shutil.copy2(src_path, dst_path)
                    except Exception as e:
                        print(f"Error copying {src_path}: {e}")
        
        progress.setValue(len(self.folders))
        return temp_dir
    
    def start_analysis(self):
        if len(self.folders) == 0:
            QtWidgets.QMessageBox.warning(self, "Error", "Please add at least one folder for analysis")
            return
        
        # If only one folder, use it directly
        if len(self.folders) == 1:
            folder = self.folders[0]
            if not os.path.exists(os.path.join(folder, "step5_1.tpr")) or not os.path.exists(os.path.join(folder, "step5_1.xtc")):
                QtWidgets.QMessageBox.warning(self, "Error", f"Folder '{os.path.basename(folder)}' does not contain required GROMACS files")
                return
                
            # Create and show the analysis window for single folder
            self.analysis_widget = Analisis_Gromacs(folder)
            analysis_window = QtWidgets.QMainWindow()
            analysis_window.setWindowTitle(f"GROMACS Analysis - {os.path.basename(folder)} | Copyright (c) Titan Digitalsoft 2025")
            analysis_window.setCentralWidget(self.analysis_widget)
            analysis_window.resize(900, 700)
            analysis_window.show()
            
            # Keep a reference to prevent garbage collection
            self.analysis_window = analysis_window
        else:
            # For multiple folders, prepare a comparison folder
            comparison_folder = self.prepare_comparison_folder()
            if not comparison_folder:
                return
                
            # Create and show the analysis window for comparison
            self.analysis_widget = Analisis_Gromacs(comparison_folder)
            analysis_window = QtWidgets.QMainWindow()
            analysis_window.setWindowTitle(f"GROMACS Comparison Analysis - {len(self.folders)} folders")
            analysis_window.setCentralWidget(self.analysis_widget)
            analysis_window.resize(900, 700)
            analysis_window.show()
            
            # Keep a reference to prevent garbage collection
            self.analysis_window = analysis_window

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Set dark palette
    dark_palette = QtGui.QPalette()
    dark_palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
    dark_palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
    dark_palette.setColor(QtGui.QPalette.Base, QtGui.QColor(25, 25, 25))
    dark_palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
    dark_palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
    dark_palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
    dark_palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
    dark_palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
    dark_palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
    dark_palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
    dark_palette.setColor(QtGui.QPalette.Link, QtGui.QColor(42, 130, 218))
    dark_palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(42, 130, 218))
    dark_palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
    
    # Uncomment to use dark theme
    # app.setPalette(dark_palette)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
