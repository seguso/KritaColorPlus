from . globals import log
import math

class rgb:
        def __init__(self, r, g, b, a):
                if not isinstance(r, float) or not isinstance(g, float) or not isinstance(b, float) or not isinstance(a, float):
                    raise TypeError("r, g, and b and a must be float values (doubles)")
                self.a = a
                self.r = r
                self.g = g
                self.b = b
                
        def log(self, msg):
                log(f"{msg}:   {self.toString()}")
                
        def toString(self):
            # inverto r e b perche' in realta' siamo bgr
            return f" b:{self.r}, g:{self.g}, r:{self.b} ,a:{self.a}"

        def average(self, c):
                return rgb((self.r + c.r) / 2.0,
                                                        (self.g + c.g) / 2.0,
                                                        (self.b + c.b) / 2.0,
                                                        255.0)

        def distance(self, c):
            return math.sqrt((self.r - c.r)*(self.r - c.r) + (self.g - c.g)*(self.g - c.g) + (self.b - c.b)*(self.b - c.b) )
            
        def equals(self, c):
            return c.r == self.r and c.g == self.g and c.b == self.b

        def clone(self):
            return rgb(self.r, self.g, self.b, self.a)

def rgbOfColorArray01(comp):
    """Converts a Krita color component sequence (RGBA, 0.0-1.0) to an rgb object (RGBA, 0.0-255.0)."""
    if not isinstance(comp, (list, tuple)) or len(comp) < 3: # Check for at least RGB
        raise ValueError("Input must be a sequence (list or tuple) with at least 3 components (R, G, B)")
        
    # Handle potential alpha component (use 255.0 if not present)
    alpha = comp[3] * 255.0 if len(comp) >= 4 else 255.0
        
    return rgb(comp[0] * 255.0, comp[1] * 255.0, comp[2] * 255.0, alpha)


def rgbOfColorArray255(comp : list[float| int]) -> rgb:
    """Converts a Krita color component sequence (RGBA, 0.0-1.0) to an rgb object (RGBA, 0.0-255.0)."""
    if not isinstance(comp, (list, tuple)) or len(comp) < 3: # Check for at least RGB
        raise ValueError("Input must be a sequence (list or tuple) with at least 3 components (R, G, B)")
        
    # Handle potential alpha component (use 255.0 if not present)
    alpha = float(comp[3]) if len(comp) >= 4 else 255.0
        
    return rgb(float(comp[0]) , float( comp[1] ), float(comp[2] ), alpha)

from typing import List # Add List import for type hinting

def colorArrayOfRgb(rgb_color: rgb) -> List[float]:
    """Converts an rgb object (RGBA, 0.0-255.0) to a Krita color component array (RGBA, 0.0-1.0), with alpha forced to 1.0."""
    if not isinstance(rgb_color, rgb):
        raise TypeError("Input must be an rgb object")
        
    # Convert R, G, B from 0-255 range to 0.0-1.0 range
    # Clamp values to ensure they are within [0.0, 1.0] after division
    r_comp = max(0.0, min(1.0, rgb_color.r / 255.0))
    g_comp = max(0.0, min(1.0, rgb_color.g / 255.0))
    b_comp = max(0.0, min(1.0, rgb_color.b / 255.0))
    
    # Return as a list [R, G, B, A] with alpha = 1.0
    return [r_comp, g_comp, b_comp, 1.0]

def colorArray01_3_OfRgb(rgb_color: rgb) -> List[float]:
    """Converts an rgb object (RGBA, 0.0-255.0) to a Krita color component array (RGBA, 0.0-1.0), with alpha forced to 1.0."""
    if not isinstance(rgb_color, rgb):
        raise TypeError("Input must be an rgb object")
        
    # Convert R, G, B from 0-255 range to 0.0-1.0 range
    # Clamp values to ensure they are within [0.0, 1.0] after division
    r_comp = max(0.0, min(1.0, rgb_color.r / 255.0))
    g_comp = max(0.0, min(1.0, rgb_color.g / 255.0))
    b_comp = max(0.0, min(1.0, rgb_color.b / 255.0))
    
    # Return as a list [R, G, B, A] with alpha = 1.0
    return [r_comp, g_comp, b_comp]

def colorArray255_3_OfRgb(rgb_color: rgb) -> List[float]:
    """Converts an rgb object (RGBA, 0.0-255.0) to a Krita color component array (RGBA, 0.0-1.0), with alpha forced to 1.0."""
    if not isinstance(rgb_color, rgb):
        raise TypeError(f"Input must be an rgb object but it is {rgb_color}")
        
    # Convert R, G, B from 0-255 range to 0.0-1.0 range
    # Clamp values to ensure they are within [0.0, 1.0] after division
    r_comp =  rgb_color.r
    g_comp = rgb_color.g
    b_comp =  rgb_color.b
    
    # Return as a list [R, G, B, A] with alpha = 1.0
    return [r_comp, g_comp, b_comp]


def rgbOfManagedColor(c):
    co = c.components()
    return rgb(float(co[0] * 255.0), float(co[1] * 255.0), float(co[2] * 255.0), 255.0)
