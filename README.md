This plugin adds the following features to Krita:

# Spectral Color Mixing Logic

This means that when you mix two colors (which can be done in various ways, see below), yellow
mixed with blue produces green; blue with white produces a bright and vibrant blue; etc.


# Auto-mix

If you enable this mode, each brushstroke automatically gets "dirty" with the color already
present on the canvas. The proportion of dirtiness is configurable with a slider.


Each brushstroke gets dirty independently. That is, with each stroke, the brush is first
"auto-cleaned," then dirtied with the new color on the canvas. (If you want the brush to
remain dirty between strokes, you can use the dirty brush. See the dedicated section).

Differences with Krita's Color Smudge Engine:

    Krita's Color Smudge mixes colors without spectral logic, thus producing
    pale colors: for example, blue + yellow = gray, not green.

    Krita's Color Smudge Engine works with the concept of "color rate,"
    meaning your chosen foreground color is gradually introduced during
    the  stroke. You cannot have a stroke that, from the beginning, has
    your foreground color but is dirtied by a fixed percentage with the
    canvas color. This produces a visually very different effect.

    Krita's Color Smudge Engine tends to produce blurry edges, because
    it uses a build-up type algorithm, not a glaze type.


Note: The stroke does not get dirty with the white of the canvas, but only
with the color actually deposited on the canvas. This setting is optional.

This engine is called "auto-mix" because each stroke "automatically
mixes" with the background color.

Auto-mix  works with any brush, including those using the pixel engine. So
you don't have to give up the dual brush, which is currently not supported
by Krita's color smudge engine. And you get sharp edges.


Note: This mode, if activated, fills Krita's color history with intermediate colors produced by
the  brush  "dirtiness."  This makes Krita's color history unusable. For this reason, ColorPlus
offers its own color history, which does not show these "intermediate" colors.

# Dirty brush

In this mode, every time you make a stroke, your brush gets a little dirty with
the color on the canvas. The amount of dirtiness is configurable with a slider.

Difference  with auto-mix: In the dirty brush, the first stroke does not get dirty, but
has the pure color you chose. Only subsequent strokes get dirty based on the color that
was on the canvas in previous strokes. In auto-mix, however, even the first stroke gets
dirty. But subsequent strokes forget how the previous stroke got dirty.

Note:  To clean the brush, there is a shortcut, which is the same as
the Previous Color function. (The first time you press it, it cleans
the brush, then starts cycling through previous colors)

Note: The stroke does not get dirty with the white of the canvas, but only
with the color actually deposited on the canvas. This setting is optional.

Note: This mode, if activated, fills Krita's color history with intermediate colors produced by
the  brush  "dirtiness."  This makes Krita's color history unusable. For this reason, ColorPlus
offers its own color history, which does not show these "intermediate" colors.

# Rapid Color Switching

There is a shortcut allowing you to easily switch between two colors,
instantly going back to the color used before the current one.

Most of the time, for my painting style, I continuously switch between two colors,
so this function is essential to avoid mouse travel to click in the color history.

With the same shortcut, pressed twice in a row, you can switch to
the second-to-last used color, and so on.



# Smart Color Picker

You have a shortcut to pick the color under the mouse, without holding ALT or CTRL.

# Color Mixing Shortcut

You have a shortcut to mix the current color (the foreground color) with a portion of
the color on the canvas. For example, if you have blue, and the mouse is over yellow,
with this shortcut you can add 50% of yellow to the blue, obtaining green.

The amount of color picked from the canvas is configurable with a slider.

An important option is that when you mix a color to make it more similar to another, the
plugin  can automatically change the stroke you just made, giving it the new color. This
function is called "color post-correction." See the dedicated section.

# Color Post-Correction 

The plugin, in its default mode, automatically creates a layer every time
you  change color. This allows for "post-correction" of wrong colors. For
example,  it  often  happens  that after making a stroke, you realize the
color is wrong, meaning it harmonizes poorly with the background, because
it is *too different* from the color underneath, on which you painted. In
this  case,  you can modify the color "on the spot," gradually, until you
see that it becomes more similar to the background.

How do you gradually modify the color of the stroke just made? You have 2 ways:

    1) Press the "color mix" button (see dedicated section). Besides mixing the color,
    this shortcut will modify the stroke(s) just made, giving them the new color.


    2) Decrease the transparency of the stroke. There is a dedicated shortcut for
    this.  Press  the shortcut several times and see the strokes just made become
    more  transparent. When you see they have reached the point where they are no
    longer too different from the color underneath, stop, and move on to the next
    stroke.

This is important because it saves you the tedious sequence where
you make a stroke, realize the color is wrong, press Undo, change
the color from the selector, try to paint, realize it's still not
right, press undo, then change the color again, and so on.

All this is made possible by layers that are created automatically. So you will
see many layers created automatically. This is intentional. Every so often (say
every  5  minutes)  you will probably want to merge them all together, which is
done with a dedicated shortcut.

You can disable automatic layer creation, but you will lose the ability
to make post-corrections of colors.

# Smart Color History

You  have a visual color history that shows recent colors, to which you can switch
by  clicking directly on them. It is similar to Krita's color history, but it does
not show all the colors produced by automix and dirty brush, but only the original
ones you selected from Krita's color selector.

# Full-Screen Preview

There  is  a  shortcut  that shows your current image full-screen, temporarily
hiding all floating dockers. If pressed again, it restores the working layout,
with floating dockers, docked dockers, and the reference window, if any.
