# TODO when changing color via the selector, then press mix, it didn't start new layer, because it erases all
#TODO when using C on reference, add layer to real image.
#TODO when chanign opacity of reference, do it on real image
#todo pick color via button does not reset opacity of layer

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
import queue

### BEGIN imported from urzeye https://krita-artists.org/t/i-realized-the-spectral-mixing-of-mypaint-in-krita/33473/197?u=seguso
from math import sqrt

R = [0.327457414, 0.323750578, 0.313439461, 0.288879383, 0.239205681, 0.189702037, 0.121746068, 0.074578271, 0.044433159, 0.028928632, 0.022316653, 0.016911307, 0.014181107, 0.013053143, 0.011986164, 0.011288715, 0.010906066, 0.010400713, 0.010637360, 0.010907663, 0.011032712, 0.011310657, 0.011154642, 0.010148770, 0.008918582, 0.007685576, 0.006705708, 0.005995806, 0.005537257, 0.005193784, 0.005025362, 0.005136363, 0.005433200, 0.005819986, 0.006400573, 0.007449529, 0.008583636, 0.010395762, 0.013565434, 0.019384516, 0.032084071, 0.074356038, 0.624393724, 0.918310033, 0.949253030, 0.958187833, 0.958187751, 0.958187625, 0.955679061, 0.958006155, 0.954101573, 0.947607606, 0.938681328, 0.924466683, 0.904606025, 0.880412199, 0.847787873, 0.805779127, 0.752531854, 0.686439397, 0.618694571, 0.540264444, 0.472964416, 0.432701597, 0.405358046, 0.385491835, 0.370983585, 0.357608702, 0.348712800, 0.344880119, 0.341917877, 0.339531093, 0.337169504, 0.336172019, 0.335167443, 0.334421625, 0.334008760, 0.333915793, 0.333818455, 0.333672775, 0.333569513]

G = [0.331861713, 0.329688188, 0.327860022, 0.319173580, 0.294322584, 0.258697065, 0.188894319, 0.125388382, 0.078687060, 0.053143271, 0.042288146, 0.033318346, 0.029755948, 0.030331251, 0.030988572, 0.031686355, 0.034669962, 0.034551957, 0.040684806, 0.054460037, 0.080905287, 0.146348303, 0.379679643, 0.766744269, 0.876214748, 0.918491656, 0.940655563, 0.953731885, 0.961643280, 0.967200020, 0.970989746, 0.972852304, 0.973116594, 0.973351069, 0.973351116, 0.972261080, 0.973351022, 0.973148495, 0.971061306, 0.966371306, 0.954941968, 0.913578990, 0.364348804, 0.071507243, 0.041230434, 0.032423874, 0.031924630, 0.031276033, 0.032630370, 0.029530872, 0.031561761, 0.035674218, 0.041403005, 0.050604260, 0.063434300, 0.078918245, 0.099542743, 0.125595760, 0.157590910, 0.195398239, 0.231474475, 0.268852136, 0.296029164, 0.309754994, 0.317815883, 0.322990347, 0.326353848, 0.329143902, 0.330808727, 0.331482690, 0.331984550, 0.332341173, 0.332912009, 0.332919280, 0.333027673, 0.333179705, 0.333247031, 0.333259349, 0.333275050, 0.333294328, 0.333309425]

B = [0.340680792, 0.346561187, 0.358700493, 0.391947027, 0.466471731, 0.551600896, 0.689359611, 0.800033347, 0.876879781, 0.917928097, 0.935395201, 0.949770347, 0.956062945, 0.956615607, 0.957025265, 0.957024931, 0.954423973, 0.955047329, 0.948677833, 0.934632300, 0.908062000, 0.842341039, 0.609165715, 0.223106961, 0.114866670, 0.073822768, 0.052638729, 0.040272309, 0.032819463, 0.027606196, 0.023984891, 0.022011333, 0.021450205, 0.020828945, 0.020248311, 0.020289391, 0.018065342, 0.016455742, 0.015373260, 0.014244178, 0.012973962, 0.012064974, 0.011257478, 0.010182725, 0.009516535, 0.009388293, 0.009887619, 0.010536342, 0.011690569, 0.012462973, 0.014336665, 0.016718175, 0.019915666, 0.024929056, 0.031959674, 0.040669554, 0.052669382, 0.068625111, 0.089877232, 0.118162359, 0.149830947, 0.190883409, 0.231006403, 0.257543385, 0.276826039, 0.291517773, 0.302662506, 0.313247301, 0.320478325, 0.323636995, 0.326097309, 0.328127369, 0.329917976, 0.330907901, 0.331803633, 0.332396627, 0.332740781, 0.332820857, 0.332901731, 0.333025967, 0.333111083]

X = [0.000032348, 0.000055345, 0.000109712, 0.000248676, 0.000560325, 0.000955933, 0.001883435, 0.003396138, 0.005940683, 0.009151623, 0.011644017, 0.014886349, 0.017280890, 0.018269793, 0.018613167, 0.017704928, 0.016210296, 0.013821903, 0.010617328, 0.007758482, 0.005245854, 0.003081053, 0.001648031, 0.000758713, 0.000253535, 0.000123299, 0.000474370, 0.001463582, 0.003137073, 0.005509365, 0.008432888, 0.011327476, 0.014345805, 0.017738600, 0.021338869, 0.024718236, 0.028129296, 0.031510755, 0.034737572, 0.038293448, 0.041529413, 0.042708709, 0.043065991, 0.044671789, 0.045236160, 0.044428484, 0.042504837, 0.039361202, 0.035455761, 0.030395676, 0.025316176, 0.021408237, 0.017738193, 0.013975302, 0.010734839, 0.008290878, 0.006258656, 0.004659214, 0.003402523, 0.002415889, 0.001732401, 0.001151995, 0.000748856, 0.000529624, 0.000384871, 0.000280078, 0.000203686, 0.000132161, 0.000084501, 0.000063740, 0.000047616, 0.000034298, 0.000024514, 0.000015617, 0.000009990, 0.000006116, 0.000003646, 0.000003134, 0.000002624, 0.000001817, 0.000001260]

Y = [0.000000922, 0.000001584, 0.000003103, 0.000007054, 0.000015506, 0.000026382, 0.000052378, 0.000095370, 0.000176832, 0.000311062, 0.000475768, 0.000763124, 0.001141210, 0.001564213, 0.002103808, 0.002666572, 0.003344628, 0.004067856, 0.004944536, 0.006147819, 0.007625247, 0.009001248, 0.010709887, 0.013347152, 0.016712607, 0.020924893, 0.025656760, 0.030589357, 0.035203447, 0.039872520, 0.043922355, 0.045904502, 0.047127747, 0.048343480, 0.048981677, 0.048273090, 0.047079310, 0.045454635, 0.043393477, 0.041606911, 0.039430961, 0.035625505, 0.031765522, 0.029376763, 0.026872545, 0.024083841, 0.021324489, 0.018506141, 0.015809755, 0.012985110, 0.010443317, 0.008572776, 0.006930529, 0.005353067, 0.004051597, 0.003093441, 0.002315209, 0.001713760, 0.001245775, 0.000881268, 0.000629695, 0.000417379, 0.000270842, 0.000191353, 0.000138986, 0.000101140, 0.000073559, 0.000047731, 0.000030518, 0.000023020, 0.000017195, 0.000012381, 0.000008846, 0.000005643, 0.000003611, 0.000002212, 0.000001318, 0.000001125, 0.000000948, 0.000000647, 0.000000450]

Z = [0.000152519, 0.000261131, 0.000518438, 0.001177069, 0.002656749, 0.004542641, 0.008977810, 0.016243540, 0.028540741, 0.044275240, 0.056829693, 0.073546267, 0.086685286, 0.093569306, 0.098109991, 0.096891008, 0.093047543, 0.084114895, 0.069980019, 0.056886438, 0.044590306, 0.032761780, 0.023949742, 0.018234915, 0.014073774, 0.010906837, 0.008069383, 0.005617940, 0.003879817, 0.002877839, 0.002148221, 0.001497284, 0.001002823, 0.000660821, 0.000430765, 0.000277570, 0.000184532, 0.000127734, 0.000095721, 0.000081814, 0.000074783, 0.000061100, 0.000046159, 0.000042275, 0.000034070, 0.000025495, 0.000014414, 0.000010067, 0.000007884, 0.000004045, 0.000001970, 0.000001185, 0.000000792, 0.000000387, 0.000000000, 0.000000000, 0.000000000, 0.000000000, 0.000000000, 0.000000000, 0.000000000, 0.000000000, 0.000000000, 0.000000000, 0.000000000, 0.000000000, 0.000000000, 0.000000000, 0.000000000, 0.000000000, 0.000000000, 0.000000000, 0.000000000, 0.000000000, 0.000000000, 0.000000000, 0.000000000, 0.000000000, 0.000000000, 0.000000000, 0.000000000]

def concentration(sr, sg, sb, sw, dr, dg, db):
    sl = 0.212648173 * sr + 0.715179242 * sg + 0.072172585 * sb
    dl = 0.212648173 * sr + 0.715179242 * sg + 0.072172585 * sb

    dw = 1.0 - sw

    sw = sl * sw * sw
    dw = dl * dw * dw

    return sw / (sw + dw)

def rgb_spectral(r, g, b):
    spectral = [0.0 for x in range(0, 81)]
    for i in range(81):
        spectral[i] = R[i] * r + G[i] * g + B[i] * b
    return spectral

def mixSpectral(spectral_s, spectral_d, sw):
    for i in range(81):
        ks = inv = 0.0

        inv = (1.0 - spectral_s[i])
        ks += sw * (inv * inv / (2.0 * spectral_s[i]))

        inv = (1.0 - spectral_d[i])
        ks += (1.0 - sw) * (inv * inv / (2.0 * spectral_d[i]))

        spectral_d[i] = 1.0 + ks - sqrt(ks * ks + 2.0 * ks)
    return spectral_d

def spectral_rgb(spectral):
    x = y = z = 0.0
    for i in range(81):
        x += X[i] * spectral[i]
        y += Y[i] * spectral[i]
        z += Z[i] * spectral[i]

    r =  3.240830229 * x - 1.537316904 * y - 0.498589266 * z
    g = -0.969229321 * x + 1.875939794 * y + 0.041554444 * z
    b =  0.055645287 * x - 0.204032720 * y + 1.057260459 * z

    return [r, g, b]

def mixRGB(sr, sg, sb, t, dr, dg, db):
    sr = max(sr, 0.0001)
    sg = max(sg, 0.0001)
    sb = max(sb, 0.0001)
    dr = max(dr, 0.0001)
    dg = max(dg, 0.0001)
    db = max(db, 0.0001)

    spectral_s = rgb_spectral(sr, sg, sb)
    spectral_d = rgb_spectral(dr, dg, db)
    t = concentration(sr, sg, sb, t, dr, dg, db)
    spectral = mixSpectral(spectral_s, spectral_d, t)
    return spectral_rgb(spectral)

print(mixRGB(1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0))

###END urzeye



g_blur_on_dry = False

countColorChanged = 0

# g_mix_auto_clears_cur_layer = "1"

g_color_changed_from_selector_probably = False
global g_virtual_fg_color_rgb

global g_virtual_fg_color_rgb_previous_when_dirty_brush_on

g_btn_pick_color = None

g_top_layer_is_dirty = False

g_virtual_color_used_last_rgb  = None
g_virtual_fg_color_rgb = None

g_last_virtual_colors_used = []

timeMessage = 300
g_normal_step_layer_opacity = 20

g_mixing_step = 0.05

g_auto_mixing_distance_step = 5

g_multi_layer_mode = False

###############auto-mixing

g_auto_mixing_uses_distance_logic = False # perche' io posso prendere un colore molto diverso o molto simile. voglio contrastare sempre poco, mai tanto. altrimenti non attivo l'auto mixing.
                                                                        # d'altra parta, è sbagliato concettualmente se io fisso un target color e voglio arrivarci in N strokes
g_auto_mixing_just_once_logic = False
g_auto_mixing_just_once_now_on = False

#when distance logic is active
g_auto_mixing_target_distance = None  # value is ignored, will be read from settings.

#when distance logic is not active
g_auto_mix__how_much_canvas_to_pick = None # value is ignored: will be read from settings --- 0.999 to drag color from canvas , e.g. to remove overlap. then set auto-mixing. 

#g_auto_mix_snap_distance = 30

########################

g_auto_opacity_max_distance = 40

g_auto_dry_each_stroke = False

g_auto_mix_paused = False
g_auto_mix_enabled = False


g_dirty_brush_overall_enabled = False
g_dirty_brush_currently_on = True

from PyQt5.QtCore import Qt, QModelIndex, QItemSelectionModel
from PyQt5.QtWidgets import QTreeView



g_last_coord_mouse_down = None
g_last_coord_mouse_up = None

g_picking_color = False
g_mixing_color = False

g_temp_switched_to_100_previous_opac = None

