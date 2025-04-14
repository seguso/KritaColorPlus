# brush_cycler.py
# Module to handle automatic brush cycling after each stroke

from krita import Krita  # type: ignore
from . import globals as g

class BrushCycler:
    """Class to manage cycling through a list of brushes automatically"""
    
    def __init__(self):
        self.enabled = False
        self.brush_list = []  # List of brush preset names to cycle through
        self.current_index = 0
        self.load_settings()
    
    def load_settings(self):
        """Load brush cycler settings from Krita configuration"""
        app = Krita.instance()
        
        # non voglio che all'avvio parta il brush cycler
        #self.enabled = app.readSetting("colorPlus", "brush_cycler_enabled", "false").lower() == "true"
        
        # Load saved brush list
        brush_list_str = app.readSetting("colorPlus", "brush_cycler_list", "")
        if brush_list_str:
            self.brush_list = brush_list_str.split(",")
        else:
            self.brush_list = []
        
        # Load current index
        try:
            self.current_index = int(app.readSetting("colorPlus", "brush_cycler_index", "0"))
            # Ensure index is valid
            if self.current_index >= len(self.brush_list):
                self.current_index = 0
        except ValueError:
            self.current_index = 0
    
    def save_settings(self):
        """Save brush cycler settings to Krita configuration"""
        app = Krita.instance()
        #app.writeSetting("colorPlus", "brush_cycler_enabled", str(self.enabled).lower())
        app.writeSetting("colorPlus", "brush_cycler_list", ",".join(self.brush_list))
        app.writeSetting("colorPlus", "brush_cycler_index", str(self.current_index))
    
    def toggle_enabled(self):
        """Toggle brush cycling on/off"""
        self.enabled = not self.enabled
        self.save_settings()
        return self.enabled
    
    def set_brush_list(self, brush_list):
        """Set the list of brushes to cycle through"""
        if not isinstance(brush_list, list):
            raise TypeError("brush_list must be a list of brush preset names")
        
        # Verify all brushes exist
        all_presets = Krita.instance().resources('preset')
        valid_brushes = []
        
        for brush_name in brush_list:
            # Check if the brush exists in available presets
            found = False
            for preset_key, preset in all_presets.items():
                if preset.name() == brush_name:
                    valid_brushes.append(brush_name)
                    found = True
                    break
            
            if not found:
                g.log(f"Warning: Brush preset '{brush_name}' not found and will be skipped")
        
        self.brush_list = valid_brushes
        self.current_index = 0 if valid_brushes else 0
        self.save_settings()
    
    def add_current_brush(self):
        """Add the currently active brush to the cycle list"""
        app = Krita.instance()
        view = app.activeWindow().activeView()
        
        if view:
            # Get current brush preset
            current_preset = view.currentBrushPreset()
            if current_preset:
                brush_name = current_preset.name()
                
                # Add to list if not already present
                if brush_name not in self.brush_list:
                    self.brush_list.append(brush_name)
                    self.save_settings()
                    return True
        
        return False
    
    def remove_brush(self, brush_name):
        """Remove a brush from the cycle list"""
        if brush_name in self.brush_list:
            self.brush_list.remove(brush_name)
            # Adjust current index if needed
            if self.current_index >= len(self.brush_list):
                self.current_index = 0 if self.brush_list else 0
            self.save_settings()
            return True
        return False
    
    def clear_brush_list(self):
        """Clear the brush cycle list"""
        self.brush_list = []
        self.current_index = 0
        self.save_settings()
    
    def cycle_to_next_brush(self):
        """Cycle to the next brush in the list and apply it, preserving size"""
        if not self.enabled or not self.brush_list:
            return False

        app = Krita.instance()
        window = app.activeWindow()
        if not window:
            return False
        view = window.activeView()
        if not view:
            return False

        # Get current brush size
        previous_size = view.brushSize()

        # Move to next brush
        self.current_index = (self.current_index + 1) % len(self.brush_list)

        # Apply the brush
        applied_successfully = self.apply_current_brush()

        # Restore the previous size if the brush was applied
        if applied_successfully:
            # Re-get view just in case, though likely unnecessary
            view = Krita.instance().activeWindow().activeView()
            if view:
                view.setBrushSize(previous_size)
                g.log(f"Restored brush size to: {previous_size}")

        return applied_successfully
    
    def apply_current_brush(self):
        """Apply the current brush in the cycle"""
        if not self.brush_list:
            return False
        
        app = Krita.instance()
        window = app.activeWindow()
        if not window:
            return False
        
        view = window.activeView()
        if not view:
            return False
        
        # Get the brush name
        brush_name = self.brush_list[self.current_index]
        
        # Find the brush preset
        all_presets = app.resources('preset')

        # self.debug_print_all_brushes()
        
        for preset_key, preset in all_presets.items():
            if preset.name() == brush_name:
                # Apply the brush preset using setCurrentBrushPreset
                view.setCurrentBrushPreset(preset)
                g.log(f"Switched to brush: {brush_name}")
                self.save_settings()
                return True
        
        g.log(f"Error: Could not find brush preset '{brush_name}'")
        return False

    def debug_print_all_brushes(self):
        """Debug function to print all available brush presets in Krita"""
        app = Krita.instance()
        all_presets = app.resources('preset')
        
        g.log("=== DEBUG: All available brush presets ===")
        g.log(f"Total number of presets: {len(all_presets)}")
        
        # Sort brush names alphabetically for easier reading
        brush_names = []
        for preset_key, preset in all_presets.items():
            brush_names.append(preset.name())
            g.log(f"Preset key: {preset_key}")
        
        brush_names.sort()
        for i, name in enumerate(brush_names):
            g.log(f"{i+1}. {name}")
        
        g.log("=== End of brush presets list ===")
        return brush_names

# Create a global instance
brush_cycler = BrushCycler()