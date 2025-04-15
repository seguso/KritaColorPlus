# brush_list_widget.py
# Widget to display and edit the list of brushes in the brush cycler

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QListWidgetItem,
    QLabel, QDialog, QDialogButtonBox, QAbstractItemView, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from krita import Krita
from . import globals as g
from .brush_cycler import brush_cycler

class BrushListWidget(QWidget):
    """Widget to display and edit the list of brushes in the brush cycler"""
    
    brushListChanged = pyqtSignal()  # Signal emitted when the brush list changes
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.update_list()
    
    def setup_ui(self):
        """Set up the user interface"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Title label
        title_label = QLabel("Brush Cycle List")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # List widget to display brushes
        self.brush_list = QListWidget()
        self.brush_list.setDragDropMode(QAbstractItemView.InternalMove)  # Allow reordering by drag and drop
        self.brush_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.brush_list.model().rowsMoved.connect(self.on_rows_moved)  # Connect to rowsMoved signal
        main_layout.addWidget(self.brush_list)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        # Add current brush button
        self.add_button = QPushButton("+")
        self.add_button.setToolTip("Add current brush to list")
        self.add_button.clicked.connect(self.add_current_brush)
        buttons_layout.addWidget(self.add_button)
        
        # Remove selected brush button
        self.remove_button = QPushButton("-")
        self.remove_button.setToolTip("Remove selected brush from list")
        self.remove_button.clicked.connect(self.remove_selected_brush)
        buttons_layout.addWidget(self.remove_button)
        
        # Move up button
        self.up_button = QPushButton("↑")
        self.up_button.setToolTip("Move selected brush up")
        self.up_button.clicked.connect(self.move_brush_up)
        buttons_layout.addWidget(self.up_button)
        
        # Move down button
        self.down_button = QPushButton("↓")
        self.down_button.setToolTip("Move selected brush down")
        self.down_button.clicked.connect(self.move_brush_down)
        buttons_layout.addWidget(self.down_button)
        
        # Clear list button
        self.clear_button = QPushButton("Clear")
        self.clear_button.setToolTip("Clear brush list")
        self.clear_button.clicked.connect(self.clear_brush_list)
        buttons_layout.addWidget(self.clear_button)
        
        main_layout.addLayout(buttons_layout)
    
    def update_list(self):
        """Update the list widget with the current brush list"""
        self.brush_list.clear()
        
        for i, brush_name in enumerate(brush_cycler.brush_list):
            item = QListWidgetItem(brush_name)
            # Highlight the current brush
            if i == g.g_brushCyclerIndex:
                font = item.font()
                font.setBold(True)
                item.setFont(font)
                item.setText(f"{brush_name} (current)")
            
            self.brush_list.addItem(item)
    
    def add_current_brush(self):
        """Add the current brush to the list"""
        if brush_cycler.add_current_brush():
            self.update_list()
            self.brushListChanged.emit()
            g.log(f"Added current brush to cycle list. Total: {len(brush_cycler.brush_list)}")
        else:
            g.log("Could not add current brush to cycle list")
    
    def remove_selected_brush(self):
        """Remove the selected brush from the list"""
        selected_items = self.brush_list.selectedItems()
        if not selected_items:
            return
        
        item = selected_items[0]
        brush_name = item.text()
        # Remove " (current)" suffix if present
        if " (current)" in brush_name:
            brush_name = brush_name.replace(" (current)", "")
        
        # Get the index of the selected item
        index = self.brush_list.row(item)
        
        # Remove the brush from the cycler
        if brush_cycler.remove_brush(brush_name):
            self.update_list()
            self.brushListChanged.emit()
            g.log(f"Removed brush '{brush_name}' from cycle list")
        else:
            g.log(f"Could not remove brush '{brush_name}' from cycle list")
    
    def move_brush_up(self):
        """Move the selected brush up in the list"""
        selected_items = self.brush_list.selectedItems()
        if not selected_items:
            return
        
        current_row = self.brush_list.row(selected_items[0])
        if current_row > 0:
            # Get the brush list from the cycler
            brush_list = brush_cycler.brush_list.copy()
            
            # Swap the brushes
            brush_list[current_row], brush_list[current_row - 1] = brush_list[current_row - 1], brush_list[current_row]
            
            # Update the cycler's brush list
            brush_cycler.set_brush_list(brush_list)
            
            # Update the list widget
            self.update_list()
            
            # Select the moved item
            self.brush_list.setCurrentRow(current_row - 1)
            
            self.brushListChanged.emit()
    
    def move_brush_down(self):
        """Move the selected brush down in the list"""
        selected_items = self.brush_list.selectedItems()
        if not selected_items:
            return
        
        current_row = self.brush_list.row(selected_items[0])
        if current_row < self.brush_list.count() - 1:
            # Get the brush list from the cycler
            brush_list = brush_cycler.brush_list.copy()
            
            # Swap the brushes
            brush_list[current_row], brush_list[current_row + 1] = brush_list[current_row + 1], brush_list[current_row]
            
            # Update the cycler's brush list
            brush_cycler.set_brush_list(brush_list)
            
            # Update the list widget
            self.update_list()
            
            # Select the moved item
            self.brush_list.setCurrentRow(current_row + 1)
            
            self.brushListChanged.emit()
    
    def clear_brush_list(self):
        """Clear the brush list after confirmation"""
        # Ask for confirmation
        reply = QMessageBox.question(
            self, 
            "Clear Brush List", 
            "Are you sure you want to clear the brush list?", 
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            brush_cycler.clear_brush_list()
            self.update_list()
            self.brushListChanged.emit()
            g.log("Cleared brush cycle list")
    
    def on_rows_moved(self, parent, start, end, destination, row):
        """Handle rows being moved by drag and drop"""
        # Get the new order of brushes
        new_brush_list = []
        for i in range(self.brush_list.count()):
            item = self.brush_list.item(i)
            brush_name = item.text()
            # Remove " (current)" suffix if present
            if " (current)" in brush_name:
                brush_name = brush_name.replace(" (current)", "")
            new_brush_list.append(brush_name)
        
        # Update the cycler's brush list
        brush_cycler.set_brush_list(new_brush_list)
        self.update_list()
        self.brushListChanged.emit()

# Dialog to show the brush list widget
class BrushListDialog(QDialog):
    """Dialog to display and edit the brush list"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Brush Cycle List Editor")
        self.resize(300, 400)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Add the brush list widget
        self.brush_list_widget = BrushListWidget(self)
        layout.addWidget(self.brush_list_widget)
        
        # Add standard dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)