def toggleAutoMixing():
            global g_actionAutoMix
            global g_btn_auto_mix 
            global g_auto_mix_enabled
            global g_auto_mixing_just_once_logic
            global g_auto_mixing_just_once_now_on
            
            if g_auto_mix_enabled:
                
                g_auto_mix_enabled = False
                g_actionAutoMix.setChecked(False)
                
                # you probably disabled auto-mixing in order to manually change the fg color (= target color). but the color selector has probably changed. so reset it to the current target
                resetForegroundColorToLastColorPicked()
                                
                quickMessage("Disabled auto-mixing")                                        
                
                g_btn_auto_mix.setChecked(False)
            else:
                quickMessage("Enabled auto-mixing")
                g_auto_mix_enabled = True
                g_btn_auto_mix.setChecked(True)
                g_actionAutoMix.setChecked(True)
        

class HelloDocker(DockWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ColorPlus")
        mainWidget = QWidget(self)
        self.setWidget(mainWidget)
        
        
        
        
        mainLayout = QVBoxLayout()
        mainWidget.setLayout(mainLayout)
        
        
        # active color
        
        layoutHorizColorAndDry = QHBoxLayout()
        mainLayout.addLayout(layoutHorizColorAndDry)
        
        
        
        
        btnDry = QPushButton("Dry paper", mainWidget)
        layoutHorizColorAndDry.addWidget(btnDry)
        font = btnDry.font()
        font.setPixelSize(15)
        btnDry.setFont(font)
        btnDry.setMinimumHeight(50)
        
        btnDry.clicked.connect(lambda: dryPaper())
        
        
        
        
        
        
        
        
        
        
        
        
        global lblActiveColor
        lblActiveColor = QLabel()
        lblActiveColor.setToolTip("Current foreground color")
        layoutHorizColorAndDry.addWidget(lblActiveColor)
        #lblActiveColor.setStyleSheet("background-color: red")
        lblActiveColor.setMinimumHeight(45)
        lblActiveColor.setMinimumWidth(65)
        
        
        
        
        
        
        
        
        
        
        
        
        
        # # mix layout
        layoutHorizMix = QHBoxLayout()
        mainLayout.addLayout(layoutHorizMix)
        
        
        global g_btn_mix;
        g_btn_mix = QPushButton("Mix color", mainWidget)
        g_btn_mix.setCheckable(True)
        layoutHorizMix.addWidget(g_btn_mix)
        g_btn_mix.clicked.connect(self.manualMixColorButtonClicked)
        g_btn_mix.setMinimumHeight(60)
        font = g_btn_mix.font()
        font.setPixelSize(15)
        g_btn_mix.setFont(font)
        
        
        
        
        
        global g_dial_mix
        global g_how_much_canvas_to_pick
        g_dial_mix = QDial(mainWidget)
        g_dial_mix.setToolTip("Mix level")
        layoutHorizMix.addWidget(g_dial_mix)
        g_dial_mix.setWrapping(False)
        g_dial_mix.setMinimumHeight(60)
        
        val099 =  round(g_how_much_canvas_to_pick * 100.0) - 1
        g_dial_mix.setValue(val099)
                
        g_dial_mix.valueChanged.connect(self.mixLevelValueChanged)
        
        
        
        
        
        
        
        # auto-mix layout
        
        layoutHorizAutoMix = QHBoxLayout()
        mainLayout.addLayout(layoutHorizAutoMix)
        
        
        # auto-mix button
        global g_btn_auto_mix 
        
        g_btn_auto_mix = QPushButton("Auto-mix color", mainWidget)
        g_btn_auto_mix.setCheckable(True)
        layoutHorizAutoMix.addWidget(g_btn_auto_mix)
        g_btn_auto_mix.clicked.connect(toggleAutoMixing)
        g_btn_auto_mix.setMinimumHeight(60)
        
        font = g_btn_auto_mix.font()
        font.setPixelSize(15)
        g_btn_auto_mix.setFont(font)
        
        
        
        # auto-mix level
        global g_dial_auto_mix_level
        global g_auto_mix__how_much_canvas_to_pick
        
        g_dial_auto_mix_level = QDial(mainWidget)
        g_dial_auto_mix_level.setToolTip("Auto-mix level")
        layoutHorizAutoMix.addWidget(g_dial_auto_mix_level)
        g_dial_auto_mix_level.setWrapping(False)
        g_dial_auto_mix_level.setMinimumHeight(60)
        
        val099 =  round(g_auto_mix__how_much_canvas_to_pick * 100.0) - 1
        g_dial_auto_mix_level.setValue(val099)
                
        g_dial_auto_mix_level.valueChanged.connect(self.autoMixLevelValueChanged)
        
        
        
        
        
        
        
        # pick color button
        self.buttonPickColor = QPushButton("Pick color", mainWidget)
        self.buttonPickColor.setMinimumHeight(50)
        self.buttonPickColor.setCheckable(True)
        font = self.buttonPickColor.font()
        font.setPixelSize(20)
        self.buttonPickColor.setFont(font)
        
        mainLayout.addWidget(self.buttonPickColor)
        
        
        self.buttonPickColor.clicked.connect(self.pickColorClicked)
        global g_btn_pick_color
        g_btn_pick_color = self.buttonPickColor
        
        
        
        
        
        
        # label = QLabel("Hello", self)
        # self.setWidget(label)
        # self.label = label
 
    def autoMixLevelValueChanged(self, level):
        print(f"autoMixLevelValueChanged {level}")
        
        global g_auto_mix__how_much_canvas_to_pick
        
        g_auto_mix__how_much_canvas_to_pick = ( level  + 1.0) / 100.0
        
                
        Krita.instance().writeSetting("colorPlus", "g_auto_mix__how_much_canvas_to_pick", str(g_auto_mix__how_much_canvas_to_pick))
        
        quickMessage(f"Changed auto-mixing to {round(g_auto_mix__how_much_canvas_to_pick * 100.0)} %")


    
    def manualMixColorButtonClicked(self):
    
        global g_mixing_color
        global g_btn_mix
        
        if g_btn_mix.isChecked():
            g_mixing_color = True
            
            # I create the layer even if I'm in single layer mode. Then I will either delete it or clear it
            newLa = dryPaper(showMessage = False)
            
            
            
            
        else:
            g_mixing_color = False
        
 
    def mixLevelValueChanged(self, level):
    
        global g_how_much_canvas_to_pick
        
        g_how_much_canvas_to_pick = ( level  + 1.0) / 100.0
        
                
        Krita.instance().writeSetting("colorPlus", "g_how_much_canvas_to_pick", str(g_how_much_canvas_to_pick))
        
        quickMessage(f"Changed mixing level to {round(g_how_much_canvas_to_pick * 100.0)} %")

 
    def pickColorClicked(self):
    
    
        global g_picking_color
        
        if self.buttonPickColor.isChecked():
            g_picking_color = True # I start layer picking mode
            
            # global g_multi_layer_mode
            # if g_multi_layer_mode:
            
            # i need to create a layer because I can then exclude the stroke just drawn and delete it.
            newLa = dryPaper(showMessage = False)  # I create the layer, but if not multi-layer-mode I will then delete it when the color is actually picked
            
            
            # I need to reset to default opacity
            application = Krita.instance()
            document = application.activeDocument()
            if document is not None:
                global g_auto_reset_opacity_on_pick_level
                global g_auto_reset_opacity_on_pick
                global g_temp_switched_to_100_previous_opac
                global g_multi_layer_mode
                if  g_temp_switched_to_100_previous_opac is None and g_multi_layer_mode: # I don't want to add a layer if I'm picking from the mixing palette, or if I've switched to 100 percent opacity mode
                    
                    
                                            
                    if g_auto_reset_opacity_on_pick == 1 :
                        newLa.setOpacity(g_auto_reset_opacity_on_pick_level * 255.0 / 100.0) # bm_djiwejdie
                        
                        document.refreshProjection()
                
            
            
        else:
            g_picking_color = False
        
        
    def canvasChanged(self, canvas):
        #self.label.setText("Hellodocker: canvas changed");
        pass
 



def get_layer_model():
    app = Krita.instance()
    kis_layer_box = next((d for d in app.dockers() if d.objectName() == 'KisLayerBox'), None)
    view = kis_layer_box.findChild(QTreeView, 'listLayers')
    return view.model(), view.selectionModel()


def getColorUnderCursorOrAtPos(skipCurrentLayer = False, forcedPos = None, pretendLastLayerIsFgColor = False):  
    #forcedPos is of type xy
    
    if skipCurrentLayer and pretendLastLayerIsFgColor:
        raise "Makes no sense to skipCurrentLayer and pretendLastLayerIsFgColor. these are exclusive."
        
    
    application = Krita.instance()
    document = application.activeDocument()
    
    if document:
            win = application.activeWindow()
            
            center = QPointF(0.5 * document.width(), 0.5 * document.height())
            
            if forcedPos is None:
                p = get_cursor_in_document_coords()  # questo dà la posizione da (-docwt/2, -docht/2) a (docwt/2, docht/2)
                doc_pos = p + center  # per cui aggiungo metà della larghezza documento e metà altezza. così è nel range (0, 0) -- (docwt, docht)
                doc_posxy = xyOfQpoint(doc_pos) # passo a intero
            else:
                doc_posxy = xy(forcedPos.x + int(round(center.x())), forcedPos.y + int(round(center.y())))
            
            
            #print(f'cursor at: x={doc_pos.x()}, y={doc_pos.y()}')
            
            
            
            parentNode = document.activeNode().parentNode()
            
            fgCol = None
            if pretendLastLayerIsFgColor:
                
                if win is not None:
                        view = win.activeView()
                        if view is not None:
                            fg = view.foregroundColor() 
                            comp = fg.components() 
                            
                            fgCol = rgb( int  (comp[0] * 255.0), int  (comp[1] * 255.0), int  (comp[2] * 255.0), 1)
                else:
                    return None
                    
                    
            
            if parentNode is not None:
            
                    brothers = parentNode.childNodes()
                    colors = []
                    
                    #costruisco colors
                    for curLayer in brothers:
                    
                            
                            if curLayer.uniqueId() == document.activeNode().uniqueId() and skipCurrentLayer:
                                #print ("salto cur layer")
                                continue
                                
                            if curLayer.uniqueId() == document.activeNode().uniqueId() and pretendLastLayerIsFgColor :
                                
                                    layerOpac = curLayer.opacity() # tra  0 e 255
                                    
                                    paintingOp01 = win.activeView().paintingOpacity()  
                                    # print(f"opacity = {paintingOp}")
                                    colors.append( rgb(fgCol.r, fgCol.g, fgCol.b, int(layerOpac * paintingOp01)))
                                    
                                
                            else:
                                    
                                pixelBytes = curLayer.pixelData(doc_posxy.x, doc_posxy.y, 1, 1)
                                
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


def dryPaper( showMessage = True):
                
                global g_blur_on_dry
                
                
                
                print(f"dry paper called showMessage = {showMessage}")
                application = Krita.instance()
                currentDoc = application.activeDocument()
                if currentDoc is  None:
                
                    return None
                else:
                    activeLayer = currentDoc.activeNode()
                    
                    if g_blur_on_dry:
                        application.action('selectopaque').trigger()
                        currentDoc.waitForDone () # action needs to finish before continuing
                        selectionStroke = currentDoc.selection()
                        blurFilter = application.filter('gaussian blur')
                        blurFilter.setProperty('level', 50)
                        blurFilter.setProperty('radius', 50)
                    
                    
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
                            
                            
                            
                            if g_blur_on_dry:
                                # al layer precedente ad activeLayer, applica il blur
                                for layerPrima in parentNode.childNodes()[ : -2]:
                                    
                                    print(f"applicando blur a  {layerPrima.name()}:{selectionStroke.x()}, {selectionStroke.y()}, {selectionStroke.width()},{selectionStroke.height()}")
                                    
                                    selFuori = Selection()
                                    selFuori.select(selectionStroke.x(), selectionStroke.y(), selectionStroke.width(), selectionStroke.height(), 255)
                                    selFuori.subtract(selectionStroke)
                                    
                                    currentDoc.setSelection(selFuori)
                                    selFuori.copy(layerPrima)
                                    
                                    blurFilter.apply(layerPrima, selectionStroke.x(), selectionStroke.y(), selectionStroke.width(), selectionStroke.height()) 
                                    
                                    currentDoc.setSelection(None)
                                    #paste è bacata, non posso usarlo                               
                                    #selFuori.paste(layerPrima, selectionStroke.x() + 20  , selectionStroke.y() + 20 ) # copia il pezzo che non doveva essere blurred
                                    
                                    currentDoc.setActiveNode(layerPrima)
                                    Krita.instance().action('edit_paste').trigger()
                                    
                                    
                                    currentDoc.waitForDone () # action needs to finish before continuing
                                    
                                    
                                    
                                    # ora ci devo 
                                    
                                    
                                currentDoc.refreshProjection()
                                currentDoc.setSelection(None)
                                #currentDoc.setSelection(None)
                            
                            global g_opacity_decided_for_layer
                            g_opacity_decided_for_layer = False
                            
                            
                            global g_top_layer_is_dirty
                            g_top_layer_is_dirty = False
                            
                            # currentDoc.setActiveNode(newLa)
                            
                            
                            
                            # currentDoc.refreshProjection() # tenta di agggirare il bug di quickmessage a tutto schermo
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

def update_label_from_virtual_color():
    global g_virtual_fg_color_rgb
    global lblActiveColor
    r = g_virtual_fg_color_rgb.r
    g = g_virtual_fg_color_rgb.g
    b = g_virtual_fg_color_rgb.b
    lblActiveColor.setStyleSheet(f"background-color: rgb({b}, {g}, {r})")

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
        global g_auto_mix_paused
        global g_color_changed_from_selector_probably
        global g_auto_mix_paused
        global g_auto_mix_enabled
        global g_top_layer_is_dirty
        global g_virtual_fg_color_rgb
        global g_color_changed_from_selector_probably
        global g_virtual_color_used_last_rgb
        global g_dirty_brush_currently_on
        global g_dirty_brush_overall_enabled
        global g_color_on_down_dirty_brush
        global g_auto_mixing_just_once_now_on
        global g_auto_mixing_just_once_logic
        global g_auto_dry_each_stroke
        global g_last_coord_mouse_up
        global g_last_coord_mouse_down
        
        
        # if event.type() == QEvent.HoverEnter:
            # print(f"hover ")
        if event.type() == QEvent.Enter:
            #print(f"enter")
            # if obj.objectName() == "ColorSelectorNg":
                # print(f"enter color selector ")
            
            # if isinstance(obj, QDockWidget):
                # print(f"enter dock widget {obj.objectName()} ")
                        
            #if obj.type() == QMdiSubWindow:
            if isinstance(obj, QMdiSubWindow):
                print(f"enter subwindow")
                
                wi = Krita.instance().activeWindow()
                q_win = wi.qwindow()
                mdi_area = q_win.findChild(QMdiArea)
                mdi_area.setActiveSubWindow(obj)
                
                
                subwin = obj
                isAlwaysOnTop = True if subwin.windowFlags() & Qt.WindowStaysOnTopHint else False
                
                
                
                
                
                
                
                
                
                
                
                # if the color has just been changed manually, create a new layer
            
                
                if g_color_changed_from_selector_probably:
                    if g_virtual_fg_color_rgb.equals(g_virtual_color_used_last_rgb):
                        l_color_changed_from_selector = False
                    else:
                        l_color_changed_from_selector = True
                else:
                    l_color_changed_from_selector = False
                    
                    
                #print ("debug 1")
                if not isAlwaysOnTop and  l_color_changed_from_selector and (not g_auto_mix_enabled or g_auto_mix_paused) and g_top_layer_is_dirty  and g_multi_layer_mode:
                
                        #print ("debug 2 creating layer")
                        newLa = dryPaper(False)
                        
                        
                        # reenable dirty brush
                        global g_dirty_brush_currently_on
                        global g_dirty_brush_overall_enabled
                        
                        if g_dirty_brush_overall_enabled:
                            g_dirty_brush_currently_on = True
                        
                        
                        
                        
                        #devo anche resettare opacità di default
                       
                        global g_auto_reset_opacity_on_pick_level
                        global g_auto_reset_opacity_on_pick
            
                        
                
                
                
                        document = Krita.instance().activeDocument()
                        if g_auto_reset_opacity_on_pick == 1 and  document is not None :
                            newLa.setOpacity(g_auto_reset_opacity_on_pick_level * 255.0 / 100.0) 
                    
                            document.refreshProjection()
            
            
            
                        g_color_changed_from_selector_probably = False
                
                
                if g_auto_mix_paused and not isAlwaysOnTop: #if I am entering a window that is not always on top (the part "and not isalwaysontop" is there to attemp to fix a bug: auto-mix sometimes stops pausing when you hover the color picker)
                    g_auto_mix_paused = False
                    
                
                #obj.activateWindow()
                
        
        
        if event.type() == QEvent.Leave:
            #print(f"leave")
            
            # logic: if the mouse leaver an always-on-top window, focus the first window that's not always on top. 
            # print(f"leave event ")
            if isinstance(obj, QMdiSubWindow):
                #print(f"leave {obj} ")
                
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
                else:
                    # mouse left a normal window. possibly it entered the color picker. So pause automixing, so you can use the picker
                    
                    if g_auto_mix_enabled:
                        g_auto_mix_paused = True
                        #print("pausing automix")
                        resetForegroundColorToLastColorPicked()
                    else:
                        pass
                        #print("leave, doing nothing, auto mix disabled")
                
        # if event.type() == QEvent.MouseMove:
            # print (f"mousemove")
            # #col = getColorUnderCursorOrAtPos()
            
        # if event.type() == QEvent.HoverMove:
            # print (f"hover mousemove")
            # #col = getColorUnderCursorOrAtPos()
                
        # if event.type() == QEvent.GraphicsSceneMouseMove:
            # print (f"GraphicsSceneMouseMove")
            # #col = getColorUnderCursorOrAtPos()
        
        # if event.type() == QEvent.GraphicsSceneHoverMove:
            # print (f"GraphicsSceneHoverMove")
            # #col = getColorUnderCursorOrAtPos()
            
        
        
        if event.type() == QEvent.MouseButtonRelease:
            
            
            global g_picking_color
            global g_mixing_color
            global g_last_coord_mouse_down
            
            
            if g_mixing_color:
            
                if g_multi_layer_mode:
                    # TODO dovrei cancellare il precedente layer, non il corrente. perché è un errore
                    mixFgColorWithBgColor_normalLogic( createLayer = False, deleteCurLayer = True, clearCurLayer = False)
                    
                else:
                    mixFgColorWithBgColor_normalLogic( createLayer = False, deleteCurLayer = True, clearCurLayer = False)
                g_mixing_color = False
                global g_btn_mix
                g_btn_mix.setChecked(False)
                
                return True # annulla l'evento, ma non funziona
            elif g_picking_color:
                # clear layer first, otherwise I pick the color just painted
                app = Krita.instance()
                
                
                # now,  pick color ignoring stroke just made (which is on its own layer)
                col = getColorUnderCursorOrAtPos(forcedPos = xyOfQpoint(g_last_coord_mouse_down ), skipCurrentLayer = True) 
                setFgColor(col)
                g_virtual_fg_color_rgb  = col
                g_picking_color = False
                
                
                # now I have to delete the stroke just made. normally I would just clear the layer. But if I'm in single layer mode I need to DELETE the layer
                if g_multi_layer_mode:  # altrimenti non ho creato un nuovo layer
                    app.action('clear').trigger()
                    app.activeDocument().waitForDone () # action needs to finish before continuing  
                else:
                    app.activeDocument().activeNode().remove()
                    
                    
                
                global g_btn_pick_color
                g_btn_pick_color.setChecked(False)
                
                
                # todo update layer opacity
                
                
                
                # set color label
                update_label_from_virtual_color()
                
                #lblActiveColor.setStyleSheet("background-color: blue")
                
                return True # annulla l'evento, ma non funziona
                
                
            
            g_last_coord_mouse_up = get_cursor_in_document_coords()
            
            # print(f"mouse buttonreleased. {g_last_coord_mouse_up}")
            if g_auto_dry_each_stroke and g_multi_layer_mode:
                newLa = dryPaper(showMessage = False)
            
            
            
                
            # uncomment this to have dirty brush ===============
            
            if g_dirty_brush_currently_on and g_dirty_brush_overall_enabled:
                application = Krita.instance()
                win = application.activeWindow()
                if win is not None:
                    view = win.activeView()
                    if  view is not None:
                    
                    
                        global g_virtual_fg_color_rgb_previous_when_dirty_brush_on
                        g_virtual_fg_color_rgb_previous_when_dirty_brush_on = g_virtual_fg_color_rgb.clone()
                        
                        
                        
                        
                        fg = view.foregroundColor() #tipo ManagedColor, valori da 0 a 1
                            # print(f"fg  = {fg}")
                            
                        # fg2 = rgbOfManagedColor(fg) # valori da 0 a 255
                        
                        # global g_virtual_fg_color_rgb
                        # g_virtual_fg_color_rgb = fg2
                        
                        # non riesco aprendere il colore precedente
                        #bgColor = getColorUnderCursorOrAtPos(True) # skippo current layer altrimenti prende il fg attuale
                        
                        # average between color when mouse down and color when mouse up
                        
                        bgColorAverage =  g_color_on_down_dirty_brush # bgColor.average( g_color_on_down_dirty_brush)
                        
                        
                        
                        comp = fg.components() 
                        
                        canv = 0.12 # 0.18 troppo difficile fare contorni scuri
                    
                        fgMul = 1.0 - canv
                        comp[0] = comp[0] * fgMul + (bgColorAverage.r / 255.0)  * canv
                        comp[1] = comp[1] * fgMul + (bgColorAverage.g / 255.0)  * canv
                        comp[2] = comp[2] * fgMul + (bgColorAverage.b  / 255.0)  * canv
                        
                    
                        
                        fg.setComponents(comp)
                        
                        view.setForeGroundColor(fg)
                        
               
                        
                        g_virtual_fg_color_rgb = rgb( int  (comp[0] * 255.0), int  (comp[1] * 255.0), int  (comp[2] * 255.0), 1)
                        update_label_from_virtual_color()
                            
                            
                            
                        print (f"dirty brush: adding a bit of {bgColorAverage.toString()} setting {g_virtual_fg_color_rgb.toString()}")
        
        
        if event.type() == QEvent.MouseButtonPress:
            # print("mouse buttonpress")
            
                
                # col = getColorUnderCursorOrAtPos()
                # setFgColor(col)
                # g_picking_color = False
                # return True # annulla l'evento
            
            
            g_last_coord_mouse_down = get_cursor_in_document_coords()
            
            
            if g_auto_mixing_just_once_logic:
                g_auto_mixing_just_once_now_on = False
            
            
            if g_dirty_brush_currently_on and g_dirty_brush_overall_enabled:
                application = Krita.instance()
                win = application.activeWindow()
                if win is not None:
                    view = win.activeView()
                    if  view is not None:
                        fg = view.foregroundColor() #tipo ManagedColor, valori da 0 a 1
                            # print(f"fg  = {fg}")
                            
                        # fg2 = rgbOfManagedColor(fg) # valori da 0 a 255
                        
                        # global g_virtual_fg_color_rgb
                        # g_virtual_fg_color_rgb = fg2
                        
                        
                        
                
                        # if g_dirty_brush_currently_on :
                                                            
                                # currentDoc = application.activeDocument()
                                # if currentDoc is not None:
                                    # application.action('clear').trigger()
                                    # currentDoc.waitForDone () # action needs to finish before continuing
                                
                
                        
                        # in theory I should skip current layer because  I am deciding the correct color, so the color on the current layer is incorrect. but I can also try the other logic because then you can drag around color without getting dirty. 
                        # kind of like auto-mixing with 100 background pick.
                        g_color_on_down_dirty_brush = getColorUnderCursorOrAtPos( skipCurrentLayer = False)
                        
                        
            # uncomment this to have dirty brush ===============
                
            
            pass
            
            # global g_opacity_decided_for_layer
            # if not g_opacity_decided_for_layer:
                # bgColor = getColorUnderCursorOrAtPosExceptCurrentLayer()
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
                            # global g_virtual_fg_color_rgb
                            # g_virtual_fg_color_rgb = rgb( int  (comp[0] * 255.0), int  (comp[1] * 255.0), int  (comp[2] * 255.0), 1)
                            
                            
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
                        
                    
                
            #col = getColorUnderCursorOrAtPos()
        
        return False # non scarta l'evento
        
        
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

def setFgColor(col):
    app = Krita.instance()
    win = app.activeWindow()
    if win is not None:
            view = win.activeView()
            if view is not None:
                fg = view.foregroundColor() 
                comp = fg.components() 
                # print(f"fg color = {comp}")
                     
                     
                
                comp[0] = (col.r/255.0) 
                comp[1] = (col.g / 255.0)
                comp[2] = (col.b / 255.0) 
                
                fg.setComponents(comp)
                
                view.setForeGroundColor(fg)

def QPointHash(qp):
    return f"{qp.x()}-{qp.y()}"

def setFgColorEqualToColorOfLastStrokeAfterOpacityAdjust():
    global g_last_coord_mouse_up
    if g_last_coord_mouse_up is None:
        print("error g_last_coord_mouse_up is none")
        
    else:
        fr = queue.Queue(0) # maxsize = means infinite
        
        fr.put(xyOfQpoint( g_last_coord_mouse_up))
        visited = {}
        count = 0
        foundColors = []
        
        
        while True:
            curPos = fr.get()
            hashCurPos = curPos.toString()
            
            if hashCurPos in visited :
                continue
                
            visited[hashCurPos] = 1
            
            col = getColorUnderCursorOrAtPos(forcedPos = curPos, pretendLastLayerIsFgColor = True)
            
            colExcludingLast = getColorUnderCursorOrAtPos(forcedPos = curPos, skipCurrentLayer = True)
            
            if not col.equals(colExcludingLast):
                # print(f"found color at {curPos}. color is {col.toString()}, col excluding curlayer is {colExcludingLast.toString()}")
                foundColors.append(col)


            
            
            
            # se ho trovato 8 colori, faccio la media ed esco. TODO prendere invece il più numeroso
            if len(foundColors) == 8:
                media  = foundColors[0]
                for  m in foundColors:
                        media = m.average(media)
                col = media
                break
            
            
            
            # cerchiamo anche intorno. espando frontiera
            st = 2
            
            
            fr.put(xy(curPos.x + st, curPos.y))
            fr.put(xy(curPos.x - st, curPos.y))
            fr.put(xy(curPos.x , curPos.y- st))
            fr.put(xy(curPos.x , curPos.y + st))
            
            
            
            
            # se dopo un po' non sono riuscito, termino
            count += 1
            
            if count > 2500:
                print("esco dal loop senza successo")
                quickMessage("errore, colore non trovato")
                break
            

        setFgColor(col)
        
        
        
        newLa = dryPaper(False)
        
        newLa.setOpacity(g_auto_reset_opacity_on_pick_level * 255.0 / 100.0) 
                        
        application = Krita.instance()
        currentDoc = application.activeDocument()
        if currentDoc is not None:
            currentDoc.refreshProjection()
                        
        
    
def resetForegroundColorToLastColorPicked():
                global g_virtual_fg_color_rgb
                if g_virtual_fg_color_rgb is not None:
                    setFgColor(g_virtual_fg_color_rgb)
                    
                    # app = Krita.instance()
                    # win = app.activeWindow()
                    # if win is not None:
                            # view = win.activeView()
                            # if view is not None:
                                # fg = view.foregroundColor() 
                                # comp = fg.components() 
                                # # print(f"fg color = {comp}")
                                     
                                     
                                
                                # comp[0] = (g_virtual_fg_color_rgb.r/255.0) 
                                # comp[1] = (g_virtual_fg_color_rgb.g / 255.0)
                                # comp[2] = (g_virtual_fg_color_rgb.b / 255.0) 
                                
                                # fg.setComponents(comp)
                                
                                # view.setForeGroundColor(fg)
                                # #print(f"color reset to {g_virtual_fg_color_rgb.toString()}")
        
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



def quickMessage(msg, timeMessage = 360):
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

        def clone(self):
            return rgb(self.r, self.g, self.b, self.a)
        
class xy:
        def __init__(self, x,y):
                self.x = x
                self.y = y
        
        def toString(self):
            return f"{self.x}-{self.y}"
            
def xyOfQpoint(q):
            return xy( int(round(q.x())),  int(round(q.y())))
            
        # def print(self, msg):
                # print(f"{msg}:   r:{self.r}, g:{self.g}, b:{self.b} ,a:{self.a}")



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

def mixFgColorWithBgColor_normalLogic( createLayer = False, clearCurLayer = False, deleteCurLayer = False):
                global g_temp_switched_to_100_previous_opac
                app = Krita.instance()
                win = app.activeWindow()
                if win is not None:
                        view = win.activeView()
                        if view is not None:
                                document = view.document()
                                if document:
                                        center = QPointF(0.5 * document.width(), 0.5 * document.height())
                                        p = get_cursor_in_document_coords()
                                        
                                        doc_pos = p + center # float
                                        print(f'cursor at: x={doc_pos.x()}, y={doc_pos.y()}')
                                        
                                        
                                        parentNode = document.activeNode().parentNode()
                                        
                                        
                                        if parentNode is not None:
                                        
                                                brothers = parentNode.childNodes()
                                                colors = []
                                                
                                                # I build colors[]
                                                for curLayer in brothers:
                                                    # If this is the current layer and it is transparent, I skip this layer, because I only want to pick from layers below it.  Why? Because you typically use the mix shortcut when the stroke you just made is wrong, and it needs to be more similar to the background layer. But then, you want to be able to click on the stroke you just did and pick the color BELOW it. 
                                                    # the exception is if I've switched to single-layer mode, aka temp_switched_to_100_previous_opac
                                                    if curLayer.uniqueId() != document.activeNode().uniqueId() or curLayer.opacity() == 255 or g_temp_switched_to_100_previous_opac is not None: 
                                                    
                                                        pixelBytes = curLayer.pixelData( int(round(doc_pos.x())), int(round(doc_pos.y())), 1, 1)
                                                        
                                                        imageData = QImage(pixelBytes, 1, 1, QImage.Format_RGBA8888)
                                                        pixelC = imageData.pixelColor(0,0)
                                                        
                                                        # if this is the current layer and it is trasparent, this means you are mixing from a stroke you just did. Then consider it not transparent. So the next stroke will be almost identical to the previous stroke
                                                        if curLayer.uniqueId() == document.activeNode().uniqueId():
                                                            correzMul = 1.0
                                                        else:
                                                            layerOpac = curLayer.opacity() # between 0 and 255
                                                            correzMul = float(layerOpac) /  255.0
                                                    

                                                        #print(f"color under cursor =  r:{self.pixelC.red()}, g:{self.pixelC.green()}, b:{self.pixelC.blue()} ,a:{self.pixelC.alpha() }, a corretto = {self.pixelC.alpha() * correzMul}")
                                                        
                                                        colors.append(  rgb(pixelC.red(),  pixelC.green(),  pixelC.blue(),  pixelC.alpha() * correzMul ))
                                                
                                                
                                                if len(colors) == 0: # there was only the fg layer
                                                    quickMessage(f"Cannot mix: could not find background layers to pick from. ")
                                                else:
                                                    #creo il colore composito dei layer. questo è il bgcolor                                                
                                                    bgColor = calcolaCompositeColor(colors)
                                                    bgColor.print("bgColor")
                                                                    
                                                    
                                                    fg = view.foregroundColor() 
                                                    comp = fg.components() 
                                                    
                                                    if len(comp ) == 4:    
                                                        global g_how_much_canvas_to_pick
                                                        canv = g_how_much_canvas_to_pick
                                                        
                                                        
                                                        # BEGIN mix color the old way (non spectral) 
                                                        
                                                        # fgMul = 1.0 - canv
                                                        # comp[0] = comp[0] * fgMul + (bgColor.r / 255.0)  * canv
                                                        # comp[1] = comp[1] * fgMul + (bgColor.g / 255.0)  * canv
                                                        # comp[2] = comp[2] * fgMul + (bgColor.b  / 255.0)  * canv
                                                        # end
                                                    
                                                    
                                                        #begin mix colors spectral, bgr
                                                        fgMul = 1.0 - canv
                                                        sb = comp[0] 
                                                        sg = comp[1]
                                                        sr = comp[2]
                                                        
                                                       
                                                        db = bgColor.r / 255.0
                                                        dg = bgColor.g / 255.0
                                                        dr = bgColor.b / 255.0
                                                       
                                                       
                                                        resultColor = mixRGB(sr, sg, sb, fgMul, dr, dg, db)
                                                        # resultColor is [r,g,b]. copy back to bgr:
                                                        
                                                        comp[0] = resultColor[2]
                                                        comp[1] = resultColor[1]
                                                        comp[2] = resultColor[0]
                                                        
                                                        # END
                                                  
                                                  
                                                        # begin mix colors spectral, rgb
                                                        # fgMul = 1.0 - canv
                                                        # sr = comp[0] 
                                                        # sg = comp[1]
                                                        # sb = comp[2]
                                                        
                                                       
                                                        # dr = bgColor.r / 255.0
                                                        # dg = bgColor.g / 255.0
                                                        # db = bgColor.b / 255.0
                                                       
                                                       
                                                        # resultColor = mixRGB(sr, sg, sb, fgMul, dr, dg, db)
                                                        
                                                        # comp[0] = resultColor[0]
                                                        # comp[1] = resultColor[1]
                                                        # comp[2] = resultColor[2]
                                                        
                                                        # END
                                                  
                                                        fg.setComponents(comp)
                                                        
                                                        view.setForeGroundColor(fg)
                                                        
                                                        
                                                        # setto anche il virtual fg color al result del mix
                                                        global g_virtual_fg_color_rgb
                                                        g_virtual_fg_color_rgb = rgb( int  (comp[0] * 255.0), int  (comp[1] * 255.0), int  (comp[2] * 255.0), 1)
                                                        update_label_from_virtual_color()
                                                        
                                                        
                                                        quickMessage(f"Picked {round(canv * 100)}%  color from the canvas.")
                                                        
                                                        # 1) if I mixed because the color is wrong, i.e. I made a mistake, then erase the mistake                                                        
                                                        if clearCurLayer :
                                                        
                                                            if g_multi_layer_mode:
                                                            
                                                                    app.action('clear').trigger()
                                                                    document.waitForDone () # action needs to finish before continuing
                                                            
                                                            
                                                        if deleteCurLayer:
                                                                document.activeNode().remove()
                                                                    
                                                                    
                                                        # 2) if I didn't make a mistake, I just want to fade the current color, then create a new layer
                                                        if createLayer and g_multi_layer_mode:
                                                            if  g_temp_switched_to_100_previous_opac is None: # I don't want to add a layer if I'm picking from the mixing palette, or if I've switched to 100 percent opacity mode
                                                                newLa = dryPaper(showMessage = False)
                                                                
                                                                # if active layer opacity < 70, set to 70
                                                                global g_auto_reset_opacity_on_pick
                                                                if g_auto_reset_opacity_on_pick == 1 and  document is not None :
                                                                    newLa.setOpacity(g_auto_reset_opacity_on_pick_level * 255.0 / 100.0) 
                                                                    
                                                                    document.refreshProjection()
                                                            
                                                            
                                                        # messaggio
                                                        
                                                        
                                                    elif len(comp ) == 2:
                                                        messageBox(" Your foreground color is currently grayscale. In order to use \"Mix\", please set your foreground color to an RGB color first.")
                                                    else:
                                                        messageBox("In order to use \"Mix\", please set your foreground color to an RGB color first.")
            
        
        
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
    
    
    
# def onTimerDebug():
        # application = Krita.instance()
        # # currentDoc = application.activeDocument()
        # # if currentDoc is not None:
            # # print(f"x offset: {currentDoc.xOffset()}")
            
            
        # wi = Krita.instance().activeWindow()
        # subwins = wi.qwindow().findChild(QMdiArea).subWindowList()
        
        
        # # fullPaths = []
        # # for wi in Krita.instance().windows():
            # # print(f"wi = {wi}  title = {wi.qwindow().windowTitle()}")
            # # for vi in wi.views():
                # # print(f"view filename {vi.document().fileName()}")
                # # fullPaths.append(vi.document().fileName())
        
        
        
        # windows = []
        # for su in subwins:
        
            # print(f"parent = {su.parent()}, par par = {su.parent().parent()}")
            # tit = su.windowTitle().replace(" *", "")
            
            # #path = [ fp for fp in fullPaths if fp.endswith(tit) ] [0]
            # print(f"window {tit}, position {su.pos()}")
            # newWin = Window()
            # newWin.x = su.pos().x()
            # newWin.y = su.pos().y()
            # newWin.wt = su.size().width()
            # newWin.ht = su.size().height()
            # #newWin.fullPath = path
            # newWin.title = tit
            # newWin.isMaximized = True if su.windowState() & Qt.WindowMaximized else False
            # newWin.isMinimized = True if su.windowState() & Qt.WindowMinimized else False
            # newWin.isAlwaysOnTop = True if su.windowFlags() & Qt.WindowStaysOnTopHint else False
            # windows.append(newWin)
        
        
        # js = json.dumps([ w.__dict__ for w in windows] )
            
            
            
            
        #print(f"dump json = {js}")

class MyExtension(Extension):

        def __init__(self, parent):  # bm_init
                # This is initialising the parent, always important when subclassing.
                super().__init__(parent)
                
                self.inited = False
                
                self.counter = 0
                
                self.qdock = QDockWidget()
                
                
                global g_multi_layer_mode
                multi_layer_mode_str = Krita.instance().readSetting("colorPlus", "g_multi_layer_mode","1")                
                g_multi_layer_mode = multi_layer_mode_str == "1"
                
                
                global g_auto_reset_opacity_on_pick_level 
                
                g_auto_reset_opacity_on_pick_level = float(Krita.instance().readSetting("colorPlus", "g_auto_reset_opacity_on_pick_level","68.0"))
                
                
                # global g_mix_auto_clears_cur_layer
                # g_mix_auto_clears_cur_layer = Krita.instance().readSetting("colorPlus", "g_mix_auto_clears_cur_layer","1")
                
                global g_auto_mix__how_much_canvas_to_pick
                g_auto_mix__how_much_canvas_to_pick = float(Krita.instance().readSetting("colorPlus", "g_auto_mix__how_much_canvas_to_pick","0.5"))
                
                
                
                
                global g_auto_mixing_target_distance
                g_auto_mixing_target_distance = float(Krita.instance().readSetting("colorPlus", "g_auto_mixing_target_distance","40.0"))
                
                
                global g_auto_reset_opacity_on_pick
                
                g_auto_reset_opacity_on_pick = int(Krita.instance().readSetting("colorPlus", "g_auto_reset_opacity_on_pick","0"))
                
                strHowMuch = Krita.instance().readSetting("colorPlus", "g_how_much_canvas_to_pick","0.45")
                global g_how_much_canvas_to_pick
                g_how_much_canvas_to_pick = float(strHowMuch)
                
                global g_auto_opacity_max_distance
                g_auto_opacity_max_distance = int(Krita.instance().readSetting("colorPlus", "g_auto_opacity_max_distance","40"))
                
                # dev values , only read when timer is active
                global g_virtual_fg_color_rgb
                g_virtual_fg_color_rgb = None # di tipo rgb
                
                
                
                
                self.g_auto_focus = Krita.instance().readSetting("colorPlus", "g_auto_focus", "true")
                
                
                self.mix_radius = 1 # pixel
                
                global g_temp_switched_to_100_previous_opac
                g_temp_switched_to_100_previous_opac = None
                
                global g_temp_switched_to_25_previous_opac
                g_temp_switched_to_25_previous_opac = None
                
                self.mixing_target_distance = 20.0
                
                self.correct_color_for_transparency = True
                
                
                
                # self.timerDebug = QTimer()
                # self.timerDebug.timeout.connect(onTimerDebug)
                # self.timerDebug.start(2000)
                
                
                #creo il timer per il mixing
                self.timerMixon = QTimer()
                self.timerMixon.timeout.connect(self.mixOnTimer)
                self.timerMixon.start(40)
                
                
                #creo il timer 
                # self.timerEnumRes = QTimer()
                # self.timerEnumRes.timeout.connect(self.enumResources)
                # self.timerEnumRes.start(2000)
                
                
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
                Krita.instance().notifier().viewCreated.connect(self.onViewOpenedEvent)
                Krita.instance().notifier().imageCreated.connect(self.onDocCreated)
                
                
                self.timer = QTimer()
                self.timer.timeout.connect(self.updateAutoFocus)
                self.timer.start(1000)
                
                
                Application.addDockWidgetFactory(DockWidgetFactory("hello", DockWidgetFactoryBase.DockRight, HelloDocker))
                
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
            global allBrushPresets
            allBrushPresets = Krita.instance().resources('paintoppresets')
            # for k,v in allBrushPresets.items():
                # print (f"key {k}")
                
            #openedView.updateAutoFocus()

        def onDocCreated(openedDoc):
            
            print(f"doc created{openedDoc}");
            global allBrushPresets
            allBrushPresets = Krita.instance().resources('paintoppresets')
            #print(f"all brush presets = {allBrushPresets.size()}")
                
            #openedView.updateAutoFocus()

        
        def onFgColorChanged(self):
            # this is fired several times when the user changes a color via the color selector. So I can't add a layer here, because I would add hundreds of layers. So I don't do anything, but mark it dirty via g_color_changed_from_selector_probably.
            global g_color_changed_from_selector_probably
            
            global g_virtual_color_used_last_rgb
            
            
            
            #capisci se è davvero cambiato, dato che questa callback è inaffidabile e viene chiamata anche se entro ed esco dal selector senza cliccare
            g_color_changed_from_selector_probably = True
            # if g_color_used_last_array is not None:
                # view  = Krita.instance().activeWindow().activeView()
                # if view is not None:
                    # fg = view.foregroundColor()
                    # if fg is not None:
                        # comp = fg.components() 
                        # if comp is not None:
                            # #if listEqual(comp, g_color_used_last_array):  # non funziona con automix
                            
                            # fgCol = rgb( int  (comp[0] * 255.0), int  (comp[1] * 255.0), int  (comp[2] * 255.0), 1)
                            # if fgCol.equals(g_virtual_color_used_last_rgb):
                                # print("current color is same")
                                # pass
                            # else:
                                
                
                
            
            global countColorChanged
            #print(f"fg color changed event: {countColorChanged}")
            
            countColorChanged += 1
            
            
            
            
            
            global g_auto_mix_enabled
            global g_auto_mix_paused
            global g_last_virtual_colors_used
            global g_virtual_fg_color_rgb
            global g_virtual_color_used_last_rgb
            
            if not g_auto_mix_enabled or g_auto_mix_paused:  # otherwise it is the auto-mixing timer that changed the color. ignore
                
                # the color has been changed manually, not by auto-mix                
                    
                # devo settare questo colore come target per l'auto-mixing
                view  = Krita.instance().activeWindow().activeView()
                if view is not None:
                    fg = view.foregroundColor()
                    if fg is not None:
                        comp = fg.components() 
                        
                        if len(comp) == 4:
                            
                            mergedColor = rgb(comp[0] * 255.0, comp[1] * 255.0, comp[2] * 255.0, 255)
                                

                            
                            g_virtual_fg_color_rgb = mergedColor #lo memorizzo
                            
                            update_label_from_virtual_color()
                            
                            
                            #print(f"setting last_color_picked = {g_virtual_fg_color_rgb.toString()}")
                        else:
                            print("err1")
                    else:
                        print ("err2")
            
                    
            else:
                    
                    pass # color changed by auto-mix
                    
                    #print(f"fg color changed event ignored. paused = {g_auto_mix_paused}")
                    
            
            
            
            
            

        def onWindowCreated(self): #called by framework
                print("on window created  ")
                

                # self.currentColor = [255,255,255,0]
                # self.previousColor = [255,255,20,0]
                # self.inited = False
                                
                app = Krita.instance()
                history_docker = next((d for d in app.dockers() if d.objectName() == 'History'), None)
                kis_undo_view = next((v for v in history_docker.findChildren(QListView) if v.metaObject().className() == 'KisUndoView'), None)
                s_model = kis_undo_view.selectionModel()
                s_model.currentChanged.connect(self._on_history_was_made)
                
                
                
                
                # start listening to color changes via color selector
                colorSelectorNg = next((d for d  in app.dockers() if d.objectName() == 'ColorSelectorNg'), None)
                for child in colorSelectorNg.findChildren(QObject):
                    meta = child.metaObject()
                    if meta.className() in {
                                'KisColorSelectorRing', 'KisColorSelectorTriangle',
                                'KisColorSelectorSimple', 'KisColorSelectorWheel'}:
                        sig = getattr(child, 'update')
                        sig.connect(self.onFgColorChanged)
                    
                
                
                
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
                global g_temp_switched_to_100_previous_opac
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
                                global g_virtual_fg_color_rgb
                                global g_last_virtual_colors_used
                                
                                
                                # scambio gli ultimi due delle'elenco
                                if len(g_last_virtual_colors_used) > 1:
                                    temp = g_last_virtual_colors_used[-1].clone()
                                    g_last_virtual_colors_used[-1] = g_last_virtual_colors_used[-2] .clone()
                                    g_last_virtual_colors_used[-2] = temp.clone()
                                
                                
                                # il virtuale diventa l'ultimo
                                g_virtual_fg_color_rgb = g_last_virtual_colors_used[-1].clone()
                                update_label_from_virtual_color()
                                
                                # il fisico diventa il virtuale

                                col = acView.foregroundColor()
                                comp = col.components()
                                
                                comp[0] =  (g_virtual_fg_color_rgb.r / 255.0)  
                                comp[1] =  (g_virtual_fg_color_rgb.g / 255.0)
                                comp[2] = (g_virtual_fg_color_rgb.b  / 255.0)
                          
                                col.setComponents(comp)
                                acView.setForeGroundColor(col)
                                
                             
                                
                                
                             
                                    
                                    
                                acView.showFloatingMessage("Last color", QIcon(), timeMessage , 1)
                                
                                
                                
                                # I also want to create a new layer, to have the overlay effect
                                global g_auto_reset_opacity_on_pick
                                
                                document = acView.document()
                                if document is not None:
                                
                                    parentNode = document.activeNode().parentNode() # could be root node, so I need to do parent again
                                        
                                        
                                    if parentNode is not None:
                                        
                                        if  g_temp_switched_to_100_previous_opac is None and g_multi_layer_mode: # I don't want to add a layer if I'm picking from the mixing palette, or if I've switched to 100 percent opacity mode
                                            newLa = dryPaper(showMessage = False)
                                            
                                            
                                                                    
                                            if g_auto_reset_opacity_on_pick == 1 :
                                                newLa.setOpacity(g_auto_reset_opacity_on_pick_level * 255.0 / 100.0) 
                                                
                                                document.refreshProjection()
                                                
                                            

                                        
                                        
                except Exception as e:
                                acView.showFloatingMessage(f"error {e}.", QIcon(), timeMessage * 2, 1)
                                print("errore trovato in swap:")
                                print(e)
                                
                                


        def toggle_100_opac(self):
            global g_temp_switched_to_100_previous_opac
            global g_temp_switched_to_25_previous_opac
            application = Krita.instance()
            currentDoc = application.activeDocument()
            if currentDoc is not None:
                activeLayer = currentDoc.activeNode()
                curOpac = activeLayer.opacity()
                
                if g_temp_switched_to_100_previous_opac is None:
                    newLa = dryPaper(False)
                    
                    activeLayer = newLa
                    # currentDoc = application.activeDocument()
                    # currentDoc.waitForDone()
                    # activeLayer = currentDoc.activeNode()
                    
                    if g_temp_switched_to_25_previous_opac is not None:
                        g_temp_switched_to_100_previous_opac = g_temp_switched_to_25_previous_opac
                        g_temp_switched_to_25_previous_opac = None
                    else:
                        g_temp_switched_to_100_previous_opac = activeLayer.opacity()
                        
                    
                    activeLayer.setOpacity(255)
                    
                    
                    # the brush opacity becomes equal to the layer opacityfg = view.foregroundColor()
                    
                    # view  = Krita.instance().activeWindow().activeView()
                    
                    # newPaintingOp = self.temp_switched_to_100_previous_opac / 255.0
                    # print(f"setting new painting op = {newPaintingOp}")
                    # view.setPaintingOpacity(newPaintingOp)
                    
                    
                    
                    quickMessage(f"Temporarily set 100% opacity. Press again to restore. debug. mix-paused = {g_auto_mix_paused}")
                else:
                    newLa = dryPaper(False)
                    
                    # currentDoc = application.activeDocument()
                    activeLayer = newLa #currentDoc.activeNode()
                    activeLayer.setOpacity(g_temp_switched_to_100_previous_opac)
                    
                    
                    quickMessage(f"Restored {round (g_temp_switched_to_100_previous_opac * 100.0 / 255.0)}  opacity. debug. mix-paused = {g_auto_mix_paused}")
                    
                    # view  = Krita.instance().activeWindow().activeView()
                    # view.setPaintingOpacity(1.0)
                    
                    g_temp_switched_to_100_previous_opac = None
        
        def toggle_25_opac(self):
            global g_temp_switched_to_100_previous_opac
            global g_temp_switched_to_25_previous_opac
            application = Krita.instance()
            currentDoc = application.activeDocument()
            if currentDoc is not None:
                activeLayer = currentDoc.activeNode()
                curOpac = activeLayer.opacity()
                
                if g_temp_switched_to_25_previous_opac is None:
                    activeLayer = dryPaper(False)
                    
                    if g_temp_switched_to_100_previous_opac is not None:
                        g_temp_switched_to_25_previous_opac = g_temp_switched_to_100_previous_opac
                        g_temp_switched_to_100_previous_opac = None
                    else:
                        g_temp_switched_to_25_previous_opac = activeLayer.opacity()
                    
                    activeLayer.setOpacity(25.0 * 255.0 / 100.0)
                    
                    
                    quickMessage(f"Temporarily set 25% opacity. Press again to restore.")
                else:
                    activeLayer = dryPaper(False)
                    activeLayer.setOpacity(g_temp_switched_to_25_previous_opac)
                    
                    
                    quickMessage(f"Restored {round (g_temp_switched_to_25_previous_opac * 100.0 / 255.0)}  opacity")
                    
                    g_temp_switched_to_25_previous_opac = None
                
                
            
        def _on_history_was_made(self):   #user painted,  _probably_
                
                # col = getColorUnderCursorOrAtPos()
                # if col is not None:
                    # print (f"user painted. counter = {self.counter}. col = {col.toString()}")
                
                                
                global g_top_layer_is_dirty
                g_top_layer_is_dirty = True
                
                
                
                self.counter +=  1
                
                try:
                        
                        acView = Krita.instance().activeWindow().activeView()
                        if acView is not None: 
                                col = acView.foregroundColor()
                                if col is not None:   
                                        comp = col.components()
                                        
                                        # ricorda con che colore ha scritto. ha appena scritto col virtuale
                                        global g_virtual_fg_color_rgb
                                        global g_last_virtual_colors_used
                                        
                                        # aggiungo alla lista solo se non è già in coda
                                        if g_virtual_fg_color_rgb is None:
                                            pass
                                        if len(g_last_virtual_colors_used) > 0:
                                            if g_last_virtual_colors_used[-1].equals(g_virtual_fg_color_rgb):
                                                pass
                                            else:
                                                g_last_virtual_colors_used.append(g_virtual_fg_color_rgb)
                                        else:
                                            g_last_virtual_colors_used.append(g_virtual_fg_color_rgb)
                                        
                                        
                                        
                                        # trim della lista
                                        if len(g_last_virtual_colors_used) > 5:
                                            g_last_virtual_colors_used = g_last_virtual_colors_used[-5:]
                                        
                                        global g_virtual_color_used_last_rgb
                                        

                                        # se ho auto mixing, is colore che davvero sto usando è quello virtuale, non quello reale nel fg color di krita, che è frutto di mixing.
                                        g_virtual_color_used_last_rgb = g_virtual_fg_color_rgb # rgb( int  (comp[0] * 255.0), int  (comp[1] * 255.0), int  (comp[2] * 255.0), 1)
                                        
                                        # if listEqual( comp, self.currentColor ):   # user did not change color. doesn't work with auto-mixing because colro is actually another
                                                 # pass
                                        # else:  # user changed color
                                                # # print("color changed")
                                                # self.previousColor = list.copy(self.currentColor) 
                                                # self.currentColor = list.copy(comp)
                                

                                        # print("user painted. lista attuale colori:------")
                                        # for x in g_last_virtual_colors_used:
                                            # print (x.toString())
                                        
                                        
                                        # print("------\n")
                                
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

                
        # Never used. this mixing logic makes sense when the current color is mostly correct, and you only want to introduce a small variation. In practice it is useless.
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
                                        
                                        #print(f'cursor at: x={doc_pos.x()}, y={doc_pos.y()}')
                                        
                                        
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
                                                        

                                                        #print(f"color under cursor =  r:{self.pixelC.red()}, g:{self.pixelC.green()}, b:{self.pixelC.blue()} ,a:{self.pixelC.alpha() }, a corretto = {self.pixelC.alpha() * correzMul}")
                                                        
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
                                                global g_virtual_fg_color_rgb
                                                g_virtual_fg_color_rgb = rgb( int  (comp[0] * 255.0), int  (comp[1] * 255.0), int  (comp[2] * 255.0), 1)
                                                update_label_from_virtual_color()
                                                
                                                
                                                # messaggio
                                                if picked50:
                                                    view.showFloatingMessage(f"Picked 50% because distance was small ({round(curDist)})", QIcon(), timeMessage, 1)
                                                else:
                                                    view.showFloatingMessage(f"Picked a bit of color from canvas. Distance: {round(curDist)}", QIcon(), timeMessage, 1)
        
        def acceptCurrentColorAndStopDirty(self, clearCurLayer = True):
            
                global g_temp_switched_to_100_previous_opac
                global g_dirty_brush_currently_on
                global g_dirty_brush_overall_enabled
                global g_virtual_fg_color_rgb_previous_when_dirty_brush_on
                
                if g_dirty_brush_overall_enabled:
                    g_dirty_brush_currently_on = False
                
                
                # reset previous color, because the dirty brush has already changed items
                if g_dirty_brush_overall_enabled:
                    setFgColor(g_virtual_fg_color_rgb_previous_when_dirty_brush_on)
                
                
                
                if clearCurLayer and  g_temp_switched_to_100_previous_opac is None:
                    app = Krita.instance()
                    win = app.activeWindow()
                    if win is not None:
                        view = win.activeView()
                        if view is not None:
                                document = view.document()
                                if document:
            
                                    app = Krita.instance()
                                    app.action('clear').trigger()
                                    document.waitForDone () # action needs to finish before continuing
                        
                quickMessage("Accept color and stop dirty brush")
                
        
        

        def updateColorUnderMouse(self):
            #print("updateColorUnderMouse")
            self.colorUnderMouse = getColorUnderCursorOrAtPos()
            # if col is not None:
                # print(f"update color under mouse: {col.toString()}")
            
        def enumResources(self):
            print("enum resources")
            #print( Krita.instance().resources('paintoppresets') )
            global allBrushPresets
            allBrushPresets = Krita.instance().resources('preset')
            print(f"resources: {allBrushPresets}")
            
            #allBrushPresets = Krita.instance().resources('paintoppresets')
            for k,v in allBrushPresets.items():
                print (f"key {k}")
            
            
        
                
                
        def mixOnTimer(self):
                global g_auto_mix_enabled
                # print("timer 1")
                global g_virtual_fg_color_rgb
                global g_auto_mix_paused
                
                if g_virtual_fg_color_rgb is None or not g_auto_mix_enabled  or g_auto_mix_paused or (g_auto_mixing_just_once_logic and not g_auto_mixing_just_once_now_on):
                        return
                        
                # print("timer 2")        
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
                                        
                                        doc_pos = xyOfQpoint(doc_pos)
                                        # print(f'cursor at: x={doc_pos.x()}, y={doc_pos.y()}')
                                        
                                        
                                        parentNode = document.activeNode().parentNode()
                                        
                                        
                                        if parentNode is not None:
                                        
                                                brothers = parentNode.childNodes()
                                                
                                                
                                                positions = [ xy( doc_pos.x, doc_pos.y)
                                                                                        
                                                                                                # , xy(doc_pos.x() + self.mix_radius, doc_pos.y() + self.mix_radius),
                                                                                                # xy(doc_pos.x() - self.mix_radius, doc_pos.y() + self.mix_radius),
                                                                                                # xy(doc_pos.x() + self.mix_radius, doc_pos.y() - self.mix_radius),
                                                                                                # xy(doc_pos.x() - self.mix_radius, doc_pos.y() - self.mix_radius) 
                                                                                                   ]
                                                                        





                                                                        
                                                merged_colors = [] # lista di rgb, uno per posizione. ognuno è il risultato di un merge di ogni layer, in quella data posizione
                                                
                                                                                         
                                                
                                                
                                                # pos =  xy(doc_pos.x(), doc_pos.y())
                                                
                                                
                                                
                                                for pos in positions:
                                                
                                                    #costruisco colors  , uno per layer                                              
                                                    colors = []
                                                    for curLayer in brothers:
                                                        
                                                        
                                                        # important choice: skip the fg layer or not? I f you don't skip the curent layer, if you click on the previous stroke it adds to it. The problem is that you can drag the color along.
                                                        #if curLayer.uniqueId() != document.activeNode().uniqueId() : 
                                                            
                                                            self.pixelBytes = curLayer.pixelData(pos.x, pos.y, 1, 1)
                                                            
                                                            self.imageData = QImage(self.pixelBytes, 1, 1, QImage.Format_RGBA8888)
                                                            self.pixelC = self.imageData.pixelColor(0,0)
                                                        
                                                            #devo correggere l'alpha del pixel con l'alpha del layer. ma non lo correggo se il layer è quello attuale, che è trasparente. così la pennellata successiva si vede uguale
                                                            # if curLayer.uniqueId() == document.activeNode().uniqueId():
                                                                # correzMul = 1.0
                                                            # else:
                                                            layerOpac = curLayer.opacity() # tra  0 e 255
                                                            correzMul = float(layerOpac) /  255.0
                                                                                                                    
                                                            
                                                            #print(f"color under cursor =  r:{self.pixelC.red()}, g:{self.pixelC.green()}, b:{self.pixelC.blue()} ,a:{self.pixelC.alpha()}")
                                                            
                                                            colors.append(  rgb(self.pixelC.red(),  self.pixelC.green(),  self.pixelC.blue(),  self.pixelC.alpha()  * correzMul))
                                                    
                                                    mergedColorOfAllLayers = calcolaCompositeColor(colors); # tipo rgb
                                                    merged_colors.append(mergedColorOfAllLayers)



                                                #creo il colore composito tra tutte le posizioni
                                                # faccio la media di tutti i merged colors
                                            
                                                media  = merged_colors[0]
                                                for  m in merged_colors:
                                                        media = m.average(media)
                                                        
                                                mergedColor = media
                                                                
                                                                
                                                                
                                                                
                                                                
                                                                
                                                # setto il fg color uguale a merged color mischiato con il memorizzato (non con il fg)
                                                
                                                fg = view.foregroundColor() 
                                                comp = fg.components() 
                                                
                                                #global g_auto_mix_snap_distance
                                                global g_auto_mixing_uses_distance_logic
                                                global g_auto_mix__how_much_canvas_to_pick
                                                
                                                if g_auto_mixing_uses_distance_logic:
                                                
                                                                                
                                                                                
                                                        bgColor = mergedColor

                                                            
                                                        # setto il fg color uguale a merged color (cioè bg color) mischiato con l'ultimo colore memorizzato
                                                        
                                                        fg2 = g_virtual_fg_color_rgb # rgbOfManagedColor(fg) # valori da 0 a 255
                                                        #fg2.print("fg2")
                                                        
                                                        comp = fg.components() 
                                                        #print(f"fg color = {comp}")
                         
                                                        dist = fg2.distance(bgColor)
                                                        #print(f"distance = {dist}, target distance = {self.mixing_target_distance}")
                         
                                                        
                                                        curDist = None
                                                        picked50 = False
                                                        global g_auto_mixing_target_distance
                                                        
                                                        curLayerTransp01 = float(document.activeNode().opacity()) / 255.0
                                                        target_distance_corretta_per_layer_transp = g_auto_mixing_target_distance / curLayerTransp01
                                                        
                                                        # calcola curFg
                                                        if dist  <= target_distance_corretta_per_layer_transp:
                                                            #i colori sono molto vicini. fai 50%
                                                            curMul = 0.5
                                                            curFg = rgb( fg2.r * curMul + bgColor.r * (1.0 - curMul),
                                                                                            fg2.g * curMul + bgColor.g * (1.0 - curMul),
                                                                                            fg2.b * curMul + bgColor.b * (1.0 - curMul),
                                                                                            255)
                                                            curDist = dist
                                                            picked50 = True
                                                        else:  # i colori sono lontani. avvicina poco a poco finché la distanza del curFg dall'origFg non diventa > target
                                                        
                                                            stepMul = 0.005
                                                            
                                                            
                                                            curMul = 1.0
                                                            
                                                            while True:
                                                                
                                                                curFg = rgb( fg2.r * curMul + bgColor.r * (1.0 - curMul),
                                                                                            fg2.g * curMul + bgColor.g * (1.0 - curMul),
                                                                                            fg2.b * curMul + bgColor.b * (1.0 - curMul),
                                                                                            255)
                                                                                            
                                                                curDist = curFg.distance(bgColor)
                                                                
                                                                #print(f"iterando. mul  = {curMul}, dist  tra {curFg.toString()} e {fg2.toString()} = {curDist}. ")
                                                                
                                                                if curDist <= target_distance_corretta_per_layer_transp:  
                                                                    break
                                                                    
                                                                if curMul <= 0:
                                                                    break
                                                                    
                                                                curMul -= stepMul   
                                                                    
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
                                                        
                                                        
                                                     
                                                        
                                                                                
                                                
                                                
                                                else: # normal logic
                                                
                                                    
                                                    
                                                    
                                                    
                                                    
                                                    #anche qui vedo la distanza, perche' se è piccola faccio snap
                                                    dist = g_virtual_fg_color_rgb.distance(mergedColor)
                                                    
                                                    # if dist < g_auto_mix_snap_distance and g_auto_mix__how_much_canvas_to_pick < 0.98:
                                                        # #snap to destination
                                                        # comp[0] = (g_virtual_fg_color_rgb.r/255.0) 
                                                        # comp[1] = (g_virtual_fg_color_rgb.g / 255.0) 
                                                        # comp[2] = (g_virtual_fg_color_rgb.b / 255.0)
                                                        
                                                    # else:
                                                        # blending
                                                        # print(f"fg color = {comp}")
                         
                     
                                                    
                                                    canv = g_auto_mix__how_much_canvas_to_pick
                                                    
                                                    fgMul = 1.0 - canv
                                                    
                                                    
                                                    # BEGIN mix colors old way
                                                    # comp[0] = (g_virtual_fg_color_rgb.r/255.0) * fgMul + (mergedColor.r / 255.0)  * canv
                                                    # comp[1] = (g_virtual_fg_color_rgb.g / 255.0) * fgMul + (mergedColor.g / 255.0)  * canv
                                                    # comp[2] = (g_virtual_fg_color_rgb.b / 255.0) * fgMul + (mergedColor.b  / 255.0)  * canv
                                                    
                                                    #END
                                                    
                                                    
                                                    #begin mix colors spectral, bgr
                                                    fgMul = 1.0 - canv
                                                    sb = g_virtual_fg_color_rgb.r/255.0
                                                    sg = g_virtual_fg_color_rgb.g/255.0
                                                    sr = g_virtual_fg_color_rgb.b/255.0
                                                    
                                                   
                                                    db = mergedColor.r / 255.0
                                                    dg = mergedColor.g / 255.0
                                                    dr = mergedColor.b / 255.0
                                                   
                                                   
                                                    resultColor = mixRGB(sr, sg, sb, fgMul, dr, dg, db)
                                                    # resultColor is [r,g,b]. copy back to bgr:
                                                    
                                                    comp[0] = resultColor[2]
                                                    comp[1] = resultColor[1]
                                                    comp[2] = resultColor[0]
                                                    
                                                    # END
                                              
                                                  
                                                  
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
                global g_auto_mixing_just_once_now_on
                global g_auto_mixing_just_once_logic
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
                                                
                                                        self.pixelBytes = curLayer.pixelData(int (round(doc_pos.x())), int(round(doc_pos.y())), 1, 1)
                                                        
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
                                                                
                                                                 
                                                global g_virtual_fg_color_rgb
                                                g_virtual_fg_color_rgb = mergedColor #lo memorizzo come target
                                                update_label_from_virtual_color()
                                                
                                                # importante: non aggiungerlo alla coda,  perché poi scatta lo stesso l'aggiunta alla coda con colore leggermente diverso, non so perche'. se non fai niente funziona.
                                                # # aggiungo alla lista solo se non è già in coda (stranamente è necessario)
                                                # if g_virtual_fg_color_rgb is None:
                                                    # pass
                                                # if len(g_last_virtual_colors_used) > 0:
                                                    # if g_last_virtual_colors_used[-1].equals(g_virtual_fg_color_rgb):
                                                        # pass
                                                    # else:
                                                        # g_last_virtual_colors_used.append(g_virtual_fg_color_rgb.clone())
                                                # else:
                                                    # g_last_virtual_colors_used.append(g_virtual_fg_color_rgb.clone())
                                                
                                                    
                                                
                                                
                                                # setto il fg color uguale a merged color
                                                fg = view.foregroundColor()
                                                comp = fg.components() 
                                                
                                                #wrokaround in case your fg color is [1,1], which means greyscale
                                                print(f"fg color = {comp}")
                                                
                                                if len(comp ) == 4:    
                                                        
                                                    
                     
                                                    comp[0] =  (mergedColor.r / 255.0)  
                                                    comp[1] =  (mergedColor.g / 255.0)
                                                    comp[2] = (mergedColor.b  / 255.0)
                                              
                                                    print(f"fg color after = {comp}")
                                                    
                                                    fg.setComponents(comp)
                                                    
                                                    view.setForeGroundColor(fg)
                            
                                                    if g_auto_mixing_just_once_logic:
                                                        g_auto_mixing_just_once_now_on = True
                                                        
                                                    # messaggio
                                                    if showMessage:
                                                        view.showFloatingMessage("Pick color", QIcon(), timeMessage, 1)
                                                elif len(comp ) == 2:
                                                    messageBox(" Your foreground color is currently grayscale. In order to use \"pick\", please set your foreground color to an RGB color first.")
                                                else:
                                                    messageBox("In order to use pick, please set your foreground color to an RGB color first.")
            
        
        
        def increaseMixing(self):
                global g_how_much_canvas_to_pick
                g_how_much_canvas_to_pick += g_mixing_step
                if g_how_much_canvas_to_pick > 1.0:
                        g_how_much_canvas_to_pick = 1.0
                        
                Krita.instance().writeSetting("colorPlus", "g_how_much_canvas_to_pick", str(g_how_much_canvas_to_pick))
                
                quickMessage(f"Increased mixing to {round(g_how_much_canvas_to_pick* 100.0)}%")
        
        def decreaseMixing(self):
                global g_how_much_canvas_to_pick
                g_how_much_canvas_to_pick -= g_mixing_step
                if g_how_much_canvas_to_pick < 0.0:
                        g_how_much_canvas_to_pick = 0.0
                        
                Krita.instance().writeSetting("colorPlus", "g_how_much_canvas_to_pick", str(g_how_much_canvas_to_pick))
                
                quickMessage(f"Decreased mixing to {round(g_how_much_canvas_to_pick * 100.0)}%")
        

        def increaseAutoMixing(self):
                global g_auto_mix__how_much_canvas_to_pick
                global g_mixing_step
                global g_auto_mixing_distance_step
                global g_auto_mixing_target_distance
                
                if g_auto_mixing_uses_distance_logic:
                    g_auto_mixing_target_distance += g_auto_mixing_distance_step
                    if g_auto_mixing_target_distance > 255.0:
                            g_auto_mixing_target_distance = 255.0
                            
                    Krita.instance().writeSetting("colorPlus", "g_auto_mixing_target_distance", str(g_auto_mixing_target_distance))
                    
                    quickMessage(f"Increased auto-mixing distance to {round(g_auto_mixing_target_distance )}")

                else:
                    g_auto_mix__how_much_canvas_to_pick += g_mixing_step
                    if g_auto_mix__how_much_canvas_to_pick > 1.0:
                            g_auto_mix__how_much_canvas_to_pick = 1.0
                            
                    Krita.instance().writeSetting("colorPlus", "g_auto_mix__how_much_canvas_to_pick", str(g_auto_mix__how_much_canvas_to_pick))
                    
                    quickMessage(f"Increased auto-mixing to {round(g_auto_mix__how_much_canvas_to_pick * 100.0)} %")
        
        def decreaseAutoMixing(self):
                global g_auto_mix__how_much_canvas_to_pick
                global g_mixing_step
                global g_auto_mixing_target_distance
                global g_auto_mixing_distance_step
                
                if g_auto_mixing_uses_distance_logic:
                    g_auto_mixing_target_distance -= g_auto_mixing_distance_step
                    if g_auto_mixing_target_distance < 0.0:
                            g_auto_mixing_target_distance = 0.0
                            
                    Krita.instance().writeSetting("colorPlus", "g_auto_mixing_target_distance", str(g_auto_mixing_target_distance))
                    
                    quickMessage(f"Decreased auto-mixing distance to {round(g_auto_mixing_target_distance)}")
        
                else:
                    g_auto_mix__how_much_canvas_to_pick -= g_mixing_step
                    if g_auto_mix__how_much_canvas_to_pick < 0.0:
                            g_auto_mix__how_much_canvas_to_pick = 0.0
                            
                    Krita.instance().writeSetting("colorPlus", "g_auto_mix__how_much_canvas_to_pick", str(g_auto_mix__how_much_canvas_to_pick))
                    
                    quickMessage(f"Decreased auto-mixing to {round(g_auto_mix__how_much_canvas_to_pick * 100.0)}%")
        

        
        def increaseAutoResetOpacityOnPick (self):
                global g_auto_reset_opacity_on_pick_level
                g_auto_reset_opacity_on_pick_level += 5.0
                if g_auto_reset_opacity_on_pick_level >= 100.0:
                        g_auto_reset_opacity_on_pick_level = 100.0
                        
                Krita.instance().writeSetting("colorPlus", "g_auto_reset_opacity_on_pick_level", str(g_auto_reset_opacity_on_pick_level))
                
                quickMessage(f"Increased default opacity to {round(g_auto_reset_opacity_on_pick_level)}%")
        def decreaseAutoResetOpacityOnPick (self):
                global g_auto_reset_opacity_on_pick_level
                g_auto_reset_opacity_on_pick_level -= 5.0
                if g_auto_reset_opacity_on_pick_level <= 0.0:
                        g_auto_reset_opacity_on_pick_level = 0.0
                        
                Krita.instance().writeSetting("colorPlus", "g_auto_reset_opacity_on_pick_level", str(g_auto_reset_opacity_on_pick_level))
                
                quickMessage(f"Decreased default opacity to {round(g_auto_reset_opacity_on_pick_level)}%")
        

        
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
        
        
                global g_normal_step_layer_opacity
                
                #dryPaper() # conviene, perche' tanto significa che i segni precedenti non si vedono.
                
                application = Krita.instance()
                currentDoc = application.activeDocument()
                
                if g_auto_dry_each_stroke:
                    parentNode = currentDoc.activeNode().parentNode()
                    if parentNode is not None:
                         activeLayer = parentNode.childNodes()[-2]
                    else:
                            activeLayer = currentDoc.activeNode()
                else:
                    activeLayer = currentDoc.activeNode()
                    
                
                curOpac = activeLayer.opacity()
                
                if curOpac <= 12.0 * 255.0 / 100.0:
                    stepOpacity = g_normal_step_layer_opacity / 2.0
                else:
                    stepOpacity = g_normal_step_layer_opacity 
                
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
                if g_auto_dry_each_stroke:
                    parentNode = currentDoc.activeNode().parentNode()
                    if parentNode is not None:
                         activeLayer = parentNode.childNodes()[-2]
                    else:
                            activeLayer = currentDoc.activeNode()
                else:
                    activeLayer = currentDoc.activeNode()
                    
                    
                curOpac = activeLayer.opacity()
                
                global g_normal_step_layer_opacity
                if curOpac <= 20.0 * 255.0 / 100.0:
                    stepOpacity = g_normal_step_layer_opacity / 2.0
                else:
                    stepOpacity = g_normal_step_layer_opacity 
                
                
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
            dryPaper(True)
            
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
                        
                        
                        if g_multi_layer_mode:
                            # root = currentDoc.rootNode()
                            newLa = currentDoc.createNode("Wet_area", "paintLayer")
                            newLa.setOpacity(oldOpacity)
                            
                            # backgroundLayer = parentNode.childNodes()[0]
                            
                            
                            parentNode.addChildNode(newLa, None)
                        
                        
                        
                        
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
        
        def manualResetLayerOpacityToDefault(self):
                global g_auto_reset_opacity_on_pick_level
                
                application = Krita.instance()
                document = application.activeDocument()
                
                                        
                if document is not None :
                    document.activeNode().setOpacity(g_auto_reset_opacity_on_pick_level * 255.0 / 100.0) # bm_djiwejdie
                    
                    document.refreshProjection()
                    
                    quickMessage(f"Reset layer opacity to default ({round(g_auto_reset_opacity_on_pick_level )}%)")
        
        def dryPaperAndPick(self):
            print("dry paper and pick")
            
            #non funziona se inverto l'ordine... non capisco perche'
            self.pick( False)
            
            
            
            # find if there is a parent node
            hasParentNode = False
            app = Krita.instance()
            document = None
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
            
            
            
            global g_auto_reset_opacity_on_pick_level
            global g_auto_reset_opacity_on_pick
            global g_temp_switched_to_100_previous_opac
            if  g_temp_switched_to_100_previous_opac is None and hasParentNode and g_multi_layer_mode: # I don't want to add a layer if I'm picking from the mixing palette, or if I've switched to 100 percent opacity mode
                newLa = dryPaper(showMessage = False)
                
                # if active layer opacity < 70, set to 70
                                        
                if g_auto_reset_opacity_on_pick == 1 and  document is not None and g_temp_switched_to_25_previous_opac is None :
                    newLa.setOpacity(g_auto_reset_opacity_on_pick_level * 255.0 / 100.0) # bm_djiwejdie
                    
                    document.refreshProjection()
                    
                quickMessage("Dry paper and pick color")
            elif g_temp_switched_to_100_previous_opac is not None and hasParentNode:
                # non faccio dry, ma devo cmq resettare l'opacità del layer attuale
                
                if g_auto_reset_opacity_on_pick == 1 and  document is not None :
                    document.activeNode().setOpacity(g_auto_reset_opacity_on_pick_level * 255.0 / 100.0) # bm_djiwejdie
                    
                    document.refreshProjection()
                
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
                
                
                
                
                
                
                # cerca di capire in che stato siamo. se c'è una window on top non minimizzata, siamo in stato normale. altrimenti siamo in stato view full screen
                siamoInStatoNormale = False
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


                    if stayOnTop and not isMinimized:
                        siamoInStatoNormale = True
                
                print(f"siamo in stato normale: {siamoInStatoNormale}")
                
                if siamoInStatoNormale:
                    # devo minimizzare le on top e massimizzare la prima delle non-on-top
                        
                    for su in subwins:
                        flags = su.windowFlags()
                        
                        stayOnTop = False
                        if su.windowFlags() & Qt.WindowStaysOnTopHint:
                            stayOnTop = True
                        else:
                            stayOnTop = False
                        
                        if stayOnTop:
                            # è una finestra di reference: minimizzala
                            su.setWindowState(su.windowState() | Qt.WindowMinimized)
                        else:
                            # è è una finestra normal: massimizza
                            #su.setWindowState(su.windowState() & ~Qt.WindowMinimized)
                            
                            su.setWindowState(su.windowState() | Qt.WindowMaximized)  # la massimizzo
                            

                    # ora nascondo i docker
                    app.action('view_show_canvas_only').trigger()
                    app.activeDocument().waitForDone () # action needs to finish before continuing
                    
                    
                    #workaround per mancanza di fit to page
                    app.action('zoom_to_100pct').trigger()
                    app.activeDocument().waitForDone () # action needs to finish before continuing
                    
                    app.action('toggle_zoom_to_fit').trigger()
                    app.activeDocument().waitForDone () # action needs to finish before continuing
                    
                
                else:
                        # devo tornare in stato normale, quindi alle on top devo togliere il minimized e alle normali devo togliere il maximized
                            
                        for su in subwins:
                            flags = su.windowFlags()
                            
                            stayOnTop = False
                            if su.windowFlags() & Qt.WindowStaysOnTopHint:
                                stayOnTop = True
                            else:
                                stayOnTop = False
                            
                            if stayOnTop:
                                # è una finestra di reference: togli il minimized
                                su.setWindowState(su.windowState() & ~Qt.WindowMinimized)
                            else:
                                # è è una finestra normal: togli il massimizza
                                su.setWindowState(su.windowState() & ~Qt.WindowMaximized)  # tolgo lo stato maximixed
                                
                        # ora ri-mostro i docker (richiamando la stessa action)                   
                        app.action('view_show_canvas_only').trigger()
                        app.activeDocument().waitForDone () # action needs to finish before continuing
                        

                        # isMinimized = False
                        # if su.windowState() & Qt.WindowMinimized:
                            # isMinimized = True
                        # else:
                            # isMinimized = False

                        # print(f"subwindow title = {su.windowTitle()}, stay on top = {stayOnTop    }, minimized = {isMinimized}")

                        
                        # if stayOnTop:
                            # if isMinimized:
                                # su.setWindowState(su.windowState() & ~Qt.WindowMinimized)
                            # else:
                                # su.setWindowState(su.windowState() | Qt.WindowMinimized)
                    
                # app.action('view_show_canvas_only').trigger()
                # app.activeDocument().waitForDone () # action needs to finish before continuing
                
                
                # #workaround per mancanza di fit to page
                # app.action('zoom_to_100pct').trigger()
                # app.activeDocument().waitForDone () # action needs to finish before continuing
                
                # app.action('toggle_zoom_to_fit').trigger()
                # app.activeDocument().waitForDone () # action needs to finish before continuing
                
                
                
                
                # # ordina le finestre in modo che la always on top sia per prima, altrimenti poi l'action fit to window avviene alla finestra sbagliata.
                
                
                # for su in subwins:
                    # flags = su.windowFlags()
                    
                    # stayOnTop = False
                    # if su.windowFlags() & Qt.WindowStaysOnTopHint:
                        # stayOnTop = True
                    # else:
                        # stayOnTop = False
                    

                    # isMinimized = False
                    # if su.windowState() & Qt.WindowMinimized:
                        # isMinimized = True
                    # else:
                        # isMinimized = False

                    # print(f"subwindow title = {su.windowTitle()}, stay on top = {stayOnTop    }, minimized = {isMinimized}")

                    
                    # if stayOnTop:
                        # if isMinimized:
                            # su.setWindowState(su.windowState() & ~Qt.WindowMinimized)
                        # else:
                            # su.setWindowState(su.windowState() | Qt.WindowMinimized)
                

                # #I activate any window that is not on top and not minimized
                # for su in subwins:
                    # flags = su.windowFlags()
                    
                    # stayOnTop = False
                    # if su.windowFlags() & Qt.WindowStaysOnTopHint:
                        # stayOnTop = True
                    # else:
                        # stayOnTop = False
                    

                    # isMinimized = False
                    # if su.windowState() & Qt.WindowMinimized:
                        # isMinimized = True
                    # else:
                        # isMinimized = False


                    # if not isMinimized and not stayOnTop:
                        
                        # q_win = wi.qwindow()
                        # mdi_area = q_win.findChild(QMdiArea)
                        # mdi_area.setActiveSubWindow(su)


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
        

        def toggleAutoResetOpacityOnPick(self):
            global g_auto_reset_opacity_on_pick
            if g_auto_reset_opacity_on_pick == 1:
                g_auto_reset_opacity_on_pick = 0
                quickMessage("Auto reset opacity on color pick: disabled")
            else:
                g_auto_reset_opacity_on_pick = 1
                quickMessage(f"Auto reset opacity on color pick: enabled. Will be reset to {round(g_auto_reset_opacity_on_pick_level)}.")
                
                
            Krita.instance().writeSetting("colorPlus", "g_auto_reset_opacity_on_pick", str(g_auto_reset_opacity_on_pick))
        
        
        # def toggleMixClearsCurrentLayer(self):
            # global g_mix_auto_clears_cur_layer
            # if g_mix_auto_clears_cur_layer == "1":
                # g_mix_auto_clears_cur_layer = "0"
                # quickMessage("Color mix will not clear current layer automatically")
            # else:
                # g_mix_auto_clears_cur_layer = "1"
                # quickMessage("Color mix will clear current layer automatically")
                
                
            # Krita.instance().writeSetting("colorPlus", "g_mix_auto_clears_cur_layer", g_mix_auto_clears_cur_layer)
        
        def toggleMultiLayerMode(self):
            global g_multi_layer_mode
            g_multi_layer_mode = not g_multi_layer_mode
            
            
            multi_layer_mode_str = "1" if g_multi_layer_mode else "0"
            
            Krita.instance().writeSetting("colorPlus", "g_multi_layer_mode", multi_layer_mode_str)
                
                
                
        def createActions(self, window):
        


                action = window.createAction("LastColor", "Switch to last used color")
                action.triggered.connect(self.switchToLastColor)
                
                # action2 = window.createAction("MixColorBig", "MixColorBig")
                # action2.triggered.connect(self.mixBig)
                
                # action2 = window.createAction("MixColorSmall", "MixColorSmall")
                # action2.triggered.connect(self.mixSmall)


                actionMixW = window.createAction("MixColorBecauseWrong", "Mix color because current color is wrong (also clears current layer)")
                actionMixW.triggered.connect(lambda : mixFgColorWithBgColor_normalLogic(clearCurLayer = True, createLayer = False))
                
                actionMixC = window.createAction("MixColorBecauseWantNew", "Mix color because you want to fade out (also creates new layer)")
                actionMixC.triggered.connect(lambda  : mixFgColorWithBgColor_normalLogic(clearCurLayer = False, createLayer = True))
                
                # actionMixSmall = window.createAction("MixColorSmall", "Pick some color from canvas, but no more than a given distance")
                # actionMixSmall.triggered.connect(self.mixFgColorWithBgColor_maxDistanceLogic)
                
                actionPickAndDry = window.createAction("DryPaperAndPick", "Pick color under cursor and dry the paper")
                actionPickAndDry.triggered.connect(self.dryPaperAndPick)
                
                
                actionPick = window.createAction("PickColor", "Pick color under cursor")
                actionPick.triggered.connect(self.pick)

                actionDryPaper = window.createAction("LayerMergeDownAndNew", "Dry the paper (create new layer and set opacity)")
                actionDryPaper.triggered.connect(self.dryPaperWithMessage)

                actionViewFullScreen = window.createAction("ViewSingleWindow", "Hide always on top windows and go fullscreen")
                actionViewFullScreen.triggered.connect(self.minimizeOnTopAndViewFullScreen)

                actionIncreaseLO = window.createAction("IncreaseLayerOpacity", "Increase current layer opacity")
                actionIncreaseLO.setShortcut("S")
                actionIncreaseLO.triggered.connect(self.increaseLayerOpacity)

                actiondeclo = window.createAction("DecreaseLayerOpacity", "Decrease current layer opacity")
                actiondeclo.setShortcut("A")
                actiondeclo.triggered.connect(self.decreaseLayerOpacity)



                # actionIncreaseAO = window.createAction("IncreaseMaxDistanceAutoOpacity", "Increase max distance for auto opacity")
                # actionIncreaseAO.triggered.connect(self.increaseAutoOpacityMaxDistance)

                # actiondecao = window.createAction("DecreaseMaxDistanceAutoOpacity", "Decrease max distance for auto opacity")
                # actiondecao.triggered.connect(self.decreaseAutoOpacityMaxDistance)

                actionincmi = window.createAction("IncreaseMixing", "Increase mixing level (amount of color you pick from canvas when mixing)")
                actionincmi.triggered.connect(self.increaseMixing)

                actiondecmi = window.createAction("DecreaseMixing", "Decrease mixing level (amount of color you pick from canvas when mixing)")
                actiondecmi.triggered.connect(self.decreaseMixing)

                # global g_mix_auto_clears_cur_layer
                # actionmixClear = window.createAction("MixClearCurrentLayer", "Mixing color auto-clears current layer")
                # actionmixClear.setCheckable(True)
                # actionmixClear.setChecked(g_mix_auto_clears_cur_layer == "1")
                # actionmixClear.triggered.connect(self.toggleMixClearsCurrentLayer)


                actioninaro= window.createAction("IncreaseAutoResetOpacityOnPick", "Increase default layer opacity")
                actioninaro.setShortcut("w")
                actioninaro.triggered.connect(self.increaseAutoResetOpacityOnPick)


                actiondearo= window.createAction("DecreaseAutoResetOpacityOnPick", "Decrease default layer opacity")
                actiondearo.setShortcut("q")
                actiondearo.triggered.connect(self.decreaseAutoResetOpacityOnPick)


                actionSave = window.createAction("saveWindowPositions", "Save state and position of all windows")
                actionSave.setShortcut("Ctrl+Shift+F")
                actionSave.triggered.connect(self.saveWindowPositions)
                
                actionRestore = window.createAction("restoreWindowPositions", "Restore state and position of all windows")
                actionRestore.setShortcut("Ctrl+Shift+R")
                actionRestore.triggered.connect(self.restoreWindowPositions)
                
                actionToggle100= window.createAction("toggle100PercOpacity", "Toggle 100% layer opacity")
                # actionToggle100.setShortcut("f")
                actionToggle100.triggered.connect(self.toggle_100_opac)

                actionToggle25= window.createAction("toggle25PercOpacity", "Toggle 25% layer opacity")
                
                actionToggle25.triggered.connect(self.toggle_25_opac)


                actionToggleMc= window.createAction("cleanupLayers", "Cleanup (merge all temp layers)")
                actionToggleMc.triggered.connect(self.mergeCleanup)
                
                
                self.actionAutoFocus= window.createAction("autoFocus", "Autofocus windows on mouse over")
                self.actionAutoFocus.setCheckable(True)
                self.actionAutoFocus.setChecked(self.g_auto_focus == "true")
                self.actionAutoFocus.triggered.connect(self.toggleAutoFocus)
                

                global g_auto_reset_opacity_on_pick
                self.actionAutoResOpPick= window.createAction("toggleAutoResetOpacityOnPick", "Auto-reset layer opacity to default on color pick")
                self.actionAutoResOpPick.setCheckable(True)
                self.actionAutoResOpPick.setChecked(g_auto_reset_opacity_on_pick == 1)
                self.actionAutoResOpPick.triggered.connect(self.toggleAutoResetOpacityOnPick)
                


                global g_multi_layer_mode
                self.actionSingleLayerMode = window.createAction("toggleSingleLayerMode", "Single-layer mode (don't auto create layers for watercolor effect)")
                self.actionSingleLayerMode.setCheckable(True)
                self.actionSingleLayerMode.setChecked(not g_multi_layer_mode)
                self.actionSingleLayerMode.triggered.connect(self.toggleMultiLayerMode)
                


                self.actionAcceptColorAndStop = window.createAction("acceptCurrentColorAndStopDirty", "Accept current color and stop dirty brush")
                self.actionAcceptColorAndStop.triggered.connect(lambda: self.acceptCurrentColorAndStopDirty(clearCurLayer = True))


                self.manualResOpPick= window.createAction("manualResetLayerOpacityToDefault", "Reset layer opacity to default now")
                # self.manualResOpPick.setShortcut("v")
                self.manualResOpPick.triggered.connect(self.manualResetLayerOpacityToDefault)
                
                
                setFgColorEqualToColorOfLastStroke = window.createAction("acceptCurrentColor", "accept current layer color")
                setFgColorEqualToColorOfLastStroke.triggered.connect(setFgColorEqualToColorOfLastStrokeAfterOpacityAdjust)
                setFgColorEqualToColorOfLastStroke.setShortcut("v")
                
                main_menu = window.qwindow().menuBar()
                custom_menu = main_menu.addMenu("ColorPlus")
                
                custom_menu.addAction(self.actionAutoFocus)
                custom_menu.addAction(self.actionSingleLayerMode)
                
                custom_menu.addSeparator()
                custom_menu.addAction(actionViewFullScreen)
                
                
                global g_auto_mix_enabled
                global g_actionAutoMix
                
                g_auto_mix_enabled = False
                g_actionAutoMix= window.createAction("toggleAutoMixing", "Auto mixing (each stroke picks a bit of color from the background)")
                g_actionAutoMix.setCheckable(True)
                g_actionAutoMix.setShortcut("r")                
                g_actionAutoMix.triggered.connect(toggleAutoMixing)


                self.actionIncAutoMix = window.createAction("increaseAutoMixing", "Increase auto-mixing (amount of bg color you pick at each stroke)")
                self.actionIncAutoMix.setShortcut("shift+w")
                self.actionIncAutoMix.triggered.connect(self.increaseAutoMixing)
                
                self.actionDecAutoMix = window.createAction("decreaseAutoMixing", "Decrease auto-mixing (amount of bg color you pick at each stroke)")
                self.actionDecAutoMix.setShortcut("shift+q")
                self.actionDecAutoMix.triggered.connect(self.decreaseAutoMixing)

                custom_menu.addSeparator()
                custom_menu.addAction(g_actionAutoMix)
                custom_menu.addAction(self.actionIncAutoMix)
                custom_menu.addAction(self.actionDecAutoMix)
                
                
                custom_menu.addSeparator()
                custom_menu.addAction(actionDryPaper)
                
                custom_menu.addAction(actionToggleMc)
                
                custom_menu.addSeparator()
                custom_menu.addAction(actionRestore)
                custom_menu.addAction(actionSave)
                
                custom_menu.addSeparator()
                custom_menu.addAction(actionPick)
                custom_menu.addAction(actionPickAndDry)
                
                custom_menu.addSeparator()
                custom_menu.addAction(self.actionAutoResOpPick)
                custom_menu.addAction(actioninaro)
                custom_menu.addAction(actiondearo)
                custom_menu.addAction(self.manualResOpPick)
                
                
                custom_menu.addSeparator()
                
                custom_menu.addAction(actionIncreaseLO)
                custom_menu.addAction(actiondeclo)
                custom_menu.addSeparator()
                # custom_menu.addAction(actionmixClear)
                custom_menu.addAction(actionMixW)
                custom_menu.addAction(actionMixC)
                
                custom_menu.addAction(actionincmi)
                custom_menu.addAction(actiondecmi)
                
                custom_menu.addSeparator()
                
                custom_menu.addAction(actionToggle100)
                custom_menu.addAction(actionToggle25)
                
                



            
                

                
                
# And add the extension to Krita's list of extensions:
Krita.instance().addExtension(MyExtension(Krita.instance()))

