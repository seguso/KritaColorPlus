from typing import Any, List, Optional

# mousemonitor.py
from PyQt5.QtCore import QObject, Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton

from . import globals as g # Import globals for logging

from .recent_color import log

# Helper function to get widget hierarchy
def get_widget_hierarchy(widget: Optional[QWidget]) -> List[QWidget]:
    hierarchy: List[str] = []
    current: Optional[QWidget] = widget
    while current:
    #    class_name: str = current.metaObject().className()
    #    object_name: str = current.objectName()
    #    hierarchy.append(f"{class_name}({object_name or 'NoObjectName'})") # Combine class and object name
        hierarchy.append(current)
        current = current.parent()
    return hierarchy

class MouseMonitor(QObject):
    mouseClicked = pyqtSignal(list)
    mouseReleased = pyqtSignal(list)

    # Attributes with type hints
    timer: QTimer
    left_button_pressed: bool
    last_widget: Optional[QWidget]

    def __init__(self) -> None:
        super().__init__()
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_mouse)
        self.timer.start(50)  # 50ms intervallo di controllo
        self.left_button_pressed = False
        self.last_widget = None

    def is_button_widget(self, widget: Optional[QWidget]) -> bool:
        """Verifica se il widget è un pulsante di qualsiasi tipo"""
        if not widget:
            return False

        # Verifica se è un QPushButton
        if isinstance(widget, QPushButton):
            return True

        # Verifica se il nome della classe contiene 'button' (case insensitive)
        class_name: str = widget.metaObject().className().lower()
        if 'button' in class_name:
            return True

        return False


    
    def check_mouse(self) -> None:
        current_buttons: Qt.MouseButtons = QApplication.mouseButtons() # Type alias for int flags
        current_widget: Optional[QWidget] = QApplication.widgetAt(QCursor.pos())

        # Gestione pressione del tasto sinistro
        if current_buttons & Qt.LeftButton:
            if not self.left_button_pressed:
                self.left_button_pressed = True
                if current_widget:
                    # Print widget hierarchy on mouse down
                    hierarchy: List[str] = get_widget_hierarchy(current_widget)
                    #log(f"Mouse down on widget hierarchy: {hierarchy}")
                    self.mouseClicked.emit(hierarchy)
                self.last_widget = current_widget
        else:
            if self.left_button_pressed:
                self.left_button_pressed = False
                try:
                    # Emettiamo il segnale solo se abbiamo un widget valido e NON è un pulsante
                    if self.last_widget and not self.is_button_widget(self.last_widget):
                        hierarchy = get_widget_hierarchy(self.last_widget) # Use self.last_widget
                        self.mouseReleased.emit(hierarchy) # Emit the hierarchy list
                except RuntimeError:
                    # Potentially log error or handle differently
                    self.last_widget = None # Ensure reset even on error
                finally:
                     # Always reset last_widget after release logic
                    self.last_widget = None


    def isColorSelector(self, widget: Optional[QWidget]) -> bool:
        if not widget:
            return False
        return widget.metaObject().className() == 'KisColorSelector'

    def isPalette(self, hier: list[QWidget]) -> bool:
        if len(hier) < 2:
            return False
        else:
            primo = hier[0]
            secondo = hier[1]
            return ( primo.metaObject().className() == "QWidget" and primo.objectName() == "qt_scrollarea_viewport"
                    and  secondo.metaObject().className() == "KisPaletteView" )
        
        # ['QWidget(qt_scrollarea_viewport)', 'KisPaletteView(paletteView)', ...
        # Note: This currently checks for KisColorSelector, not a palette view.
        # if not widget:
        #     return False
        # return widget.metaObject().className() == 'KisColorSelector'


    def is_krita_canvas(self, widget: Optional[QWidget]) -> bool:
        """Verifica se il widget è il canvas di Krita"""

        #print("\niskritac1\n");
        if not widget:
            #print(f"\n return false. widget = {widget}\n");
            return False
        # TODO: Consider alternative ways to identify canvas if OpenGL is not used
        if widget.metaObject().className() == 'KisOpenGLCanvas2':
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
    

def mouseIsCurrentlyDown() -> bool:
    current_buttons: Qt.MouseButtons = QApplication.mouseButtons() # Type alias for int flags
    return current_buttons & Qt.LeftButton    