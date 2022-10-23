#TODO on mouse leave on top, focus the single window that's not always on top


from krita import *

from krita import (
                Krita,)

from pathlib import Path
    
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
                QKeyEvent,
                QCursor)

from PyQt5.QtWidgets import (
                QWidget,
                QMdiArea,
                QTextEdit,
                QAbstractScrollArea,
                QAction, QMenu
                
                )


# from PyQt5 import QtWidgets, QtCore, QtGui, uic
import os
import os.path
import time
import datetime
import xml
import math
import json

timeMessage = 300
stepOpacity = 20

g_mixing_step = 0.05

g_step_mixing_target_distance = 2.5


g_auto_opacity_max_distance = 40

from PyQt5.QtCore import Qt, QModelIndex, QItemSelectionModel
from PyQt5.QtWidgets import QTreeView


def get_layer_model():
    app = Krita.instance()
    kis_layer_box = next((d for d in app.dockers() if d.objectName() == 'KisLayerBox'), None)
    view = kis_layer_box.findChild(QTreeView, 'listLayers')
    return view.model(), view.selectionModel()


def getColorUnderCursorExceptCurrentLayer():
    application = Krita.instance()
    document = application.activeDocument()
    
    if document:
            center = QPointF(0.5 * document.width(), 0.5 * document.height())
            p = get_cursor_in_document_coords()
            
            doc_pos = p + center
            #print(f'cursor at: x={doc_pos.x()}, y={doc_pos.y()}')
            
            
            parentNode = document.activeNode().parentNode()
            
            
            if parentNode is not None:
            
                    brothers = parentNode.childNodes()
                    colors = []
                    
                    #costruisco colors
                    for curLayer in brothers:
                            if curLayer.uniqueId() == document.activeNode().uniqueId():
                                #print ("salto cur layer")
                                continue
                                
                                
                            pixelBytes = curLayer.pixelData(doc_pos.x(), doc_pos.y(), 1, 1)
                            
                            imageData = QImage(pixelBytes, 1, 1, QImage.Format_RGBA8888)
                            pixelC = imageData.pixelColor(0,0)
                            
                            # devo correggere l'alpha del pixel con l'alpha del layer. ma non lo correggo se il layer è quello attuale, che è trasparente. così la pennellata successiva si vede uguale
                            # if curLayer.uniqueId() == document.activeNode().uniqueId():
                                # correzMul = 1.0
                            # else:
                            layerOpac = curLayer.opacity() # tra  0 e 255
                            correzMul = float(layerOpac) /  255.0
                        

                            #print(f"color under cursor =  r:{self.pixelC.red()}, g:{self.pixelC.green()}, b:{self.pixelC.blue()} ,a:{self.pixelC.alpha() }, a corretto = {self.pixelC.alpha() * correzMul}")
                            
                            colors.append(  rgb(pixelC.red(),  pixelC.green(),  pixelC.blue(),  pixelC.alpha() * correzMul ))
                    
                    #creo il colore composito dei layer. questo è il bgcolor                                                
                    bgColor = calcolaCompositeColor(colors)
                    #print(f"color under cursor  = {bgColor.toString()}")
                    return bgColor
            else:
                return None
    else:
        return None


def node_to_index(node, model):
    path = list()
    while node and (node.index() >= 0):
        path.insert(0, node.index())
        node = node.parentNode()

    index = QModelIndex()    
    for i in path:
        last_row = model.rowCount(index) - 1
        index = model.index(last_row - i, 0, index)
    return index


def index_to_node(index, document):
    if not index.isValid():
        raise RuntimeError('Invalid index')
    model = index.model()
    path = list()
    while index.isValid():
        last_row = model.rowCount(index.parent()) - 1
        path.insert(0, last_row - index.row())
        index = index.parent()
        
    node = None
    children = document.topLevelNodes()
    for i in path:
        node = children[i]
        children = node.childNodes()
    return node

class AutoFocusSetter(QObject):

    # Q_OBJECT
    # ...
