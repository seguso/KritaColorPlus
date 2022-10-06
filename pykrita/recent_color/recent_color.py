from krita import *

from krita import (
                Krita,)

from PyQt5.QtCore import (
                Qt,
                QEvent,
                QPointF,
                QRect,
                QTimer)

from PyQt5.QtGui import (
                QTransform,
                QPainter,
                QBrush,
                QColor,
                QPolygonF,
                QInputEvent,
                QCursor)

from PyQt5.QtWidgets import (
                QWidget,
                QMdiArea,
                QTextEdit,
                QAbstractScrollArea)


# from PyQt5 import QtWidgets, QtCore, QtGui, uic
import os.path
import time
import datetime
import xml
import math

timeMessage = 300
stepOpacity = 20

g_mixing_step = 0.02

g_step_mixing_target_distance = 2.5



print(Krita.instance().filters())


def minimize_views():
        """
        https://doc.qt.io/qtforpython-5/PySide2/QtWidgets/QMdiArea.html
        https://doc.qt.io/qtforpython-5/PySide2/QtWidgets/QMdiSubWindow.html
        https://doc.qt.io/qtforpython-5/PySide2/QtWidgets/QWidget.html#PySide2.QtWidgets.PySide2.QtWidgets.QWidget.showMinimized
        """        
        app = Krita.instance()
        win = app.activeWindow()
        q_win = win.qwindow()
        mdi_area = q_win.findChild(QMdiArea)
        for sub_win in mdi_area.subWindowList():
                sub_win.showMinimized()


def set_active_view_stay_on_top(new_state):
        """
        https://doc.qt.io/qtforpython-5/PySide2/QtWidgets/QMdiArea.html
        https://doc.qt.io/qtforpython-5/PySide2/QtWidgets/QMdiSubWindow.html
        https://doc.qt.io/qtforpython-5/PySide2/QtWidgets/QWidget.html#PySide2.QtWidgets.PySide2.QtWidgets.QWidget.setWindowFlag
        """
        app = Krita.instance()
        win = app.activeWindow()
        q_win = win.qwindow()
        mdi_area = q_win.findChild(QMdiArea)
        sub_win = mdi_area.activeSubWindow()
        sub_win.setWindowFlag(Qt.WindowStaysOnTopHint, new_state)



def quickMessage(msg, timeMessage = 300):
        application = Krita.instance()
        application.activeWindow().activeView().showFloatingMessage(msg, QIcon(), timeMessage, 1)
        
        
def rgbOfManagedColor( c):
            co = c.components()
            return rgb(co[0] * 255 , co[1] * 255, co[2] * 255, 255)

class rgb:
        def __init__(self, r, g, b, a):
                self.a = a
                self.r = r
                self.g = g
                self.b = b
                
        def print(self, msg):
                print(f"{msg}:   {self.toString()}")
                
        def toString(self):
            return f" r:{self.r}, g:{self.g}, b:{self.b} ,a:{self.a}"

        def average(self, c):
                return rgb((self.r + c.r) / 2,
                                                        (self.g + c.g) / 2,
                                                        (self.b + c.b) / 2,
                                                        255)

        def distance(self, c):
            return math.sqrt((self.r - c.r)*(self.r - c.r) + (self.g - c.g)*(self.g - c.g) + (self.b - c.b)*(self.b - c.b) )
            
        def equals(self, c):
            return c.r == self.r and c.g == self.g and c.b == self.b

        
class xy:
        def __init__(self, x,y):
                self.x = x
                self.y = y
                
        def print(self, msg):
                print(f"{msg}:   r:{self.r}, g:{self.g}, b:{self.b} ,a:{self.a}")



def get_q_view(view):
        window = view.window()
        q_window = window.qwindow()
        q_stacked_widget = q_window.centralWidget()
        q_mdi_area = q_stacked_widget.findChild(QMdiArea)
        for v, q_mdi_view in zip(window.views(), q_mdi_area.subWindowList()):
                if v == view:
                        return q_mdi_view.widget()


def calcolaCompositeColor(colors):
        mergedColor = None
        for col in colors:
                        col.print("cur color")
                        if mergedColor is None:
                                mergedColor = col
                                mergedColor.print("setto merged color")
                        else:
                                a = float(col.a) / 255.0
                                print (f"a = {a}")
                                invA = (1.0 - a) 
                                print (f"invA = {invA}")
                                mergedColor = rgb( mergedColor.r * invA + col.r * a,
                                                                                mergedColor.g * invA + col.g * a,
                                                                                mergedColor.b* invA + col.b * a,
                                                                                255)
                                mergedColor.print("merged color")
        return mergedColor
        
def get_q_canvas(q_view):
        if q_view is None:
                return None
                
        scroll_area = q_view.findChild(QAbstractScrollArea)
        viewport = scroll_area.viewport()
        for child in viewport.children():
                cls_name = child.metaObject().className()
                if cls_name.startswith('Kis') and ('Canvas' in cls_name):
                        return child


