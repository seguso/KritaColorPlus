from typing import Any

# mousemonitor.py
from PyQt5.QtCore import QObject
from PyQt5.QtGui import (
                QCursor)
from PyQt5.QtWidgets import (
        QApplication,
                QWidget,
                QPushButton,
                )


from PyQt5.QtCore import (
                Qt,
                QTimer,
                pyqtSignal) # Added pyqtSignal


from . import globals as g # Import globals for logging

# Helper function to get widget hierarchy
def get_widget_hierarchy(widget):
   hierarchy = []
   current = widget
   while current:
       hierarchy.append(current.metaObject().className())
       current = current.parent()
   return hierarchy

class MouseMonitor(QObject):
    mouseClicked = pyqtSignal(QObject)
    mouseReleased = pyqtSignal(QObject)

    def __init__(self):
        super().__init__()
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_mouse)
        self.timer.start(50)  # 50ms intervallo di controllo
        self.left_button_pressed = False
        self.last_widget = None

    def is_button_widget(self, widget):
        """Verifica se il widget è un pulsante di qualsiasi tipo"""
        if not widget:
            return False
            
        # Verifica se è un QPushButton
        if isinstance(widget, QPushButton):
            return True
            
        # Verifica se il nome della classe contiene 'button' (case insensitive)
        class_name = widget.metaObject().className().lower()
        if 'button' in class_name:
            return True
            
        return False
        
    def check_mouse(self):
        current_buttons = QApplication.mouseButtons()
        current_widget = QApplication.widgetAt(QCursor.pos())

        # Gestione pressione del tasto sinistro
        if current_buttons & Qt.LeftButton:
            if not self.left_button_pressed:
                self.left_button_pressed = True
                if current_widget:
                    # Print widget hierarchy on mouse down
                    hierarchy = get_widget_hierarchy(current_widget)
                    g.log(f"Mouse down on widget hierarchy: {hierarchy}")
                    self.mouseClicked.emit(current_widget)
                self.last_widget = current_widget
        else:
            if self.left_button_pressed:
                self.left_button_pressed = False
                try:
                    # Emettiamo il segnale solo se abbiamo un widget valido e NON è un pulsante
                    if self.last_widget and not self.is_button_widget(self.last_widget):
                        self.mouseReleased.emit(self.last_widget)
                except RuntimeError:
                    self.last_widget = None
                self.last_widget = None

    def is_krita_canvas(self, widget):
        """Verifica se il widget è il canvas di Krita"""

        #print("\niskritac1\n");
        if not widget:
            #print(f"\n return false. widget = {widget}\n");
            return False
        if widget.metaObject().className() == 'KisOpenGLCanvas2': # TODO potrebbe non funzionare senza opengl
            #print("\ndetected canvas krita\n");
            return True
            # parent = widget.parent()
            # while parent:
            #     if hasattr(parent, 'canvas') and 'KisCanvas' in str(type(parent)):
            #         return True
            #     parent = parent.parent()

        # else:
        #     print(f"class name { widget.metaObject().className()}. widget = {widget}\n")
        return False