# # protected
    # eventFilter = bool(QObject obj, QEvent event)

    def eventFilter(self, obj, event):
        # if event.type() == QEvent.HoverEnter:
            # print(f"hover ")
        if event.type() == QEvent.Enter:
            #if obj.type() == QMdiSubWindow:
            if isinstance(obj, QMdiSubWindow):
                print(f"enter {obj} ")
                
                wi = Krita.instance().activeWindow()
                q_win = wi.qwindow()
                mdi_area = q_win.findChild(QMdiArea)
                mdi_area.setActiveSubWindow(obj)
                #obj.activateWindow()
        if event.type() == QEvent.Leave:
            # logic: if the mouse leaver an always-on-top window, focus the first window that's not always on top. 
            print(f"leave event ")
            if isinstance(obj, QMdiSubWindow):
                print(f"leave {obj} ")
                
                wi = Krita.instance().activeWindow()
                
                
                subwin = obj
                isAlwaysOnTop = True if subwin.windowFlags() & Qt.WindowStaysOnTopHint else False
                
                if isAlwaysOnTop: #if mouse left an always-on-top window:
                    print ("is always-on-top")
                
                    subwins = wi.qwindow().findChild(QMdiArea).subWindowList()
                    for su in subwins:
                        curIsAlw =  False if su.windowFlags() & Qt.WindowStaysOnTopHint else True
                        if curIsAlw:
                            
                            # focus this one
                            q_win = wi.qwindow()
                            mdi_area = q_win.findChild(QMdiArea)
                            mdi_area.setActiveSubWindow(su)
                            
                            break
                            
                            print ("focusing first window that's not always on top")
                
        # if event.type() == QEvent.MouseMove:
            # print (f"mousemove")
            # #col = getColorUnderCursor()
            
        # if event.type() == QEvent.HoverMove:
            # print (f"hover mousemove")
            # #col = getColorUnderCursor()
                
        # if event.type() == QEvent.GraphicsSceneMouseMove:
            # print (f"GraphicsSceneMouseMove")
            # #col = getColorUnderCursor()
        
        # if event.type() == QEvent.GraphicsSceneHoverMove:
            # print (f"GraphicsSceneHoverMove")
            # #col = getColorUnderCursor()
        
        if event.type() == QEvent.MouseButtonPress:
            # print("mouse buttonpress")
            
            
            # uncomment this to have dirty brush ===============
            pass
            
            # global g_opacity_decided_for_layer
            # if not g_opacity_decided_for_layer:
                # bgColor = getColorUnderCursorExceptCurrentLayer()
                # application = Krita.instance()
                # win = application.activeWindow()
                # if win is not None:
                    # view = win.activeView()
                    # if bgColor  is not None and view is not None:
                        # # print (f"MouseButtonPress. col = {bgColor.toString()}")
                        
                        # # I need to set current layer opacity so that the distance between fg and color under cursor is small
                        
                        

                                        
                        # # setto il fg color uguale a merged color mischiato con il fg
                        # fg = view.foregroundColor() #tipo ManagedColor, valori da 0 a 1
                        # # print(f"fg  = {fg}")
                        
                        # fg2 = rgbOfManagedColor(fg) # valori da 0 a 255
                        # # fg2.print("MouseButtonPress fg2 = ")
                        
                        
                        
                        # document = application.activeDocument()
                        # if document:
                        
                            # curLayer = document.activeNode()
                            
                            
                            # comp = fg.components() 
                            # # print(f"fg color = {comp}")

                            # dist = fg2.distance(bgColor)
                            # # print(f"distance = {dist}")

                            
        
        
                            # curDist = None
                            # picked50 = False
                            
                            
                            # global g_auto_opacity_max_distance
                            # max_distance = g_auto_opacity_max_distance
                            
                            # # calcola curFg
                            # if dist  <= g_auto_opacity_max_distance:
                                # #i colori sono molto vicini. fai 50%
                                # quickMessage("colors very close. leaving same")
                                # # curMul = 0.5
                                # curFg = fg2
                                # # curFg = rgb( fg2.r * curMul + bgColor.r * (1.0 - curMul),
                                                                # # fg2.g * curMul + bgColor.g * (1.0 - curMul),
                                                                # # fg2.b * curMul + bgColor.b * (1.0 - curMul),
                                                                # # 255)
                                # # curDist = dist
                                # # picked50 = True
                            # else:  # i colori sono lontani. avvicina poco a poco finché la distanza del curFg dall'origFg non diventa > target
                            
                                # stepMul = 0.001
                                
                                
                                # curMul = 1.0
                                
                                # while True:
                                    
                                    # curFg = rgb( fg2.r * curMul + bgColor.r * (1.0 - curMul),
                                                                # fg2.g * curMul + bgColor.g * (1.0 - curMul),
                                                                # fg2.b * curMul + bgColor.b * (1.0 - curMul),
                                                                # 255)
                                                                
                                    # curDist = curFg.distance(bgColor)
                                    
                                    # #print(f"iterando. mul  = {curMul}, dist  tra {curFg.toString()} e {fg2.toString()} = {curDist}. ")
                                    
                                    # if curDist <= g_auto_opacity_max_distance:  
                                        # break
                                        
                                    # curMul -= stepMul   
                                        
                                # picked50 = False
                                
                                
                                # quickMessage(f"fg color changed to {curFg.toString()}")
                                # print (f"fg color changed to {curFg.toString()}")
                                
                            # #canv = howMuchCanvas # pick half color from canvas
                            
                            # comp[0] = curFg.r / 255.0
                            # comp[1] = curFg.g / 255.0
                            # comp[2] = curFg.b / 255.0
                            
                            
                            # # fgMul = 1.0 - canv
                            # # comp[0] = comp[0] * fgMul + (bgColor.r / 255.0)  * canv
                            # # comp[1] = comp[1] * fgMul + (bgColor.g / 255.0)  * canv
                            # # comp[2] = comp[2] * fgMul + (bgColor.b  / 255.0)  * canv
                            
                        
                      
                            # fg.setComponents(comp)
                            
                            # view.setForeGroundColor(fg)
                            
                            
                            # # setto anche il virtual fg color al result del mix
                            # self.last_color_picked = rgb( int  (comp[0] * 255.0), int  (comp[1] * 255.0), int  (comp[2] * 255.0), 1)
                            
                            
                            # g_opacity_decided_for_layer = True
                            
                            
                            # # messaggio
                            # # if picked50:
                                # # view.showFloatingMessage(f"Picked 50% because distance was small ({round(curDist)})", QIcon(), timeMessage, 1)
                            # # else:
                                # # view.showFloatingMessage(f"Picked a bit of color from canvas. Distance: {round(curDist)}", QIcon(), timeMessage, 1)
                            
                            
                            
                            # # old logic that sets layer opacity
                            # # curDist = None
                            # # picked50 = False
                            
                            # # global g_auto_opacity_max_distance
                            # # max_distance = g_auto_opacity_max_distance
                            
                            # # # calcola curFg
                            # # if dist  <= max_distance:
                                # # #i colori sono molto vicini. 
                                # # curLayer.setOpacity(25 * 255.0 / 100.0)
                                # # document.refreshProjection()           #altrimenti non si aggiorna    
                                
                            # # else:  # i colori sono lontani. diminuisci l'opacita del fg finche' diventano vicini
                            
                                # # stepOp = 0.001
                                
                                
                                # # curOp01 = 1.0
                                
                                # # while True:
                                    
                                    # # quantoBg = 1.0 - curOp01
                                    # # curFg = rgb( fg2.r * curOp01 + bgColor.r * quantoBg,
                                                                # # fg2.g * curOp01 + bgColor.g * quantoBg,
                                                                # # fg2.b * curOp01 + bgColor.b * quantoBg,
                                                                # # 255)
                                                                
                                    # # curDist = curFg.distance(bgColor)
                                    
                                    # # # print(f"iterando. mul  = {curOp01}, dist  = {curDist}. ")
                                    
                                    # # if curDist <= max_distance:  
                                        # # break
                                        
                                    # # if curOp01 <= 0.0:
                                        # # break
                                        
                                    # # curOp01  -= stepOp   
                                

                                # # # here, I am sure distance is small
                                # # curLayer.setOpacity(curOp01 * 255)
                                
                                # # document.refreshProjection()           #altrimenti non si aggiorna    
                                # # quickMessage(f"auto-opacity {round(curOp01 * 255)}")
                                
                            # # g_opacity_decided_for_layer = True
                        
                    
                
            #col = getColorUnderCursor()
        
        return False
        #return QObject.eventFilter(obj, event)
        
        # if event.type() == QEvent.KeyPress:
            # print(f"keypress")
            # keyEvent = QKeyEvent(event)
            # qDebug("Ate key press %d", keyEvent.key())
            # return True
        # else:
            # # standard event processing
            # return QObject.eventFilter(obj, event)

#print(Krita.instance().filters())

class Dict2Class(object):
      
    def __init__(self, my_dict):
          
        for key in my_dict:
            setattr(self, key, my_dict[key])


def messageBox(txt):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setText(txt)
    # msg.setInformativeText()
    msg.setWindowTitle("ColorPlus")
    #msg.setDetailedText("The details are as follows:")
    msg.setStandardButtons(QMessageBox.Ok )
    msg.exec_()
    

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
            return f" r:{round(self.r)}, g:{round(self.g)}, b:{round(self.b)} ,a:{self.a}"

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
                        #col.print("cur color")
                        if mergedColor is None:
                                mergedColor = col
                                #mergedColor.print("setto merged color")
                        else:
                                a = float(col.a) / 255.0
                                #print (f"a = {a}")
                                invA = (1.0 - a) 
                                #print (f"invA = {invA}")
                                mergedColor = rgb( mergedColor.r * invA + col.r * a,
                                                                                mergedColor.g * invA + col.g * a,
                                                                                mergedColor.b* invA + col.b * a,
                                                                                255)
                                #mergedColor.print("merged color")
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
    
    
class Window:
    x = 10
    y = 20
    wt = 30
    ht = 40
    name = "file.kra"
    isMaximized = False
    isMinimized = False
    isAlwaysOnTop = False
    fullPath = ""
    
class PluginState:
    windows = []
    
    
global g_opacity_decided_for_layer
g_opacity_decided_for_layer = False
    
