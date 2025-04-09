from typing import List, TYPE_CHECKING # Import List and TYPE_CHECKING

if TYPE_CHECKING:
    from .recent_color import rgb # Import for type hinting only
    from PyQt5.QtWidgets import QLabel # Import for type hinting only

# Funzione di log per il debug
def log(s):
    global printCount
    printCount += 1
    print(f"{printCount}: {s}\n\n")

g_blur_on_dry = False

countColorChanged = 0
printCount = 0

# g_mix_auto_clears_cur_layer = "1"

g_color_changed_from_selector_probably = False

g_layer_is_dirty = {}

g_diminishing_opacity = False #True to have auto-mixing with amount that auto-decreases

g_btn_pick_color = None



#g_virtual_color_used_last_rgb  = None
g_virtual_fg_color_rgb = None

g_last_virtual_colors_used: List['rgb'] = [] # Add type hint using forward reference
g_color_history_index = -1 # Index pointing to the 'active' color in g_last_virtual_colors_used for switching

timeMessage = 300
g_normal_step_layer_opacity = 20

g_mixing_step = 0.05

g_auto_mixing_distance_step = 5

g_set_spectral_blend_mode_when_creating_layer = False

g_multi_layer_mode = False

###############auto-mixing

g_auto_mixing_uses_distance_logic = False # perche' io posso prendere un colore molto diverso o molto simile. voglio contrastare sempre poco, mai tanto. altrimenti non attivo l'auto mixing.
                                                                        # d'altra parta, è sbagliato concettualmente se io fisso un target color e voglio arrivarci in N strokes
g_auto_mixing_just_once_logic = False
g_auto_mixing_just_once_now_on = False
g_ultimo_colore_vero_settato_dall_utente = None

#when distance logic is active
g_auto_mixing_target_distance = None  # value is ignored, will be read from settings.

#when distance logic is not active
g_auto_mix__how_much_canvas_to_pick = None # value is ignored: will be read from settings --- 0.999 to drag color from canvas , e.g. to remove overlap. then set auto-mixing. 

g_auto_mix_ignore_current_layer = False # metti false se vuoi trascinare il colore appena messo, true se vuoi evitarlo

#g_auto_mix_snap_distance = 30

########################

g_auto_opacity_max_distance = 40

g_auto_dry_each_stroke = False
g_is_drying_paper = False # Flag to prevent history update during dryPaper

g_auto_mix_paused = False
g_auto_mix_enabled = False
g_auto_mix_color_to_ignore = None



g_dirty_brush_overall_enabled = False
g_dirty_brush_currently_on = True
g_dirty_brush_color_to_ignore  = None
g_dirty_brush_level = None # value is ignored: will be read from settings --- range from 0.04 to 0.5

g_color_on_down_dirty_brush = None
g_last_coord_mouse_down = None
g_last_coord_mouse_up = None

g_picking_color = False
g_mixing_color = False

g_temp_switched_to_100_previous_opac = None

g_opacity_decided_for_layer = False

lblActiveColor : 'QLabel' = None # Use None, forward reference QLabel