def get_transform(view):
        def _offset(scroller):
                mid = (scroller.minimum() + scroller.maximum()) / 2.0
                return -(scroller.value() - mid)
        canvas = view.canvas()
        document = view.document()
        q_view = get_q_view(view)
        if q_view is not None:
                area = q_view.findChild(QAbstractScrollArea)
                zoom = (canvas.zoomLevel() * 72.0) / document.resolution()
                transform = QTransform()
                transform.translate(
                                _offset(area.horizontalScrollBar()),
                                _offset(area.verticalScrollBar()))
                transform.rotate(canvas.rotation())
                transform.scale(zoom, zoom)
                return transform
        else:
                return None

def get_cursor_in_document_coords():
        app = Krita.instance()
        view = app.activeWindow().activeView()
        if view.document():
                q_view = get_q_view(view)
                q_canvas = get_q_canvas(q_view)        
                transform = get_transform(view)
                if transform is not None:
                        transform_inv, _ = transform.inverted()
                        global_pos = QCursor.pos()
                        local_pos = q_canvas.mapFromGlobal(global_pos)
                        center = q_canvas.rect().center()
                        return transform_inv.map(local_pos - QPointF(center))
                else:
                        return None

# from PyQt5.QtCore import (
                # Qt,)

# from PyQt5.QtWidgets import (
                # QTextEdit,
                # QTableView)





def listEqual(l1,l2):
   if(len(l1)==len(l2) and len(l1)==sum([1 for i,j in zip(l1,l2) if i==j])):
          return True
   else:
          return False
          
# import numpy as np

# def rgb2hsv(rgb):
    # """ convert RGB to HSV color space

    # :param rgb: np.ndarray
    # :return: np.ndarray
    # """

    # rgb = rgb.astype('float')
    # maxv = np.amax(rgb, axis=2)
    # maxc = np.argmax(rgb, axis=2)
    # minv = np.amin(rgb, axis=2)
    # minc = np.argmin(rgb, axis=2)

    # hsv = np.zeros(rgb.shape, dtype='float')
    # hsv[maxc == minc, 0] = np.zeros(hsv[maxc == minc, 0].shape)
    # hsv[maxc == 0, 0] = (((rgb[..., 1] - rgb[..., 2]) * 60.0 / (maxv - minv + np.spacing(1))) % 360.0)[maxc == 0]
    # hsv[maxc == 1, 0] = (((rgb[..., 2] - rgb[..., 0]) * 60.0 / (maxv - minv + np.spacing(1))) + 120.0)[maxc == 1]
    # hsv[maxc == 2, 0] = (((rgb[..., 0] - rgb[..., 1]) * 60.0 / (maxv - minv + np.spacing(1))) + 240.0)[maxc == 2]
    # hsv[maxv == 0, 1] = np.zeros(hsv[maxv == 0, 1].shape)
    # hsv[maxv != 0, 1] = (1 - minv / (maxv + np.spacing(1)))[maxv != 0]
    # hsv[..., 2] = maxv

    # return hsv

    
# def hsv2rgb(hsv):
    # """ convert HSV to RGB color space

    # :param hsv: np.ndarray
    # :return: np.ndarray
    # """

    # hi = np.floor(hsv[..., 0] / 60.0) % 6
    # hi = hi.astype('uint8')
    # v = hsv[..., 2].astype('float')
    # f = (hsv[..., 0] / 60.0) - np.floor(hsv[..., 0] / 60.0)
    # p = v * (1.0 - hsv[..., 1])
    # q = v * (1.0 - (f * hsv[..., 1]))
    # t = v * (1.0 - ((1.0 - f) * hsv[..., 1]))

    # rgb = np.zeros(hsv.shape)
    # rgb[hi == 0, :] = np.dstack((v, t, p))[hi == 0, :]
    # rgb[hi == 1, :] = np.dstack((q, v, p))[hi == 1, :]
    # rgb[hi == 2, :] = np.dstack((p, v, t))[hi == 2, :]
    # rgb[hi == 3, :] = np.dstack((p, q, v))[hi == 3, :]
    # rgb[hi == 4, :] = np.dstack((t, p, v))[hi == 4, :]
    # rgb[hi == 5, :] = np.dstack((v, p, q))[hi == 5, :]

    # return rgb
    
    
    