class MyExtension(Extension):

        def __init__(self, parent):
                # This is initialising the parent, always important when subclassing.
                super().__init__(parent)
                
                self.inited = False
                
                self.counter = 0
                
                
                strHowMuch = Krita.instance().readSetting("colorPlus", "g_how_much_canvas_to_pick","0.45")
                self.g_how_much_canvas_to_pick = float(strHowMuch)
                
                global g_auto_opacity_max_distance
                g_auto_opacity_max_distance = int(Krita.instance().readSetting("colorPlus", "g_auto_opacity_max_distance","40"))
                
                # dev values , only read when timer is active
                self.last_color_picked = None # di tipo rgb
                self.g_how_much_canvas_to_pick_on_timer = 0.8
                
                self.g_auto_focus = Krita.instance().readSetting("colorPlus", "g_auto_focus", "true")
                
                
                self.mix_radius = 2 # pixel
                
                self.temp_switched_to_100_previous_opac = None
                
                self.temp_switched_to_25_previous_opac = None
                
                self.mixing_target_distance = 20.0
                
                self.correct_color_for_transparency = True
                
                
                #creo il timer per il mixing
                # self.timer = QTimer()
                # self.timer.timeout.connect(self.mixOnTimer)
                # self.timer.start(40)
                
                
                #creo il timer per il colore
                # self.timer2 = QTimer()
                # self.timer2.timeout.connect(self.updateColorUnderMouse)
                # self.timer2.start(40)
                
                # self.timer = QTimer()
                # self.timer.timeout.connect(self.saveWindowPositions)
                # self.timer.start(2000)
                
                
                # self.timer = QTimer()
                # self.timer.timeout.connect(self.mergeOnTimer)
                # self.timer.start(4000)
                
            
                
                home = str(Path.home())
                
                home= os.getenv('APPDATA')
                
                self.plugin_state_dir = f"{home}/plugin_krita_color_plus"
                
                self.filePathWindowState = f"{self.plugin_state_dir}/windowPositions.txt"
                
                self.windows_with_autofocus = []
                self.ef_autofocus  = AutoFocusSetter(self)
                
                if not os.path.exists(self.plugin_state_dir):
                
                    os.mkdir(self.plugin_state_dir)
                    
                
                Krita.instance().notifier().windowCreated.connect(self.onWindowCreated)
                # Krita.instance().notifier().viewCreated.connect(self.onViewOpenedEvent)
                
                
                self.timer = QTimer()
                self.timer.timeout.connect(self.updateAutoFocus)
                self.timer.start(1000)
                
                
                print(f"init ok. home = {home}")


        def updateAutoFocus(self):
                
        
                wi = Krita.instance().activeWindow()
                if wi is not None:
                    subwins = wi.qwindow().findChild(QMdiArea).subWindowList()
                    
                    if self.g_auto_focus ==  "true":
                        for su in subwins:
                                if su not in self.windows_with_autofocus:
                                    print(f"installing autofocus for window {su}")
                                    su.installEventFilter(self.ef_autofocus)
                                    self.windows_with_autofocus.append(su)
                    else:
                        for su in subwins:
                            if su  in self.windows_with_autofocus:
                                print(f"uninstalling autofocus for window {su}")
                                su.removeEventFilter(self.ef_autofocus)
                                self.windows_with_autofocus.remove(su)
                        
                        
                
        def onViewOpenedEvent(openedView):
            
            print(f"view opened {openedView}");
            openedView.updateAutoFocus()

        def onWindowCreated(self): #called by framework
                print("on window created  ")
                

                self.currentColor = [255,255,255,0]
                self.previousColor = [255,255,20,0]
                # self.inited = False
                                
                app = Krita.instance()
                history_docker = next((d for d in app.dockers() if d.objectName() == 'History'), None)
                kis_undo_view = next((v for v in history_docker.findChildren(QListView) if v.metaObject().className() == 'KisUndoView'), None)
                s_model = kis_undo_view.selectionModel()
                s_model.currentChanged.connect(self._on_history_was_made)
                
                self.inited = True;
                print ("swap: initialized")
                

                print("on window created : ok")
                
        def setup(self): #called by framework
            print("setup called")

        def saveWindowPositions(self):
            wi = Krita.instance().activeWindow()
            subwins = wi.qwindow().findChild(QMdiArea).subWindowList()
            
            
            fullPaths = []
            for wi in Krita.instance().windows():
                print(f"wi = {wi}  title = {wi.qwindow().windowTitle()}")
                for vi in wi.views():
                    print(f"view filename {vi.document().fileName()}")
                    fullPaths.append(vi.document().fileName())
            
            
            
            windows = []
            for su in subwins:
                tit = su.windowTitle().replace(" *", "")
                
                path = [ fp for fp in fullPaths if fp.endswith(tit) ] [0]
                print(f"window {tit}, position {su.pos()}")
                newWin = Window()
                newWin.x = su.pos().x()
                newWin.y = su.pos().y()
                newWin.wt = su.size().width()
                newWin.ht = su.size().height()
                newWin.fullPath = path
                newWin.title = tit
                newWin.isMaximized = True if su.windowState() & Qt.WindowMaximized else False
                newWin.isMinimized = True if su.windowState() & Qt.WindowMinimized else False
                newWin.isAlwaysOnTop = True if su.windowFlags() & Qt.WindowStaysOnTopHint else False
                windows.append(newWin)
                
            js = json.dumps([ w.__dict__ for w in windows] )
            
            
            
            with open(self.filePathWindowState, 'w+') as f:
                f.write(js)
            print(f"dump json = {js}")

            return js
            
        # def restoreWindowPositionsOld(self): #relies on sessions to open the files
        
            # #restore last saved window state
            # f = open(self.filePathWindowState)
            # windows = json.load(f)
            # print(f"roba letta: {windows}")
            
            

            # f.close()
            
            # wi = Krita.instance().activeWindow()
            # subwins = wi.qwindow().findChild(QMdiArea).subWindowList()
            
            
            # for w in windows:
                # w2 = Dict2Class(w)
                # print(f"titolo = {w2.title}, x = {w2.x}")
                
                # for su in subwins:
                    # tit = su.windowTitle().replace(" *", "")
                    # if tit == w2.title:
                        # # devo settare questa finestra come era
                        # if w2.isMaximized: # se era massimizzata                    
                            # su.setWindowState(su.windowState() | Qt.WindowMaximized)  # la massimizzo
                        # else:
                            # su.setWindowState(su.windowState() & ~Qt.WindowMaximized)  # tolgo lo stato maximixed
                            
                        # if w2.isAlwaysOnTop : # se era always on top
                            # su.setWindowFlags(su.windowFlags() | Qt.WindowStaysOnTopHint)  # la metto on top
                        # else:
                            # su.setWindowFlags(su.windowFlags() & ~Qt.WindowStaysOnTopHint)  # tolgo lo stato on top
                        
                        
                        # su.move( w2.x, w2.y)
                        # su.resize(w2.wt, w2.ht)
        
        def restoreWindowPositions(self):
        
            #restore last saved window state
            try:
                f = open(self.filePathWindowState)
                windows = json.load(f)
                print(f"roba letta: {windows}")
                
                f.close()
                
                wi = Krita.instance().activeWindow()
                subwins = wi.qwindow().findChild(QMdiArea).subWindowList()
                
                
                # sort the windows so that the always on top is restored first, otherwise if it's last you don't see the correct layers in the layer list, after I do setActiveSubWindow below.
                def sortFun(wi):
                    w2 = Dict2Class(wi)
                    if w2.isAlwaysOnTop:
                        return -1
                    else:
                        return 1
                        
                        
                windows.sort(key = sortFun)
                print(f"sorted: {windows}")    
                
                
                
                
                    
                # open all files in the correct order
                for w in windows:
                    w2 = Dict2Class(w)
                    print(f"titolo = {w2.title}, x = {w2.x}. opening document: {w2.fullPath}")
                
                    alreadyOpen = False
                    for su in subwins:
                            tit = su.windowTitle().replace(" *", "")
                            if tit == w2.title:
                                alreadyOpen = True
                                
                    if not alreadyOpen:
                        doc = Krita.instance().openDocument(w2.fullPath)
                        Krita.instance().activeWindow().addView(doc)


                        
                # all needed files are open. Set attributes, like maximized and always on top
                    
                
                # subwins have changed. reload them
                subwins = wi.qwindow().findChild(QMdiArea).subWindowList()
                
                for w in windows:
                    w2 = Dict2Class(w)
                    print(f"titolo = {w2.title}, x = {w2.x}")
                    
                    for su in subwins:
                        tit = su.windowTitle().replace(" *", "")
                        if tit == w2.title:
                            # devo settare questa finestra come era
                            if w2.isMaximized: # se era massimizzata                    
                                su.setWindowState(su.windowState() | Qt.WindowMaximized)  # la massimizzo
                            else:
                                su.setWindowState(su.windowState() & ~Qt.WindowMaximized)  # tolgo lo stato maximixed
                                
                                
                            if w2.isMinimized: 
                                su.setWindowState(su.windowState() | Qt.WindowMinimized)  
                            else:
                                su.setWindowState(su.windowState() & ~Qt.WindowMinimized)  
                                
                            if w2.isAlwaysOnTop : # se era always on top
                                su.setWindowFlags(su.windowFlags() | Qt.WindowStaysOnTopHint)  # la metto on top
                            else:
                                su.setWindowFlags(su.windowFlags() & ~Qt.WindowStaysOnTopHint)  # tolgo lo stato on top
                            
                            
                            su.move( w2.x, w2.y)
                            su.resize(w2.wt, w2.ht)
                            
                            
                #I activate any window that is not on top and not minimized. this still leaves the layers of the wrong window in the layer list, therefore I sorted them previously
                for su in subwins:
                    flags = su.windowFlags()
                    
                    stayOnTop = False
                    if su.windowFlags() & Qt.WindowStaysOnTopHint:
                        stayOnTop = True
                    else:
                        stayOnTop = False
                    

                    isMinimized = False
                    if su.windowState() & Qt.WindowMinimized:
                        isMinimized = True
                    else:
                        isMinimized = False


                    if not isMinimized and not stayOnTop:
                        
                        q_win = wi.qwindow()
                        mdi_area = q_win.findChild(QMdiArea)
                        mdi_area.setActiveSubWindow(su)
                        su.activateWindow() # test


                    
                # subwins = window.qwindow().findChild(QMdiArea).subWindowList()
                # for su in subwins:
          



                # application = Krita.instance()
                # currentDoc = application.activeDocument()
                # currentDoc.refreshProjection()           #altrimenti non si aggiorna

            except FileNotFoundError:
                messageBox(f"The file where the window state is stored was not found: \n\n{self.filePathWindowState } \n\nYou need to save the windows state first. Then the file will be created.")
                
        # def setup(self):
                
                
                
                
                # self.currentColor = [0,0,0,0]
                # self.previousColor = [0,0,0,0]
                # self.inited = False
                
                # print("LastColor setup ok")
                
                
                
        
        def switchToLastColor(self):
                try:
                        # doc  = Krita.instance().activeWindow().activeView().document()
                        # print(doc)
                        
                        # sel  = doc.selection()
                        # print(sel )
                        
                        # x = sel.x()
                        # print(x)
        
                        pos = QtGui.QCursor.pos()
                        # print("cursor absolute = ", pos)

                        win = Krita.instance().activeWindow().qwindow().mapFromGlobal(pos);

                        # print("cursor mapped = ", win)
        
                        acView = Krita.instance().activeWindow().activeView()
                        if not self.inited:
                                quickMessage ("LastColor not yet initialized")
                                
                                # print ("swap: initializing...")
                                
                                
                                
                                
                                
                                
                                
                                
                                
                                # app = Krita.instance()
                                # history_docker = next((d for d in app.dockers() if d.objectName() == 'History'), None)
                                # kis_undo_view = next((v for v in history_docker.findChildren(QListView) if v.metaObject().className() == 'KisUndoView'), None)
                                # s_model = kis_undo_view.selectionModel()
                                # s_model.currentChanged.connect(self._on_history_was_made)
                                
                                # self.inited = True;
                                # print ("swap: initialized")
                                
                                # acView.showFloatingMessage("Last color initialized. Press again to use.", QIcon(), timeMessage * 2, 1)
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
                                
                                


        def toggle_100_opac(self):
        
            application = Krita.instance()
            currentDoc = application.activeDocument()
            if currentDoc is not None:
                activeLayer = currentDoc.activeNode()
                curOpac = activeLayer.opacity()
                
                if self.temp_switched_to_100_previous_opac is None:
                    newLa = self.dryPaper(False)
                    
                    activeLayer = newLa
                    # currentDoc = application.activeDocument()
                    # currentDoc.waitForDone()
                    # activeLayer = currentDoc.activeNode()
                    
                    if self.temp_switched_to_25_previous_opac is not None:
                        self.temp_switched_to_100_previous_opac = self.temp_switched_to_25_previous_opac
                        self.temp_switched_to_25_previous_opac = None
                    else:
                        self.temp_switched_to_100_previous_opac = activeLayer.opacity()
                        
                    
                    activeLayer.setOpacity(255)
                    
                    
                    # the brush opacity becomes equal to the layer opacityfg = view.foregroundColor()
                    
                    # view  = Krita.instance().activeWindow().activeView()
                    
                    # newPaintingOp = self.temp_switched_to_100_previous_opac / 255.0
                    # print(f"setting new painting op = {newPaintingOp}")
                    # view.setPaintingOpacity(newPaintingOp)
                    
                    
                    
                    quickMessage(f"Temporarily set 100% opacity. Press again to restore.")
                else:
                    newLa = self.dryPaper(False)
                    
                    # currentDoc = application.activeDocument()
                    activeLayer = newLa #currentDoc.activeNode()
                    activeLayer.setOpacity(self.temp_switched_to_100_previous_opac)
                    
                    
                    quickMessage(f"Restored {round (self.temp_switched_to_100_previous_opac * 100.0 / 255.0)}  opacity")
                    
                    # view  = Krita.instance().activeWindow().activeView()
                    # view.setPaintingOpacity(1.0)
                    
                    self.temp_switched_to_100_previous_opac = None
        
        def toggle_25_opac(self):
        
            application = Krita.instance()
            currentDoc = application.activeDocument()
            if currentDoc is not None:
                activeLayer = currentDoc.activeNode()
                curOpac = activeLayer.opacity()
                
                if self.temp_switched_to_25_previous_opac is None:
                    activeLayer = self.dryPaper(False)
                    
                    if self.temp_switched_to_100_previous_opac is not None:
                        self.temp_switched_to_25_previous_opac = self.temp_switched_to_100_previous_opac
                        self.temp_switched_to_100_previous_opac = None
                    else:
                        self.temp_switched_to_25_previous_opac = activeLayer.opacity()
                    
                    activeLayer.setOpacity(25.0 * 255.0 / 100.0)
                    
                    
                    quickMessage(f"Temporarily set 25% opacity. Press again to restore.")
                else:
                    activeLayer = self.dryPaper(False)
                    activeLayer.setOpacity(self.temp_switched_to_25_previous_opac)
                    
                    
                    quickMessage(f"Restored {round (self.temp_switched_to_25_previous_opac * 100.0 / 255.0)}  opacity")
                    
                    self.temp_switched_to_25_previous_opac = None
                
                
            
        def _on_history_was_made(self):
                
                # col = getColorUnderCursor()
                # if col is not None:
                    # print (f"user painted. counter = {self.counter}. col = {col.toString()}")
                
                                

                
                self.counter +=  1
                
                try:
                        
                        acView = Krita.instance().activeWindow().activeView()
                        if acView is not None: 
                                col = acView.foregroundColor()
                                if col is not None:   
                                        comp = col.components()
                                        if listEqual( comp, self.currentColor ):   # user did not change color
                                                 pass
                                        else:  # user changed color
                                                # print("color changed")
                                                self.previousColor = list.copy(self.currentColor) 
                                                self.currentColor = list.copy(comp)
                                

                                
                except Exception as e:
                                print(f"found error: {e}")
                                #self.timer_hm.stop()
                                raise

        # def mixOldSingleLayer(self):
                # app = Krita.instance()
                # win = app.activeWindow()
                # if win is not None:
                        # view = win.activeView()
                        # if view is not None:
                                # document = view.document()
                                # if document:
                                        # center = QPointF(0.5 * document.width(), 0.5 * document.height())
                                        # p = get_cursor_in_document_coords()
                                        # if p is not None:
                                                # doc_pos = p + center
                                                # print(f'cursor at: x={doc_pos.x()}, y={doc_pos.y()}')
                                                
                                                # self.pixelBytes = document.activeNode().pixelData(doc_pos.x(), doc_pos.y(), 1, 1)
                                                
                                                # self.imageData = QImage(self.pixelBytes, 1, 1, QImage.Format_RGBA8888)
                                                # self.pixelC = self.imageData.pixelColor(0,0)
                                                # print(f"color under cursor = {self.pixelC.red()}, {self.pixelC.green()}, {self.pixelC.blue()}")
                                                
                                                # fg = view.foregroundColor()
                                                # comp = fg.components() 
                                                # print(f"fg color = {comp}")
                 
                 
                                                # canv = 0.5 #I pick half color from canvas
                                                # fgMul = 1.0 - canv
                                                # comp[0] = comp[0] * fgMul + (self.pixelC.red() / 255.0)  * canv
                                                # comp[1] = comp[1] * fgMul + (self.pixelC.green() / 255.0)  * canv
                                                # comp[2] = comp[2] * fgMul + (self.pixelC.blue()  / 255.0)  * canv
                                          
                                                # fg.setComponents(comp)
                                                
                                                # view.setForeGroundColor(fg)

                

        def mixFgColorWithBgColor_maxDistanceLogic(self):
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
                                                fg = view.foregroundColor() #tipo ManagedColor, valori da 0 a 1
                                                print(f"fg  = {fg}")
                                                
                                                fg2 = rgbOfManagedColor(fg) # valori da 0 a 255
                                                fg2.print("fg2")
                                                
                                                comp = fg.components() 
                                                print(f"fg color = {comp}")
                 
                                                dist = fg2.distance(bgColor)
                                                print(f"distance = {dist}")
                 
                                                
                                                curDist = None
                                                picked50 = False
                                                
                                                # calcola curFg
                                                if dist  <= self.mixing_target_distance:
                                                    #i colori sono molto vicini. fai 50%
                                                    curMul = 0.5
                                                    curFg = rgb( fg2.r * curMul + bgColor.r * (1.0 - curMul),
                                                                                    fg2.g * curMul + bgColor.g * (1.0 - curMul),
                                                                                    fg2.b * curMul + bgColor.b * (1.0 - curMul),
                                                                                    255)
                                                    curDist = dist
                                                    picked50 = True
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
                                                            
                                                    picked50 = False
                                                    
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
                                                if picked50:
                                                    view.showFloatingMessage(f"Picked 50% because distance was small ({round(curDist)})", QIcon(), timeMessage, 1)
                                                else:
                                                    view.showFloatingMessage(f"Picked a bit of color from canvas. Distance: {round(curDist)}", QIcon(), timeMessage, 1)
                                                
        def mixFgColorWithBgColor_normalLogic(self):
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
                                                
                                                # I build colors[]
                                                for curLayer in brothers:
                                                    # If this is the current layer and it is transparent, I skip this layer, because I only want to pick from layers below it.  Why? Because you typically use the mix shortcut when the stroke you just made is wrong, and it needs to be more similar to the background layer. But then, you want to be able to click on the stroke you just did and pick the color BELOW it. 
                                                    if curLayer.uniqueId() != document.activeNode().uniqueId() or curLayer.opacity() == 255: 
                                                    
                                                        self.pixelBytes = curLayer.pixelData(doc_pos.x(), doc_pos.y(), 1, 1)
                                                        
                                                        self.imageData = QImage(self.pixelBytes, 1, 1, QImage.Format_RGBA8888)
                                                        self.pixelC = self.imageData.pixelColor(0,0)
                                                        
                                                        # if this is the current layer and it is trasparent, this means you are mixing from a stroke you just did. Then consider it not transparent. So the next stroke will be almost identical to the previous stroke
                                                        if curLayer.uniqueId() == document.activeNode().uniqueId():
                                                            correzMul = 1.0
                                                        else:
                                                            layerOpac = curLayer.opacity() # between 0 and 255
                                                            correzMul = float(layerOpac) /  255.0
                                                    

                                                        print(f"color under cursor =  r:{self.pixelC.red()}, g:{self.pixelC.green()}, b:{self.pixelC.blue()} ,a:{self.pixelC.alpha() }, a corretto = {self.pixelC.alpha() * correzMul}")
                                                        
                                                        colors.append(  rgb(self.pixelC.red(),  self.pixelC.green(),  self.pixelC.blue(),  self.pixelC.alpha() * correzMul ))
                                                
                                                
                                                if len(colors) == 0: # there was only the fg layer
                                                    quickMessage(f"Cannot mix: could not find background layers to pick from. ")
                                                else:
                                                    #creo il colore composito dei layer. questo è il bgcolor                                                
                                                    bgColor = calcolaCompositeColor(colors)
                                                    bgColor.print("bgColor")
                                                                    
                                                    
                                                    fg = view.foregroundColor() 
                                                    comp = fg.components() 
                                                    
                                                    canv = self.g_how_much_canvas_to_pick
                                                    
                                                    
                                                    fgMul = 1.0 - canv
                                                    comp[0] = comp[0] * fgMul + (bgColor.r / 255.0)  * canv
                                                    comp[1] = comp[1] * fgMul + (bgColor.g / 255.0)  * canv
                                                    comp[2] = comp[2] * fgMul + (bgColor.b  / 255.0)  * canv
                                                    
                                                
                                              
                                                    fg.setComponents(comp)
                                                    
                                                    view.setForeGroundColor(fg)
                                                    
                                                    
                                                    # setto anche il virtual fg color al result del mix
                                                    self.last_color_picked = rgb( int  (comp[0] * 255.0), int  (comp[1] * 255.0), int  (comp[2] * 255.0), 1)
                                                    
                                                    
                                                    
                                                    # messaggio
                                                    
                                                    quickMessage(f"Picked {round(canv * 100)}%  color from the canvas.")
                                                    

        def updateColorUnderMouse(self):
            #print("updateColorUnderMouse")
            self.colorUnderMouse = getColorUnderCursor()
            # if col is not None:
                # print(f"update color under mouse: {col.toString()}")
            
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
                                                
                                                positions = [ xy(doc_pos.x(), doc_pos.y())
                                                # ,
                                                                                                # xy(doc_pos.x() + self.mix_radius, doc_pos.y() + self.mix_radius),
                                                                                                # xy(doc_pos.x() - self.mix_radius, doc_pos.y() + self.mix_radius),
                                                                                                # xy(doc_pos.x() + self.mix_radius, doc_pos.y() - self.mix_radius),
                                                                                                # xy(doc_pos.x() - self.mix_radius, doc_pos.y() - self.mix_radius) 
                                                                                                    ]
                                                                        





                                                                        
                                                merged_colors = [] # lista di rgb, uno per posizione
                                                
                                                                                         
                                                
                                                
                                                
                                                for pos in positions:
                                                
                                                        #costruisco colors
                                                        for curLayer in brothers:
                                                        
                                                                self.pixelBytes = curLayer.pixelData(pos.x, pos.y, 1, 1)
                                                                
                                                                self.imageData = QImage(self.pixelBytes, 1, 1, QImage.Format_RGBA8888)
                                                                self.pixelC = self.imageData.pixelColor(0,0)
                                                            
                                                                #devo correggere l'alpha del pixel con l'alpha del layer. ma non lo correggo se il layer è quello attuale, che è trasparente. così la pennellata successiva si vede uguale
                                                                if curLayer.uniqueId() == document.activeNode().uniqueId():
                                                                    correzMul = 1.0
                                                                else:
                                                                    layerOpac = curLayer.opacity() # tra  0 e 255
                                                                    correzMul = float(layerOpac) /  255.0
                                                                                                                            
                                                                
                                                                #print(f"color under cursor =  r:{self.pixelC.red()}, g:{self.pixelC.green()}, b:{self.pixelC.blue()} ,a:{self.pixelC.alpha()}")
                                                                
                                                                colors.append(  rgb(self.pixelC.red(),  self.pixelC.green(),  self.pixelC.blue(),  self.pixelC.alpha()  * correzMul))
                                                        
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
                 
                 
                                                
                                                canv = self.g_how_much_canvas_to_pick_on_timer
                                                
                                                fgMul = 1.0 - canv
                                                comp[0] = (self.last_color_picked.r/255.0) * fgMul + (mergedColor.r / 255.0)  * canv
                                                comp[1] = (self.last_color_picked.g / 255.0) * fgMul + (mergedColor.g / 255.0)  * canv
                                                comp[2] = (self.last_color_picked.b / 255.0) * fgMul + (mergedColor.b  / 255.0)  * canv
                                                
                                                # comp[0] =  (mergedColor.r / 255.0)  
                                                # comp[1] =  (mergedColor.g / 255.0)
                                                # comp[2] = (mergedColor.b  / 255.0)
                                          
                                                fg.setComponents(comp)
                                                
                                                view.setForeGroundColor(fg)
                                                
                                                

                
        # def mixSmall(self):
                # return self.mix(0.66)  #0.66 from canvas
                
        # def mixBig(self):
                # return self.mix( 0.33)  #0.33 from canvas
        
                                   
        def pick(self, showMessage = True):
                # print("pick called")
                app = Krita.instance()
                win = app.activeWindow()
                if win is not None:
                        # print("pick called 1")
                        view = win.activeView()
                        if view is not None:
                                # print("pick called 2")
                                document = view.document()
                                if document:
                                        # print("pick called 3")
                                        center = QPointF(0.5 * document.width(), 0.5 * document.height())
                                        p = get_cursor_in_document_coords()
                                        doc_pos = p + center
                                        # print(f'cursor at: x={doc_pos.x()}, y={doc_pos.y()}')
                                        
                                        parentNode = document.activeNode().parentNode()
                                        
                                        
                                        if parentNode is not None:
                                                # print("pick called 4")
                                                brothers = parentNode.childNodes()
                                                colors = []
                                                
                                                #costruisco colors
                                                for curLayer in brothers:
                                                
                                                        self.pixelBytes = curLayer.pixelData(doc_pos.x(), doc_pos.y(), 1, 1)
                                                        
                                                        self.imageData = QImage(self.pixelBytes, 1, 1, QImage.Format_RGBA8888)
                                                        self.pixelC = self.imageData.pixelColor(0,0) # valori tra 0 e 255

                                                        # devo correggere l'alpha del pixel con l'alpha del layer. ma non lo correggo se il layer è quello attuale, che è trasparente. così la pennellata successiva si vede uguale
                                                        # if curLayer.uniqueId() == document.activeNode().uniqueId():
                                                            # correzMul = 1.0
                                                        # else:
                                                        layerOpac = curLayer.opacity() # tra  0 e 255
                                                        correzMul = float(layerOpac) /  255.0
                                                        
                                                        

                                                        #print(f"pick: color under cursor =  r:{self.pixelC.red()}, g:{self.pixelC.green()}, b:{self.pixelC.blue()} ,a:{self.pixelC.alpha() }, a corretto = {self.pixelC.alpha() * correzMul}")
                                                        
                                                        colors.append(  rgb(self.pixelC.red(),  self.pixelC.green(),  self.pixelC.blue(),  self.pixelC.alpha() * correzMul ))
                                                
                                                #creo il colore composito
                                                
                                                mergedColor = calcolaCompositeColor(colors);
                                                print (f"picked color: {mergedColor.toString()}")
                                                                
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
                                                #print(f"fg color = {comp}")
                 
                                                comp[0] =  (mergedColor.r / 255.0)  
                                                comp[1] =  (mergedColor.g / 255.0)
                                                comp[2] = (mergedColor.b  / 255.0)
                                          
                                                fg.setComponents(comp)
                                                
                                                view.setForeGroundColor(fg)

                                                # messaggio
                                                if showMessage:
                                                    view.showFloatingMessage("Pick color", QIcon(), timeMessage, 1)
                                                
        
        
        
        def increaseMixing(self):
                self.g_how_much_canvas_to_pick += g_mixing_step
                if self.g_how_much_canvas_to_pick > 1.0:
                        self.g_how_much_canvas_to_pick = 1.0
                        
                Krita.instance().writeSetting("colorPlus", "g_how_much_canvas_to_pick", str(self.g_how_much_canvas_to_pick))
                
                quickMessage(f"Increased mixing to {round(self.g_how_much_canvas_to_pick* 100.0)}%")
        
        def decreaseMixing(self):
                self.g_how_much_canvas_to_pick -= g_mixing_step
                if self.g_how_much_canvas_to_pick < 0.0:
                        self.g_how_much_canvas_to_pick = 0.0
                        
                Krita.instance().writeSetting("colorPlus", "g_how_much_canvas_to_pick", str(self.g_how_much_canvas_to_pick))
                
                quickMessage(f"Decreased mixing to {round(self.g_how_much_canvas_to_pick * 100.0)}%")
        

        

        # def increaseMixing_targetLogic(self):
                # self.mixing_target_distance += g_step_mixing_target_distance
                # if self.mixing_target_distance > 255.0:
                        # self.mixing_target_distance = 255.0
                        
                        
                # quickMessage(f"Increased mixing. Target distance from fg color: {round(self.mixing_target_distance )}")
        
        # def decreaseMixing_targetLogic(self):
                # self.mixing_target_distance -= g_step_mixing_target_distance
                # if self.mixing_target_distance < 0.0:
                        # self.mixing_target_distance = 0.0
                        
                # quickMessage(f"Decreased mixing. Target distance from fg color: {round(self.mixing_target_distance)}")

                
        def increaseLayerOpacity(self):
        
        

                
                #self.dryPaper() # conviene, perche' tanto significa che i segni precedenti non si vedono.
                
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
        

        def increaseAutoOpacityMaxDistance(self):
        
        
                global g_auto_opacity_max_distance
                g_auto_opacity_max_distance += 5
                
                if g_auto_opacity_max_distance > 255:
                        g_auto_opacity_max_distance = 255
                
                
                Krita.instance().writeSetting("colorPlus", "g_auto_opacity_max_distance", g_auto_opacity_max_distance)
                
                
                quickMessage(f"Increased max distance to {g_auto_opacity_max_distance}")
        
        
        def decreaseAutoOpacityMaxDistance(self):
        
        
                global g_auto_opacity_max_distance
                g_auto_opacity_max_distance -= 5
                
                if g_auto_opacity_max_distance <= 0 :
                        g_auto_opacity_max_distance = 0
                
                
                Krita.instance().writeSetting("colorPlus", "g_auto_opacity_max_distance", g_auto_opacity_max_distance)
                quickMessage(f"Decreased max distance to {g_auto_opacity_max_distance}")
        


        def decreaseLayerOpacity(self):
                
                # application = Krita.instance()
                # currentDoc = application.activeDocument()
                # activeLayer = currentDoc.activeNode()
                # blurFilter = application.filter('gaussian blur')
                # blurFilter.apply(activeLayer, 0, 0, 3000, 2000)
                
                #self.dryPaper() # conviene, perche' tanto significa che i segni precedenti non si vedono.
                
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
                                        
                                        
        def dryPaperWithMessage(self):
            self.dryPaper(True)
            
        def dryPaperOldWithMerge(self, showMessage = True):
                global g_opacity_decided_for_layer
                print(f"dry paper called showMessage = {showMessage}")
                application = Krita.instance()
                currentDoc = application.activeDocument()
                activeLayer = currentDoc.activeNode()
                
                # application.action('selectopaque').trigger()
                # currentDoc.waitForDone () # action needs to finish before continuing
                # selectionStroke = currentDoc.selection()
                
                parentNode = activeLayer.parentNode()
                newLa = None
                if parentNode is not None:  
                        print("dry paper called1")
                        oldOpacity = activeLayer.opacity()
                        activeLayer.mergeDown()
                        currentDoc.waitForDone()
                        
                        root = currentDoc.rootNode()
                        newLa = currentDoc.createNode("Wet_area", "paintLayer")
                        newLa.setOpacity(oldOpacity)
                        
                        backgroundLayer = parentNode.childNodes()[0]
                        
                        
                        parentNode.addChildNode(newLa, None)
                        
                        
                        g_opacity_decided_for_layer = False
                        
                        # currentDoc.setActiveNode(newLa)
                        # currentDoc.refreshProjection()
                        # currentDoc.waitForDone()
                        
                        
                        
                else:
                        
                        newLa = currentDoc.createNode("Wet_area", "paintLayer")
                        newLa.setOpacity(50.0 * 255.0 / 100.0)
                        root.addChildNode(newLa, None)
                        
                        
                        g_opacity_decided_for_layer = False
                        
                        
                #test blur        
                
                if showMessage:
                    print("dry paper called message")
                    quickMessage("Dry paper")
                    #application.activeWindow().activeView().showFloatingMessage("Dry paper", QIcon(), timeMessage, 1)
                        
                return newLa
        
        def dryPaper(self, showMessage = True):
                print(f"dry paper called showMessage = {showMessage}")
                application = Krita.instance()
                currentDoc = application.activeDocument()
                activeLayer = currentDoc.activeNode()
                
                # application.action('selectopaque').trigger()
                # currentDoc.waitForDone () # action needs to finish before continuing
                # selectionStroke = currentDoc.selection()
                
                parentNode = activeLayer.parentNode()
                newLa = None
                if parentNode is not None:  
                        print("dry paper called1")
                        oldOpacity = activeLayer.opacity()
                        
                        #activeLayer.mergeDown()
                        #currentDoc.waitForDone()
                        
                        root = currentDoc.rootNode()
                        newLa = currentDoc.createNode("Wet_area", "paintLayer")
                        newLa.setOpacity(oldOpacity)
                        
                        backgroundLayer = parentNode.childNodes()[0]
                        
                        
                        parentNode.addChildNode(newLa, None)
                        
                        global g_opacity_decided_for_layer
                        g_opacity_decided_for_layer = False
                        
                        
                        # currentDoc.setActiveNode(newLa)
                        # currentDoc.refreshProjection()
                        # currentDoc.waitForDone()
                        
                        
                        
                else:
                        messageBox("In order to call \"Dry paper\", the current layer needs to have a parent group")
                        showMessage = False
                        # newLa = currentDoc.createNode("Wet_area", "paintLayer")
                        # newLa.setOpacity(50.0 * 255.0 / 100.0)
                        # root.addChildNode(newLa, None)
                        
                #test blur        
                
                if showMessage:
                    print("dry paper called message")
                    quickMessage("Dry paper")
                    #application.activeWindow().activeView().showFloatingMessage("Dry paper", QIcon(), timeMessage, 1)
                        
                return newLa
        
        def mergeOnTimer(self): # does not work. cannot set the active layer after merging down.
                    #print(f"dry paper called showMessage = {showMessage}")
                application = Krita.instance()
                currentDoc = application.activeDocument()
                if currentDoc is not None:
                    activeLayer = currentDoc.activeNode()
                    if activeLayer is not None:
                        
                        # application.action('selectopaque').trigger()
                        # currentDoc.waitForDone () # action needs to finish before continuing
                        # selectionStroke = currentDoc.selection()
                        
                        parentNode = activeLayer.parentNode()

                        if parentNode is not None:  
                                
                                
                                
                                
                                
                                children = parentNode.childNodes() 
                                if len(children) > 3:
                                        
                                        
                                        
                                    lastLayer = children[1] # skip the background which has opacity 100%. but follow the order from closest to bg to farthest 
                                
                                    lastLayer.mergeDown()
                                    currentDoc.waitForDone()
                                    #merged all layers. Create a new one and set opacity
                                    #currentDoc.setActiveNode(children[-1])
                                    
                                    quickMessage("auto dry layer")
                                    
                                    
                                    
                                    #setActiveNode does not work. Workaround is:
                                    children = parentNode.childNodes() 
                                    target_node = children[1]
                                    model, s_model = get_layer_model()
                                    index = node_to_index(target_node, model)
                                    print (f"index is {index}")

                                    s_model.setCurrentIndex(index, QItemSelectionModel.Select)
                                    
                                    #currentDoc.setActiveNode(children[1])
                                    
                                
              
        def mergeCleanup(self):
                #print(f"dry paper called showMessage = {showMessage}")
                application = Krita.instance()
                currentDoc = application.activeDocument()
                activeLayer = currentDoc.activeNode()
                
                # application.action('selectopaque').trigger()
                # currentDoc.waitForDone () # action needs to finish before continuing
                # selectionStroke = currentDoc.selection()
                
                parentNode = activeLayer.parentNode()
                newLa = None
                if parentNode is not None:  
                        print("dry paper called1")
                        oldOpacity = activeLayer.opacity()
                        
                        
                        while True:
                            children = parentNode.childNodes() 
                            if len(children) <= 1:
                                break
                                
                                
                            lastLayer = children[1] # skip the background which has opacity 100%. but follow the order from closest to bg to farthest 
                        
                            lastLayer.mergeDown()
                        
                        #merged all layers. Create a new one and set opacity
                        
                        currentDoc.waitForDone()
                        
                        # root = currentDoc.rootNode()
                        newLa = currentDoc.createNode("Wet_area", "paintLayer")
                        newLa.setOpacity(oldOpacity)
                        
                        # backgroundLayer = parentNode.childNodes()[0]
                        
                        
                        parentNode.addChildNode(newLa, None)
                        
                        # # currentDoc.setActiveNode(newLa)
                        # # currentDoc.refreshProjection()
                        # # currentDoc.waitForDone()
                        
                        
                        
                else:
                        messageBox("In order to call \"Cleanup layers\", the current layer needs to have a parent group")
                        showMessage = False
                        # newLa = currentDoc.createNode("Wet_area", "paintLayer")
                        # newLa.setOpacity(50.0 * 255.0 / 100.0)
                        # root.addChildNode(newLa, None)
                        newLa = None
                        
                #test blur        
                
                
                print("cleanup layers called message")
                quickMessage("Cleanup layers")
                 #application.activeWindow().activeView().showFloatingMessage("Dry paper", QIcon(), timeMessage, 1)
                        
                return newLa
        
        def dryPaperAndPick(self):
            print("dry paper and pick")
            
            #non funziona se inverto l'ordine... non capisco perche'
            self.pick(showMessage = False)
            
            
            
            # find if there is a parent node
            hasParentNode = False
            app = Krita.instance()
            win = app.activeWindow()
            if win is not None:
                        # print("pick called 1")
                        view = win.activeView()
                        if view is not None:
                                # print("pick called 2")
                                document = view.document()
                                if document:
                                        
                                        parentNode = document.activeNode().parentNode() # could be root node, so I need to do parent again
                                        
                                        
                                        if parentNode is not None:
                                                pa = parentNode.parentNode()
                                                if pa is not None:
                                                    print(f"has parent node. document file {document.fileName()}. parentNode = {parentNode.name()}")
                                                    hasParentNode = True
            
            
            
            
            
            if self.temp_switched_to_100_previous_opac is None and hasParentNode: # I don't want to add a layer if I'm picking from the mixing palette, or if I've switched to 100 percent opacity mode
                self.dryPaper(showMessage = False)
                quickMessage("Dry paper and pick color")
            else:
                #useless to dry paper because I am at 100% opacity
                quickMessage("Picked color")
                
        
        # def dryPaperAndMix(self):
            # print("dry paper and mix")
            
            # #non funziona se inverto l'ordine... non capisco perche'
            # self.mixFgColorWithBgColor_normalLogic()
            
            # if self.temp_switched_to_100_previous_opac is None:
                # self.dryPaper(showMessage = False)
                # #quickMessage("Dry paper and mix color")
            # else:
                # #useless to dry paper because I am at 100% opacity
                # pass
                # #quickMessage("Picked color")
                
        def minimizeOnTopAndViewFullScreen(self):
                app = Krita.instance()
                                
                # print(f"windows = {app.windows()}")                
                # print(f"active window title = {app.activeWindow().qwindow().windowTitle()}")
                
                wi = app.activeWindow()
                
                
                #for wi in app.windows():
                # print(f"---------")
                # print(f"window title = {wi.qwindow().windowTitle()}")
                # print(f"wi views = {wi.views()}")
                # print (f"wi subwindows = {wi.qwindow().findChild(QMdiArea).subWindowList()}")
                
                subwins = wi.qwindow().findChild(QMdiArea).subWindowList()
                
                
                
                app.action('view_show_canvas_only').trigger()
                app.activeDocument().waitForDone () # action needs to finish before continuing
                
                
                #workaround per mancanza di fit to page
                app.action('zoom_to_100pct').trigger()
                app.activeDocument().waitForDone () # action needs to finish before continuing
                
                app.action('toggle_zoom_to_fit').trigger()
                app.activeDocument().waitForDone () # action needs to finish before continuing
                
                
                
                
                # ordina le finestre in modo che la always on top sia per prima, altrimenti poi l'action fit to window avviene alla finestra sbagliata.
                
                
                for su in subwins:
                    flags = su.windowFlags()
                    
                    stayOnTop = False
                    if su.windowFlags() & Qt.WindowStaysOnTopHint:
                        stayOnTop = True
                    else:
                        stayOnTop = False
                    

                    isMinimized = False
                    if su.windowState() & Qt.WindowMinimized:
                        isMinimized = True
                    else:
                        isMinimized = False

                    print(f"subwindow title = {su.windowTitle()}, stay on top = {stayOnTop    }, minimized = {isMinimized}")

                    
                    if stayOnTop:
                        if isMinimized:
                            su.setWindowState(su.windowState() & ~Qt.WindowMinimized)
                        else:
                            su.setWindowState(su.windowState() | Qt.WindowMinimized)
                

                #I activate any window that is not on top and not minimized
                for su in subwins:
                    flags = su.windowFlags()
                    
                    stayOnTop = False
                    if su.windowFlags() & Qt.WindowStaysOnTopHint:
                        stayOnTop = True
                    else:
                        stayOnTop = False
                    

                    isMinimized = False
                    if su.windowState() & Qt.WindowMinimized:
                        isMinimized = True
                    else:
                        isMinimized = False


                    if not isMinimized and not stayOnTop:
                        
                        q_win = wi.qwindow()
                        mdi_area = q_win.findChild(QMdiArea)
                        mdi_area.setActiveSubWindow(su)


                # end for
                
                
                            
                          
        # def setup(self):
        
                # try:
                    # print ("swap: initializing plugin LastColor...")
                    
                    # # app = Krita.instance()
                    # # history_docker = next((d for d in app.dockers() if d.objectName() == 'History'), None)
                    # # kis_undo_view = next((v for v in history_docker.findChildren(QListView) if v.metaObject().className() == 'KisUndoView'), None)
                    # # s_model = kis_undo_view.selectionModel()
                    # # s_model.currentChanged.connect(self._on_history_was_made)
                    
                    # # self.inited = True;
                    # # print ("swap: initialized")
                
                # except Exception as e:
                    # print(f"errore trovato in setup {e}")
                    
                                
        def onEnter(self):
            print(f"enter event")
            
            
        def toggleAutoFocus(self):
            if self.g_auto_focus == "true":
                
                self.g_auto_focus = "false"
            else:
                
                self.g_auto_focus = "true"
                
            Krita.instance().writeSetting("colorPlus", "g_auto_focus", self.g_auto_focus)
            
        def createActions(self, window):
        


                action = window.createAction("LastColor", "Switch to last used color")
                action.triggered.connect(self.switchToLastColor)
                
                # action2 = window.createAction("MixColorBig", "MixColorBig")
                # action2.triggered.connect(self.mixBig)
                
                # action2 = window.createAction("MixColorSmall", "MixColorSmall")
                # action2.triggered.connect(self.mixSmall)


                actionMix = window.createAction("MixColor", "Pick some color from canvas and mix with fg color")
                actionMix.triggered.connect(self.mixFgColorWithBgColor_normalLogic)
                
                actionMixSmall = window.createAction("MixColorSmall", "Pick some color from canvas, but no more than a given distance")
                actionMixSmall.triggered.connect(self.mixFgColorWithBgColor_maxDistanceLogic)
                
                actionMix = window.createAction("DryPaperAndPick", "Dry the paper and pick color under cursor with a single key press")
                actionMix.triggered.connect(self.dryPaperAndPick)
                
                
                actionPick = window.createAction("PickColor", "Pick color under cursor")
                actionPick.triggered.connect(self.pick)

                actionDryPaper = window.createAction("LayerMergeDownAndNew", "Dry the paper")
                actionDryPaper.triggered.connect(self.dryPaperWithMessage)

                actionViewFullScreen = window.createAction("ViewSingleWindow", "Hide always on top windows and go fullscreen")
                actionViewFullScreen.triggered.connect(self.minimizeOnTopAndViewFullScreen)

                actionIncreaseLO = window.createAction("IncreaseLayerOpacity", "Increase current layer opacity")
                actionIncreaseLO.triggered.connect(self.increaseLayerOpacity)

                actiondeclo = window.createAction("DecreaseLayerOpacity", "Decrease current layer opacity")
                actiondeclo.triggered.connect(self.decreaseLayerOpacity)



                # actionIncreaseAO = window.createAction("IncreaseMaxDistanceAutoOpacity", "Increase max distance for auto opacity")
                # actionIncreaseAO.triggered.connect(self.increaseAutoOpacityMaxDistance)

                # actiondecao = window.createAction("DecreaseMaxDistanceAutoOpacity", "Decrease max distance for auto opacity")
                # actiondecao.triggered.connect(self.decreaseAutoOpacityMaxDistance)

                actionincmi = window.createAction("IncreaseMixing", "Increase mixing level (increase amount of color you pick from canvas)")
                actionincmi.triggered.connect(self.increaseMixing)

                actiondecmi = window.createAction("DecreaseMixing", "Decrease mixing level (decrease amount of color you pick from canvas)")
                actiondecmi.triggered.connect(self.decreaseMixing)


                actionSave = window.createAction("saveWindowPositions", "Save state and position of all windows")
                actionSave.setShortcut("Ctrl+Shift+F")
                actionSave.triggered.connect(self.saveWindowPositions)
                
                actionRestore = window.createAction("restoreWindowPositions", "Restore state and position of all windows")
                actionRestore.setShortcut("Ctrl+Shift+R")
                actionRestore.triggered.connect(self.restoreWindowPositions)
                
                actionToggle100= window.createAction("toggle100PercOpacity", "Toggle 100% layer opacity")
                actionToggle100.setShortcut("f")
                actionToggle100.triggered.connect(self.toggle_100_opac)

                actionToggle25= window.createAction("toggle25PercOpacity", "Toggle 25% layer opacity")
                actionToggle25.setShortcut("w")
                actionToggle25.triggered.connect(self.toggle_25_opac)


                actionToggleMc= window.createAction("cleanupLayers", "Cleanup all wet layers")
                actionToggleMc.triggered.connect(self.mergeCleanup)
                
                
                self.actionAutoFocus= window.createAction("autoFocus", "Autofocus windows on mouse over")
                self.actionAutoFocus.setCheckable(True)
                self.actionAutoFocus.setChecked(self.g_auto_focus == "true")
                self.actionAutoFocus.triggered.connect(self.toggleAutoFocus)
                
                
                main_menu = window.qwindow().menuBar()
                custom_menu = main_menu.addMenu("ColorPlus")
                
                custom_menu.addAction(self.actionAutoFocus)
                custom_menu.addSeparator()
                custom_menu.addAction(actionViewFullScreen)
                
                custom_menu.addSeparator()
                custom_menu.addAction(actionDryPaper)
                
                custom_menu.addAction(actionToggleMc)
                
                custom_menu.addSeparator()
                custom_menu.addAction(actionRestore)
                custom_menu.addAction(actionSave)
                custom_menu.addSeparator()
                # custom_menu.addAction(actionPick)
                # custom_menu.addAction(actionMix)
                # custom_menu.addAction(actionMixSmall)
                
                custom_menu.addAction(actionIncreaseLO)
                custom_menu.addAction(actiondeclo)
                custom_menu.addSeparator()
                custom_menu.addAction(actionincmi)
                custom_menu.addAction(actiondecmi)
                custom_menu.addSeparator()
                custom_menu.addAction(actionToggle100)
                custom_menu.addAction(actionToggle25)
                
                



            
                

                
                
# And add the extension to Krita's list of extensions:
Krita.instance().addExtension(MyExtension(Krita.instance()))

