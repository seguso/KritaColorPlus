# mousemonitor.py
from PyQt5.QtCore import QObject
from PyQt5.QtGui import (
                QCursor)
from PyQt5.QtWidgets import (
        QApplication,
                QWidget,
                )


from PyQt5.QtCore import (
                Qt,
                QTimer,
                pyqtSignal) # Added pyqtSignal


class MouseMonitor(QObject):
    mouseClicked = pyqtSignal(QWidget)
    mouseReleased = pyqtSignal(QWidget)

    def __init__(self):
        super().__init__()
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_mouse)
        self.timer.start(50)  # 50ms intervallo di controllo
        self.left_button_pressed = False
        self.last_widget = None

    def check_mouse(self):
        current_buttons = QApplication.mouseButtons()
        current_widget = QApplication.widgetAt(QCursor.pos())

        # Gestione pressione del tasto sinistro
        if current_buttons & Qt.LeftButton:
            if not self.left_button_pressed:
                self.left_button_pressed = True
                if current_widget:
                    self.mouseClicked.emit(current_widget)
                self.last_widget = current_widget
        else:
            if self.left_button_pressed:
                self.left_button_pressed = False
                # Emettiamo il segnale se abbiamo un widget valido
                # QPushButton è già una sottoclasse di QWidget, quindi non serve un controllo specifico
                if self.last_widget:
                    self.mouseReleased.emit(self.last_widget)
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