class MyExtension(Extension):

        def __init__(self, parent):
                # This is initialising the parent, always important when subclassing.
                super().__init__(parent)
                
                
                self.last_color_picked = None # di tipo rgb
                
                self.g_how_much_canvas_to_pick = 0.4
                self.mix_radius = 2 # pixel
                
                #self.g_how_much_canvas_to_pick_old = 0.3
                
                self.mixing_target_distance = 25.0
                
                self.correct_color_for_transparency = True
                # creo il timer per il mixing
                # self.timer = QTimer()
                # self.timer.timeout.connect(self.mixOnTimer)
                # self.timer.start(40)
                
                print("LastColor init ok")


                
        def setup(self):
                
                
                
                
                self.currentColor = [0,0,0,0]
                self.previousColor = [0,0,0,0]
                self.inited = False
                
                print("LastColor setup ok")
                
                
                
        
        def switchToLastColor(self):
                try:
                        # doc  = Krita.instance().activeWindow().activeView().document()
                        # print(doc)
                        
                        # sel  = doc.selection()
                        # print(sel )
                        
                        # x = sel.x()
                        # print(x)
        
                        pos = QtGui.QCursor.pos()
                        print("cursor absolute = ", pos)

                        win = Krita.instance().activeWindow().qwindow().mapFromGlobal(pos);

                        print("cursor mapped = ", win)
        
                        acView = Krita.instance().activeWindow().activeView()
                        if not self.inited:
                                print ("swap: initializing...")
                                
                                
                                
                                
                                
                                
                                
                                
                                
                                app = Krita.instance()
                                history_docker = next((d for d in app.dockers() if d.objectName() == 'History'), None)
                                kis_undo_view = next((v for v in history_docker.findChildren(QListView) if v.metaObject().className() == 'KisUndoView'), None)
                                s_model = kis_undo_view.selectionModel()
                                s_model.currentChanged.connect(self._on_history_was_made)
                                
                                self.inited = True;
                                print ("swap: initialized")
                                
                                acView.showFloatingMessage("Last color initialized. Press again to use.", QIcon(), timeMessage * 2, 1)
                        else:
                                
                                

                                col = acView.foregroundColor()
                                comp = col.components()
                                
                                
                                col.setComponents(self.previousColor)
                                acView.setForeGroundColor(col)
                                
                                
                                # setto anche il fg virtuale
                                
                                self.last_color_picked = rgb( int  (comp[0] * 255.0), int  (comp[1] * 255.0), int  (comp[2] * 255.0), 1)
                                
                                self.previousColor = self.currentColor
                                
                                acView.showFloatingMessage("Last color", QIcon(), timeMessage , 1)
                                        
                except Exception as e:
                                acView.showFloatingMessage(f"error {e}.", QIcon(), timeMessage * 2, 1)
                                print("errore trovato in swap:")
                                print(e)
                                
                                


        
        def _on_history_was_made(self):
                # print ("user painted")
                try:
                        
                        acView = Krita.instance().activeWindow().activeView()
                        if acView is not None: 
                                col = acView.foregroundColor()
                                if col is not None:   
                                        comp = col.components()
                                        if listEqual( comp, self.currentColor ):   # user did not change color
                                                 pass
                                        else:  # user changed color
                                                print("color changed")
                                                self.previousColor = list.copy(self.currentColor) 
                                                self.currentColor = list.copy(comp)
                                

                                
                except:
                                print("found error")
                                #self.timer_hm.stop()
                                raise

        def mixOld(self):
                app = Krita.instance()
                win = app.activeWindow()
                if win is not None:
                        view = win.activeView()
                        if view is not None:
                                document = view.document()
                                if document:
                                        center = QPointF(0.5 * document.width(), 0.5 * document.height())
                                        p = get_cursor_in_document_coords()
                                        if p is not None:
                                                doc_pos = p + center
                                                print(f'cursor at: x={doc_pos.x()}, y={doc_pos.y()}')
                                                
                                                self.pixelBytes = document.activeNode().pixelData(doc_pos.x(), doc_pos.y(), 1, 1)
                                                
                                                self.imageData = QImage(self.pixelBytes, 1, 1, QImage.Format_RGBA8888)
                                                self.pixelC = self.imageData.pixelColor(0,0)
                                                print(f"color under cursor = {self.pixelC.red()}, {self.pixelC.green()}, {self.pixelC.blue()}")
                                                
                                                fg = view.foregroundColor()
                                                comp = fg.components() 
                                                print(f"fg color = {comp}")
                 
                 
                                                canv = 0.5 #I pick half color from canvas
                                                fgMul = 1.0 - canv
                                                comp[0] = comp[0] * fgMul + (self.pixelC.red() / 255.0)  * canv
                                                comp[1] = comp[1] * fgMul + (self.pixelC.green() / 255.0)  * canv
                                                comp[2] = comp[2] * fgMul + (self.pixelC.blue()  / 255.0)  * canv
                                          
                                                fg.setComponents(comp)
                                                
                                                view.setForeGroundColor(fg)

                

        def mixFgColorWithBgColor(self):
                app = Krita.instance()
                win = app.activeWindow()
                if win is not None:
                        view = win.activeView()
                        if view is not None:
                                document = view.document()
                                if document:
                                        center = QPointF(0.5 * document.width(), 0.5 * document.height())
                                        p = get_cursor_in_document_coords()
                                        
                                        doc_pos = p + center
                                        print(f'cursor at: x={doc_pos.x()}, y={doc_pos.y()}')
                                        
                                        
                                        parentNode = document.activeNode().parentNode()
                                        
                                        
                                        if parentNode is not None:
                                        
                                                brothers = parentNode.childNodes()
                                                colors = []
                                                
                                                #costruisco colors
                                                for curLayer in brothers:
                                                
                                                        self.pixelBytes = curLayer.pixelData(doc_pos.x(), doc_pos.y(), 1, 1)
                                                        
                                                        self.imageData = QImage(self.pixelBytes, 1, 1, QImage.Format_RGBA8888)
                                                        self.pixelC = self.imageData.pixelColor(0,0)
                                                        
                                                        # devo correggere l'alpha del pixel con l'alpha del layer. ma non lo correggo se il layer è quello attuale, che è trasparente. così la pennellata successiva si vede uguale
                                                        if curLayer.uniqueId() == document.activeNode().uniqueId():
                                                            correzMul = 1.0
                                                        else:
                                                            layerOpac = curLayer.opacity() # tra  0 e 255
                                                            correzMul = float(layerOpac) /  255.0
                                                        

                                                        print(f"color under cursor =  r:{self.pixelC.red()}, g:{self.pixelC.green()}, b:{self.pixelC.blue()} ,a:{self.pixelC.alpha() }, a corretto = {self.pixelC.alpha() * correzMul}")
                                                        
                                                        colors.append(  rgb(self.pixelC.red(),  self.pixelC.green(),  self.pixelC.blue(),  self.pixelC.alpha() * correzMul ))
                                                
                                                #creo il colore composito dei layer. questo è il bgcolor                                                
                                                bgColor = calcolaCompositeColor(colors)
                                                bgColor.print("bgColor")
                                                                
                                                
                                                                
                                                # setto il fg color uguale a merged color mischiato con il fg
                                                fg = view.foregroundColor() #tipo ManagedColor
                                                print(f"fg  = {fg}")
                                                
                                                fg2 = rgbOfManagedColor(fg)
                                                fg2.print("fg2")
                                                
                                                comp = fg.components() 
                                                print(f"fg color = {comp}")
                 
                                                dist = fg2.distance(bgColor)
                                                print(f"distance = {dist}")
                 
                                                
                                                curDist = None
                                                
                                                # calcola curFg
                                                if dist  <= self.mixing_target_distance:
                                                    #i colori sono molto vicini. prendi tutto il colore canvas
                                                    curFg = bgColor
                                                    curDist = dist
                                                else:  # i colori sono lontani. avvicina poco a poco finché la distanza del curFg dall'origFg non diventa > target
                                                
                                                    stepMul = 0.001
                                                    
                                                    
                                                    curMul = 0.0
                                                    
                                                    while True:
                                                        
                                                        curFg = rgb( fg2.r * curMul + bgColor.r * (1.0 - curMul),
                                                                                    fg2.g * curMul + bgColor.g * (1.0 - curMul),
                                                                                    fg2.b * curMul + bgColor.b * (1.0 - curMul),
                                                                                    255)
                                                                                    
                                                        curDist = curFg.distance(fg2)
                                                        
                                                        print(f"iterando. mul  = {curMul}, dist  tra {curFg.toString()} e {fg2.toString()} = {curDist}. ")
                                                        
                                                        if curDist <= self.mixing_target_distance:  
                                                            break
                                                            
                                                        curMul += stepMul   
                                                            
                                                        
                                                #canv = howMuchCanvas # pick half color from canvas
                                                
                                                comp[0] = curFg.r / 255.0
                                                comp[1] = curFg.g / 255.0
                                                comp[2] = curFg.b / 255.0
                                                
                                                
                                                # fgMul = 1.0 - canv
                                                # comp[0] = comp[0] * fgMul + (bgColor.r / 255.0)  * canv
                                                # comp[1] = comp[1] * fgMul + (bgColor.g / 255.0)  * canv
                                                # comp[2] = comp[2] * fgMul + (bgColor.b  / 255.0)  * canv
                                                
                                            
                                          
                                                fg.setComponents(comp)
                                                
                                                view.setForeGroundColor(fg)
                                                
                                                
                                                # setto anche il virtual fg color al result del mix
                                                self.last_color_picked = rgb( int  (comp[0] * 255.0), int  (comp[1] * 255.0), int  (comp[2] * 255.0), 1)
                                                
                                                
                                                
                                                # messaggio
                                                if curFg.equals(bgColor):
                                                    view.showFloatingMessage(f"Picked whole color from canvas because distance was small ({round(curDist)})", QIcon(), timeMessage, 1)
                                                else:
                                                    view.showFloatingMessage(f"Picked a bit of color from canvas. Distance: {round(curDist)}", QIcon(), timeMessage, 1)
                                                
                                                

        def mixOnTimer(self):
                print("timer 1")
                if self.last_color_picked is None:
                        return
                        
                print("timer 2")        
                app = Krita.instance()
                win = app.activeWindow()
                if win is not None:
                        view = win.activeView()
                        if view is not None:
                                document = view.document()
                                if document:
                                        center = QPointF(0.5 * document.width(), 0.5 * document.height())
                                        p = get_cursor_in_document_coords()
                                        if p is None:
                                                print ("aborted mixOnTimer")
                                                return;
                                                
                                        doc_pos = p + center
                                        print(f'cursor at: x={doc_pos.x()}, y={doc_pos.y()}')
                                        
                                        
                                        parentNode = document.activeNode().parentNode()
                                        
                                        
                                        if parentNode is not None:
                                        
                                                brothers = parentNode.childNodes()
                                                colors = []
                                                
                                                positions = [ xy(doc_pos.x(), doc_pos.y()),
                                                                                                xy(doc_pos.x() + self.mix_radius, doc_pos.y() + self.mix_radius),
                                                                                                xy(doc_pos.x() - self.mix_radius, doc_pos.y() + self.mix_radius),
                                                                                                xy(doc_pos.x() + self.mix_radius, doc_pos.y() - self.mix_radius),
                                                                                                xy(doc_pos.x() - self.mix_radius, doc_pos.y() - self.mix_radius) ]
                                                                        





                                                                        
                                                merged_colors = [] # lista di rgb, uno per posizione
                                                
                                                                                         
                                                
                                                
                                                
                                                for pos in positions:
                                                
                                                        #costruisco colors
                                                        for curLayer in brothers:
                                                        
                                                                self.pixelBytes = curLayer.pixelData(pos.x, pos.y, 1, 1)
                                                                
                                                                self.imageData = QImage(self.pixelBytes, 1, 1, QImage.Format_RGBA8888)
                                                                self.pixelC = self.imageData.pixelColor(0,0)
                                                                print(f"color under cursor =  r:{self.pixelC.red()}, g:{self.pixelC.green()}, b:{self.pixelC.blue()} ,a:{self.pixelC.alpha()}")
                                                                
                                                                colors.append(  rgb(self.pixelC.red(),  self.pixelC.green(),  self.pixelC.blue(),  self.pixelC.alpha() ))
                                                        
                                                        #creo il colore composito
                                                        
                                                        mergedColor = calcolaCompositeColor(colors); # tipo rgb
                                                                                                                
                                                        merged_colors.append(mergedColor)

                                                                
                                                                
                                                # faccio la media di tutti i merged colors
                                                media  = merged_colors[0]
                                                for  m in merged_colors:
                                                        media = m.average(media)
                                                        
                                                mergedColor = media
                                                                
                                                # setto il fg color uguale a merged color mischiato con il memorizzato (non con il fg)
                                                
                                                fg = view.foregroundColor() 
                                                comp = fg.components() 
                                                print(f"fg color = {comp}")
                 
                 
                                                
                                                canv = self.g_how_much_canvas_to_pick
                                                
                                                fgMul = 1.0 - canv
                                                comp[0] = (self.last_color_picked.r/255.0) * fgMul + (mergedColor.r / 255.0)  * canv
                                                comp[1] = (self.last_color_picked.g / 255.0) * fgMul + (mergedColor.g / 255.0)  * canv
                                                comp[2] = (self.last_color_picked.b / 255.0) * fgMul + (mergedColor.b  / 255.0)  * canv
                                                
                                                # comp[0] =  (mergedColor.r / 255.0)  
                                                # comp[1] =  (mergedColor.g / 255.0)
                                                # comp[2] = (mergedColor.b  / 255.0)
                                          
                                                fg.setComponents(comp)
                                                
                                                view.setForeGroundColor(fg)
                                                
                                                

                
        def mixSmall(self):
                return self.mix(0.66)  #0.66 from canvas
                
        def mixBig(self):
                return self.mix( 0.33)  #0.33 from canvas
        
        # def mixHalf(self):
                # return self.mix( self.g_how_much_canvas_to_pick_old) 
                                   
        def pick(self):
                app = Krita.instance()
                win = app.activeWindow()
                if win is not None:
                        view = win.activeView()
                        if view is not None:
                                document = view.document()
                                if document:
                                        center = QPointF(0.5 * document.width(), 0.5 * document.height())
                                        p = get_cursor_in_document_coords()
                                        doc_pos = p + center
                                        print(f'cursor at: x={doc_pos.x()}, y={doc_pos.y()}')
                                        
                                        parentNode = document.activeNode().parentNode()
                                        
                                        
                                        if parentNode is not None:
                                        
                                                brothers = parentNode.childNodes()
                                                colors = []
                                                
                                                #costruisco colors
                                                for curLayer in brothers:
                                                
                                                        self.pixelBytes = curLayer.pixelData(doc_pos.x(), doc_pos.y(), 1, 1)
                                                        
                                                        self.imageData = QImage(self.pixelBytes, 1, 1, QImage.Format_RGBA8888)
                                                        self.pixelC = self.imageData.pixelColor(0,0) # valori tra 0 e 255

                                                        # devo correggere l'alpha del pixel con l'alpha del layer. ma non lo correggo se il layer è quello attuale, che è trasparente. così la pennellata successiva si vede uguale
                                                        if curLayer.uniqueId() == document.activeNode().uniqueId():
                                                            correzMul = 1.0
                                                        else:
                                                            layerOpac = curLayer.opacity() # tra  0 e 255
                                                            correzMul = float(layerOpac) /  255.0
                                                            
                                                        

                                                        print(f"color under cursor =  r:{self.pixelC.red()}, g:{self.pixelC.green()}, b:{self.pixelC.blue()} ,a:{self.pixelC.alpha() }, a corretto = {self.pixelC.alpha() * correzMul}")
                                                        
                                                        colors.append(  rgb(self.pixelC.red(),  self.pixelC.green(),  self.pixelC.blue(),  self.pixelC.alpha() * correzMul ))
                                                
                                                #creo il colore composito
                                                
                                                mergedColor = calcolaCompositeColor(colors);
                                                                                                                
                                                                
                                                # if self.correct_color_for_transparency:
                                                    # #risaturiamo in modo tale che la somma resti uguale
                                                    # sommaOld = mergedColor.r + mergedColor.g + mergedColor.b
                                                    
                                                    # # deve essere uguale a mul * curLayerOpac01 * (mergedColor.r + mergedColor.g + mergedColor.b)
                                                    
                                                    # curLayerOpac01 =  float (document.activeNode().opacity()) / 255.0  #tra 0 e 1
                                                    
                                                    # # # formula: mulA è tale che (merged.a * mulA) * curLayerOpac =  merged.a  => mul = 1 / curlayeropac
                                                    # # print(f"  curLayerOpac01 = {curLayerOpac01}, newr = {mergedColor.r / curLayerOpac01 },    newg = {mergedColor.g / curLayerOpac01 },    newb = {mergedColor.b / curLayerOpac01}")
                                                    # # # newR * curLayerOpac01 = merged.r
                                                    # mergedColor = rgb(   min (255, mergedColor.r / curLayerOpac01 ),    min(255,mergedColor.g / curLayerOpac01 ),    min(255, mergedColor.b / curLayerOpac01 ),  255)
                                                                
                                                                

                                                self.last_color_picked = mergedColor #lo memorizzo
                                                
                                                # setto il fg color uguale a merged color
                                                fg = view.foregroundColor()
                                                comp = fg.components() 
                                                print(f"fg color = {comp}")
                 
                                                comp[0] =  (mergedColor.r / 255.0)  
                                                comp[1] =  (mergedColor.g / 255.0)
                                                comp[2] = (mergedColor.b  / 255.0)
                                          
                                                fg.setComponents(comp)
                                                
                                                view.setForeGroundColor(fg)

                                                # messaggio
                                                view.showFloatingMessage("Pick color", QIcon(), timeMessage, 1)
                                                
        
        
        
        # def increaseMixing(self):
                # self.g_how_much_canvas_to_pick += g_mixing_step
                # if self.g_how_much_canvas_to_pick > 1.0:
                        # self.g_how_much_canvas_to_pick = 1.0
                        
                        
                # quickMessage(f"Increased mixing to {self.g_how_much_canvas_to_pick}")
        
        # def decreaseMixing(self):
                # self.g_how_much_canvas_to_pick -= g_mixing_step
                # if self.g_how_much_canvas_to_pick < 0.0:
                        # self.g_how_much_canvas_to_pick = 0.0
                        
                # quickMessage(f"Decreased mixing to {self.g_how_much_canvas_to_pick}")
        

        # def increaseMixingOrig(self):
                # self.g_how_much_canvas_to_pick_old += g_mixing_step
                # if self.g_how_much_canvas_to_pick_old > 1.0:
                        # self.g_how_much_canvas_to_pick_old = 1.0
                        
                        
                # quickMessage(f"Increased mixing to {self.g_how_much_canvas_to_pick_old }")
        
        # def decreaseMixingOrig(self):
                # self.g_how_much_canvas_to_pick_old -= g_mixing_step
                # if self.g_how_much_canvas_to_pick_old < 0.0:
                        # self.g_how_much_canvas_to_pick_old = 0.0
                        
                # quickMessage(f"Decreased mixing to {self.g_how_much_canvas_to_pick_old}")
        
        def increaseMixingOrig(self):
                self.mixing_target_distance += g_step_mixing_target_distance
                if self.mixing_target_distance > 255.0:
                        self.mixing_target_distance = 255.0
                        
                        
                quickMessage(f"Increased mixing. Target distance from fg color: {round(self.mixing_target_distance )}")
        
        def decreaseMixingOrig(self):
                self.mixing_target_distance -= g_step_mixing_target_distance
                if self.mixing_target_distance < 0.0:
                        self.mixing_target_distance = 0.0
                        
                quickMessage(f"Decreased mixing. Target distance from fg color: {round(self.mixing_target_distance)}")
                
        def increaseLayerOpacity(self):
        
                #self.layerMergeAndCreate() # conviene, perche' tanto significa che i segni precedenti non si vedono.
                
                application = Krita.instance()
                currentDoc = application.activeDocument()
                activeLayer = currentDoc.activeNode()
                curOpac = activeLayer.opacity()
                newOpac = curOpac + stepOpacity  
                
                if newOpac > 255:
                        newOpac = 255
                activeLayer.setOpacity(newOpac)
                
                
                currentDoc.refreshProjection()           #altrimenti non si aggiorna
                
                # #aggiro bug di setopacity
                # parentNode = activeLayer.parentNode()
                # if parentNode is not None:
                        # newLa = activeLayer.clone()
                        # activeLayer.remove()
                        # parentNode.addChildNode(newLa, None)
                
                
                
                application.activeWindow().activeView().showFloatingMessage(f"Increased layer opacity to {round(newOpac * 100.0 / 255.0)}", QIcon(), timeMessage, 1)
        

        def decreaseLayerOpacity(self):
                
                # application = Krita.instance()
                # currentDoc = application.activeDocument()
                # activeLayer = currentDoc.activeNode()
                # blurFilter = application.filter('gaussian blur')
                # blurFilter.apply(activeLayer, 0, 0, 3000, 2000)
                
                #self.layerMergeAndCreate() # conviene, perche' tanto significa che i segni precedenti non si vedono.
                
                application = Krita.instance()
                currentDoc = application.activeDocument()
                activeLayer = currentDoc.activeNode()
                curOpac = activeLayer.opacity()
                newOpac = curOpac - stepOpacity
                
                if newOpac < 0 :
                        newOpac = 0 
                activeLayer.setOpacity(newOpac)
           

                currentDoc.refreshProjection()           #altrimenti non si aggiorna
                
                # #aggiro bug di setopacity
                # parentNode = activeLayer.parentNode()
                # if parentNode is not None:
                        # newLa = activeLayer.clone()
                        # activeLayer.remove()
                        # parentNode.addChildNode(newLa, None)
                        
          
                
                
                application.activeWindow().activeView().showFloatingMessage(f"Decreased layer opacity to { round(newOpac * 100.0 / 255.0)}", QIcon(), timeMessage, 1)
                
                
        def grum(self, currentSelection, currentLayer, application):
                currentDoc = application.activeDocument()

                if currentDoc is not None:
                        #currentSelection = currentDoc.selection()

                        if currentSelection is not None:
                                #currentLayer = currentDoc.activeNode()
                                
                                if currentLayer is not None and currentLayer.type() == 'paintlayer':
                                        blurFilter = application.filter('gaussian blur')
                                        
                                        tmpDoc = Krita.instance().createDocument(currentDoc.width(),
                                                                                                                         currentDoc.height(), 
                                                                                                                         'tmpDoc', 
                                                                                                                         currentDoc.colorModel(), 
                                                                                                                         currentDoc.colorDepth(), 
                                                                                                                         currentDoc.colorProfile(), 
                                                                                                                         currentDoc.resolution())

                                        tmpLayer = tmpDoc.createNode('tmpLayer', 'paintlayer')
                                        tmpLayer.setPixelData(currentLayer.pixelData(currentSelection.x(), 
                                                                                                                                 currentSelection.y(), 
                                                                                                                                 currentSelection.width(),
                                                                                                                                 currentSelection.height()), 
                                                                                  currentSelection.x(), 
                                                                                  currentSelection.y(), 
                                                                                  currentSelection.width(), 
                                                                                  currentSelection.height())
                                                                                

                                        tmpFilterMask = tmpDoc.createFilterMask('tmpFilterMask', blurFilter, currentSelection)
                                        tmpLayer.addChildNode(tmpFilterMask, None)
                                        
                                        tmpDoc.rootNode().addChildNode(tmpLayer, None)

                                        currentLayer.setPixelData(tmpLayer.projectionPixelData(currentSelection.x(), 
                                                                                                                                currentSelection.y(), 
                                                                                                                                                currentSelection.width(), 
                                                                                                                                                currentSelection.height()), 
                                                                                        currentSelection.x(), 
                                                                                        currentSelection.y(), 
                                                                                        currentSelection.width(), 
                                                                                        currentSelection.height())
                                                
                                        currentDoc.refreshProjection()  
                                        
                                        tmpDoc.close()
                                        
        def layerMergeAndCreate(self):
                application = Krita.instance()
                currentDoc = application.activeDocument()
                activeLayer = currentDoc.activeNode()
                
                # application.action('selectopaque').trigger()
                # currentDoc.waitForDone () # action needs to finish before continuing
                # selectionStroke = currentDoc.selection()
                
                parentNode = activeLayer.parentNode()
                if parentNode is not None:
                        oldOpacity = activeLayer.opacity()
                        activeLayer.mergeDown()
                        root = currentDoc.rootNode()
                        newLa = currentDoc.createNode("Wet_area", "paintLayer")
                        newLa.setOpacity(oldOpacity)
                        
                        backgroundLayer = parentNode.childNodes()[0]
                        
                        
                        parentNode.addChildNode(newLa, None)
                        
                        # # # test blur
                        # self.grum(selectionStroke, backgroundLayer, application)
                        
                        # deseleziona
                        
                        # currentDoc.setSelection(None)
                        # currentDoc.setActiveNode(backgroundLayer)
                        # blurFilter = application.filter('gaussian blur')
                        # currentSelection = currentDoc.selection()
                        
                        # x = selection.x()
                        # y = selection.y()
                        # wt = selection.width()
                        # ht = selection.height()
                        
                        # rectSelection = Selection()
                        # rectSelection.select(x, y, wt , ht, 255)
                        
                        # currentDoc.setSelection(rectSelection)
                        
                        # # newUnblurred = currentDoc.createNode("unblurred", "paintLayer")
                        # # parentNode.addChildNode(newUnblurred, None)
                        
                        # currentDoc.setActiveNode(backgroundLayer)
                        # selection.cut(backgroundLayer)
                        
                        # Krita.instance().action('edit_paste').trigger()
                        # currentDoc.waitForDone () # action needs to finish before continuing
                        
                        # newUnblurred = currentDoc.activeNode()
                        # # currentDoc.setSelection(None)
                        
                        # currentDoc.setActiveNode(newUnblurred)
                        # selection.paste(newUnblurred, 0,0)
                        
                        # print (f"selection: {selection.x()}, {selection.y()}, wt = {selection.width()}, ht = {selection.height()}")
                        # # selection.copy(backgroundLayer)
                        # blurFilter.apply(backgroundLayer, x, y, wt, ht)
                        # # print(f"blur filter: {blurFilter}")
                        
                        # newBlurred = currentDoc.createNode("unblurred", "paintLayer")
                        
                        # selection.copy(backgroundLayer)
                        # selection.paste(newUnblurred, selection.x(), selection.y())
                        
                        
                        # #application.action('add_new_filter_mask').trigger()
                        
                        # # print( blurFilter.configuration().properties() )
                        # currentDoc.waitForDone () # action needs to finish before continuing
                        # currentDoc.refreshProjection()  # update UI
                        
                        
                else:
                        newLa = currentDoc.createNode("Wet_area", "paintLayer")
                        newLa.setOpacity(140)
                        root.addChildNode(newLa, None)
                        
                #test blur        
                
                application.activeWindow().activeView().showFloatingMessage("Dry paper", QIcon(), timeMessage, 1)
                        
                
        
                
        def viewSingleWindow(self):
                app = Krita.instance()
                
                
                print(f"windows = {app.windows()}")
                
                # for wi in app.windows():
                        # print(f"wi views = {wi.views()}")
                        # print (f"wi subwindows = {wi.qwindow().findChild(QMdiArea).subWindowList()}")
                        
                        # subwins = wi.qwindow().findChild(QMdiArea).subWindowList()
                        # firstsubwin = subwins[1]
                        # firstsubwin.showMinimized()
                        
                
                # mdi_area = firstWindow.findChild(QMdiArea)
                # for sub_win in mdi_area.subWindowList():
                        # print(sub_win)

                
                #currentDoc = app.activeDocument()
                curWin = app.activeWindow()
                wins = app.windows()
                
                
                # dockers = app.dockers()
                
                # for d in dockers:
                        # print (f"docker  {d.objectName()}")


                # documents = app.documents()
                
                # for d in documents:
                        # print (f"document {d.fileName()}")
                
                # views = app.views()
                
                # for v in views:
                        
                        # print(f"view: {v.document().fileName()}. win: {v.window().activeView().document().fileName()}")
                
                # #minimizzo tutte le finestre tranne quella attiva
                for win in wins:
                                
                                print (f"win: {win.activeView().document().fileName()}")
                                # print("flename2")
                                # # print (curWin.activeView().document().fileName())
                                
                                # # if win.activeView().document() is   curWin.activeView().document():
                                        # # print ("trovata")
                                q_win = win.qwindow()
                                mdi_area = q_win.findChild(QMdiArea)
                                for sub_win in mdi_area.subWindowList():
                                        sub_win.showMinimized()

                                #curWin.qwindow().showNormal()
        
        def createActions(self, window):
        


                action = window.createAction("LastColor", "LastColor")
                action.triggered.connect(self.switchToLastColor)
                
                # action2 = window.createAction("MixColorBig", "MixColorBig")
                # action2.triggered.connect(self.mixBig)
                
                # action2 = window.createAction("MixColorSmall", "MixColorSmall")
                # action2.triggered.connect(self.mixSmall)


                action2 = window.createAction("MixColor", "MixColor")
                action2.triggered.connect(self.mixFgColorWithBgColor)
                
                action2 = window.createAction("PickColor", "PickColor")
                action2.triggered.connect(self.pick)

                action2 = window.createAction("LayerMergeDownAndNew", "LayerMergeDownAndNew")
                action2.triggered.connect(self.layerMergeAndCreate)

                action2 = window.createAction("ViewSingleWindow", "ViewSingleWindow")
                action2.triggered.connect(self.viewSingleWindow)

                action2 = window.createAction("IncreaseLayerOpacity", "IncreaseLayerOpacity")
                action2.triggered.connect(self.increaseLayerOpacity)

                action2 = window.createAction("DecreaseLayerOpacity", "DecreaseLayerOpacity")
                action2.triggered.connect(self.decreaseLayerOpacity)


                action2 = window.createAction("IncreaseMixing", "IncreaseMixing")
                action2.triggered.connect(self.increaseMixingOrig)

                action2 = window.createAction("DecreaseMixing", "DecreaseMixing")
                action2.triggered.connect(self.decreaseMixingOrig)

# And add the extension to Krita's list of extensions:
Krita.instance().addExtension(MyExtension(Krita.instance()))

