g_blur_on_dry = False

countColorChanged = 0

# g_mix_auto_clears_cur_layer = "1"

g_color_changed_from_selector_probably = False
global g_virtual_fg_color_rgb

global g_virtual_fg_color_rgb_previous_when_dirty_brush_on

g_layer_is_dirty = {}

g_diminishing_opacity = False #True to have auto-mixing with amount that auto-decreases

g_btn_pick_color = None



g_virtual_color_used_last_rgb  = None
g_virtual_fg_color_rgb = None

g_last_virtual_colors_used: List['rgb'] = [] # Add type hint using forward reference
g_color_history_index = -1 # Index pointing to the 'active' color in g_last_virtual_colors_used for switching

timeMessage = 300
g_normal_step_layer_opacity = 20

g_mixing_step = 0.05

g_auto_mixing_distance_step = 5

g_set_spectral_blend_mode_when_creating_layer = True

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

g_auto_mix_ignore_current_layer = False # metti false se vuoi trascinare il colore appena messo, true se vuoi evitarlo

#g_auto_mix_snap_distance = 30

########################

g_auto_opacity_max_distance = 40

g_auto_dry_each_stroke = False

g_auto_mix_paused = False
g_auto_mix_enabled = False


g_dirty_brush_overall_enabled = False
g_dirty_brush_currently_on = True



g_last_coord_mouse_down = None
g_last_coord_mouse_up = None

g_picking_color = False
g_mixing_color = False

g_temp_switched_to_100_previous_opac = None

g_opacity_decided_for_layer = False