event_lookup = {"0": "QEvent::None",
                "114": "QEvent::ActionAdded",
                "113": "QEvent::ActionChanged",
                "115": "QEvent::ActionRemoved",
                "99": "QEvent::ActivationChange",
                "121": "QEvent::ApplicationActivate",
                "122": "QEvent::ApplicationDeactivate",
                "36": "QEvent::ApplicationFontChange",
                "37": "QEvent::ApplicationLayoutDirectionChange",
                "38": "QEvent::ApplicationPaletteChange",
                "214": "QEvent::ApplicationStateChange",
                "35": "QEvent::ApplicationWindowIconChange",
                "68": "QEvent::ChildAdded",
                "69": "QEvent::ChildPolished",
                "71": "QEvent::ChildRemoved",
                "40": "QEvent::Clipboard",
                "19": "QEvent::Close",
                "200": "QEvent::CloseSoftwareInputPanel",
                "178": "QEvent::ContentsRectChange",
                "82": "QEvent::ContextMenu",
                "183": "QEvent::CursorChange",
                "52": "QEvent::DeferredDelete",
                "60": "QEvent::DragEnter",
                "62": "QEvent::DragLeave",
                "61": "QEvent::DragMove",
                "63": "QEvent::Drop",
                "170": "QEvent::DynamicPropertyChange",
                "98": "QEvent::EnabledChange",
                "10": "QEvent::Enter",
                "150": "QEvent::EnterEditFocus",
                "124": "QEvent::EnterWhatsThisMode",
                "206": "QEvent::Expose",
                "116": "QEvent::FileOpen",
                "8": "QEvent::FocusIn",
                "9": "QEvent::FocusOut",
                "23": "QEvent::FocusAboutToChange",
                "97": "QEvent::FontChange",
                "198": "QEvent::Gesture",
                "202": "QEvent::GestureOverride",
                "188": "QEvent::GrabKeyboard",
                "186": "QEvent::GrabMouse",
                "159": "QEvent::GraphicsSceneContextMenu",
                "164": "QEvent::GraphicsSceneDragEnter",
                "166": "QEvent::GraphicsSceneDragLeave",
                "165": "QEvent::GraphicsSceneDragMove",
                "167": "QEvent::GraphicsSceneDrop",
                "163": "QEvent::GraphicsSceneHelp",
                "160": "QEvent::GraphicsSceneHoverEnter",
                "162": "QEvent::GraphicsSceneHoverLeave",
                "161": "QEvent::GraphicsSceneHoverMove",
                "158": "QEvent::GraphicsSceneMouseDoubleClick",
                "155": "QEvent::GraphicsSceneMouseMove",
                "156": "QEvent::GraphicsSceneMousePress",
                "157": "QEvent::GraphicsSceneMouseRelease",
                "182": "QEvent::GraphicsSceneMove",
                "181": "QEvent::GraphicsSceneResize",
                "168": "QEvent::GraphicsSceneWheel",
                "18": "QEvent::Hide",
                "27": "QEvent::HideToParent",
                "127": "QEvent::HoverEnter",
                "128": "QEvent::HoverLeave",
                "129": "QEvent::HoverMove",
                "96": "QEvent::IconDrag",
                "101": "QEvent::IconTextChange",
                "83": "QEvent::InputMethod",
                "207": "QEvent::InputMethodQuery",
                "169": "QEvent::KeyboardLayoutChange",
                "6": "QEvent::KeyPress",
                "7": "QEvent::KeyRelease",
                "89": "QEvent::LanguageChange",
                "90": "QEvent::LayoutDirectionChange",
                "76": "QEvent::LayoutRequest",
                "11": "QEvent::Leave",
                "151": "QEvent::LeaveEditFocus",
                "125": "QEvent::LeaveWhatsThisMode",
                "88": "QEvent::LocaleChange",
                "176": "QEvent::NonClientAreaMouseButtonDblClick",
                "174": "QEvent::NonClientAreaMouseButtonPress",
                "175": "QEvent::NonClientAreaMouseButtonRelease",
                "173": "QEvent::NonClientAreaMouseMove",
                "177": "QEvent::MacSizeChange",
                "43": "QEvent::MetaCall",
                "102": "QEvent::ModifiedChange",
                "4": "QEvent::MouseButtonDblClick",
                "2": "QEvent::MouseButtonPress",
                "3": "QEvent::MouseButtonRelease",
                "5": "QEvent::MouseMove",
                "109": "QEvent::MouseTrackingChange",
                "13": "QEvent::Move",
                "197": "QEvent::NativeGesture",
                "208": "QEvent::OrientationChange",
                "12": "QEvent::Paint",
                "39": "QEvent::PaletteChange",
                "131": "QEvent::ParentAboutToChange",
                "21": "QEvent::ParentChange",
                "212": "QEvent::PlatformPanel",
                "217": "QEvent::PlatformSurface",
                "75": "QEvent::Polish",
                "74": "QEvent::PolishRequest",
                "123": "QEvent::QueryWhatsThis",
                "106": "QEvent::ReadOnlyChange",
                "199": "QEvent::RequestSoftwareInputPanel",
                "14": "QEvent::Resize",
                "204": "QEvent::ScrollPrepare",
                "205": "QEvent::Scroll",
                "117": "QEvent::Shortcut",
                "51": "QEvent::ShortcutOverride",
                "17": "QEvent::Show",
                "26": "QEvent::ShowToParent",
                "50": "QEvent::SockAct",
                "192": "QEvent::StateMachineSignal",
                "193": "QEvent::StateMachineWrapped",
                "112": "QEvent::StatusTip",
                "100": "QEvent::StyleChange",
                "87": "QEvent::TabletMove",
                "92": "QEvent::TabletPress",
                "93": "QEvent::TabletRelease",
                "171": "QEvent::TabletEnterProximity",
                "172": "QEvent::TabletLeaveProximity",
                "219": "QEvent::TabletTrackingChange",
                "22": "QEvent::ThreadChange",
                "1": "QEvent::Timer",
                "120": "QEvent::ToolBarChange",
                "110": "QEvent::ToolTip",
                "184": "QEvent::ToolTipChange",
                "194": "QEvent::TouchBegin",
                "209": "QEvent::TouchCancel",
                "196": "QEvent::TouchEnd",
                "195": "QEvent::TouchUpdate",
                "189": "QEvent::UngrabKeyboard",
                "187": "QEvent::UngrabMouse",
                "78": "QEvent::UpdateLater",
                "77": "QEvent::UpdateRequest",
                "111": "QEvent::WhatsThis",
                "118": "QEvent::WhatsThisClicked",
                "31": "QEvent::Wheel",
                "132": "QEvent::WinEventAct",
                "24": "QEvent::WindowActivate",
                "103": "QEvent::WindowBlocked",
                "25": "QEvent::WindowDeactivate",
                "34": "QEvent::WindowIconChange",
                "105": "QEvent::WindowStateChange",
                "33": "QEvent::WindowTitleChange",
                "104": "QEvent::WindowUnblocked",
                "203": "QEvent::WinIdChange",
                "126": "QEvent::ZOrderChange", }
                
allBrushPresets = None # Use None instead of null

g_docker_instance = None
g_color_history_docker_instance = None

g_auto_focus = "False"