# Table of Contents

1.  [ColorPlus](#colorplus)
2.  [Features](#features)
    * [Spectral color mixing logic](#spectral-color-mixing-logic)
    * [Auto-mix](#auto-mix)
    * [Dirty brush](#dirty-brush)
    * [Quick color switching (Previous Color)](#quick-color-switching-previous-color)
    * [Smart color picker](#smart-color-picker)
    * [Color Mixing shortcut](#color-mixing-shortcut)
    * [Color post-correction](#color-post-correction)
        * [Modify stroke transparency](#modify-stroke-transparency)
    * [Watercolor simulation](#watercolor-simulation)
    * [Smart color history](#smart-color-history)
    * [Main docker](#main-docker)
    * [Full-screen preview](#full-screen-preview)
    * [Saving and restoring windows and their positions](#saving-and-restoring-windows-and-their-positions)
    * [Exporting layers and coordinates](#exporting-layers-and-coordinates)
    * [Window autofocus](#window-autofocus)
3.  [INSTALLATION](#installation)
    * [On Windows](#on-windows)

# ColorPlus

ColorPlus is a plugin for Krita that adds the following features to Krita:

# Features

## Spectral color mixing logic

This means that colors mix realistically. For example, when you mix two colors, yellow mixed
with blue produces green; blue with white produces a bright and vibrant blue; etc.

This realistic mixing occurs in all ColorPlus features: manual mixing, auto-mix, dirty brush.

Thanks to Ronald van Wijnen for the library used for color mixing
according to the Kubelka-Munk theory!

## Auto-mix

If you activate this mode, every brush stroke you make automatically
gets dirty with the color that is already present on the canvas. The
proportion in which it gets dirty is configurable with a slider.


Each stroke gets dirty independently. That is, with each stroke, the brush is
first  "auto-cleaned", then dirtied with the new color on the canvas. (If you
want  the brush to remain dirty between strokes, you can use the dirty brush.
See the dedicated section).

So, with each stroke, you will introduce a bit of color. By continuing to brush, it
will  eventually reach the target color. (Provided the mixing radius is low enough,
otherwise you will never reach it).

Differences with Krita's Color Smudge Engine:

    Krita's Color Smudge mixes colors without spectral logic, thus producing
    faded colors: for example, blue + yellow = gray, not green.

    Krita's  Color Smudge Engine works with the concept of "color rate", meaning your chosen color
    (foreground  color)  is  gradually introduced during the stroke. You cannot have a stroke that
    from the beginning has your foreground color, but dirtied by a fixed percentage with the color
    on the canvas. This produces a visually very different effect.

    Krita's Color Smudge Engine tends to produce blurry edges, because
    it uses a build-up type algorithm and not a glaze type.


Note: the stroke does not get dirty with the white of the canvas, but only
with the color actually deposited on the canvas. This setting is optional.

This engine is called "auto-mix" because each stroke "automatically
mixes" with the background color.

Auto-mix works with any brush, even those using the pixel engine. So you don't have
to give up the dual brush, which is currently not supported by Krita's color smudge
engine. And you get sharp edges.


Note: this mode, if activated, fills Krita's color history with intermediate colors, produced
by  the  "dirtying" of the brush. This makes Krita's color history unusable. For this reason,
ColorPlus offers its own color history, which does not show these "intermediate" colors.

To activate auto-mix, click in the ColorPlus docker: https://i.imgur.com/COOOjwa.png

There is also the slider that controls how much it takes from the canvas with each stroke.

## Dirty brush

In this mode, every time you make a stroke, your brush gets a little dirty with the
color on the canvas. The amount it gets dirty is configurable with a slider.

Difference with auto-mix: in dirty brush, the first stroke does not get dirty, but has the
pure color you chose. Only subsequent strokes get dirty based on the color that was on the
canvas  in  previous  strokes. Instead, in auto-mix, even the first stroke gets dirty. But
subsequent strokes forget how the previous stroke got dirty.

Another  difference is that, with auto-mix, each stroke brings you closer and closer to the
target color (i.e., the foreground color). Instead, with the dirty brush, each stroke takes
you further and further away from the foreground color.

Note: There is a shortcut to clean the brush, which is the same one used for the Dry Paper
function. (If the brush is dirty, besides creating a new layer, it also cleans the brush).

Note: the stroke does not get dirty with the white of the canvas, but only
with the color actually deposited on the canvas. This setting is optional.

Note: this mode, if activated, fills Krita's color history with intermediate colors, produced
by  the  "dirtying" of the brush. This makes Krita's color history unusable. For this reason,
ColorPlus offers its own color history, which does not show these "intermediate" colors.

To activate the Dirty Brush, use the ColorPlus docker: https://i.imgur.com/RDHdyWS.png

## Quick color switching (Previous Color)

There is a shortcut with which you can easily switch between two colors,
instantly switching to the color used before the current one.

Most of the time, for my painting style, I continuously switch between two colors,
so this function is essential to avoid mouse travel to click in the color history.

With the same shortcut, pressed twice in a row, you can switch to
the second to last color used, and so on.

I recommend assigning this shortcut to the V key: https://i.imgur.com/vpKxHaf.png


## Smart color picker

You have a shortcut to color pick the color under the mouse, without holding down ALT or CTRL.

There  is a version of the shortcut that, in addition to color picking, also creates
a new layer. I recommend using that one. It is advisable to create a new layer every
time you change color, to simulate the watercolor effect (see dedicated section).

I recommend associating this shortcut with the C button: https://i.imgur.com/zC2rmom.png

## Color Mixing shortcut

You  have a shortcut to mix the current color (the foreground color) with a
portion of the color on the canvas. In other words, with this shortcut, you
change the current color bringing it closer to the color the mouse is over.

For example, if you have the color blue, and the mouse is over the color yellow,
with this shortcut you can add 50% yellow to blue, obtaining green.

The amount of color you pick from the canvas is configurable with
the "mix level" slider in the ColorPlus docker.

An  important  option is that, when you mix a color to make it more similar to another,
the plugin is able to automatically change also the stroke you just made, giving it the
new color. This function is called "color post-correction". See the dedicated section.

I recommend associating this function with the F key: https://i.imgur.com/AiehdQv.png

## Color Post-correction

The plugin, in its default mode, automatically creates a layer every time you change color.
This  way, it allows "post-correction" of wrong colors. For example, it often happens that,
after  making  a  stroke, you realize the color is wrong, meaning it harmonizes poorly with
the  background, because it is *too different* from the color that was underneath, on which
you painted. In this case, you can modify the color "on the spot", gradually, until you see
it has become similar enough to the background.

How do you gradually modify the color of the stroke just made? ColorPlus
offers 2 ways to do it:

    1)  Press the "color mix" button (see dedicated section). This, as we said, will
    change the brush color bringing it closer to the color the mouse is over. But it
    will  also  modify the stroke just made (or the strokes just made) bringing them
    closer to the color under the mouse!


    2)  Decrease the transparency of the stroke just made. There is a dedicated shortcut
    for this. Press the shortcut several times and see the strokes just made become more
    transparent.  When  you see they have reached the point where they are no longer too
    different from the color underneath, you stop, and continue painting with that level
    of transparency.

This system (both 1 and 2) is important because it saves you the tedious sequence where you
make  a stroke, realize the color is wrong, press Undo, change color from the selector, try
to brush, realize it's still not right, do undo, then change color again, and so on.

All this is made possible by layers that are created automatically. So you will see
many layers created automatically. This is intentional. Every so often (say every 5
minutes)  you will probably want to merge them all together, which is done with the
cleanup layers button in the ColorPlus docker: https://i.imgur.com/MTQC8l5.png.

You can disable automatic layer creation, but you will lose the ability
to make post-corrections of colors.

Note: The fact that ColorPlus automatically creates layers also allows
the watercolor effect (see dedicated section).


### Modify stroke transparency

We  said there is a shortcut to increase the transparency of the last
stroke (color post-correction). I recommend associating it with the X
key: https://i.imgur.com/K8VM3Mx.png

Usually,  when  you increase the transparency of the stroke because you want to make a
very slight modification, typically the final transparency will be very high. When you
then  want to switch to another color, you also want the transparency of the stroke to
be  automatically  reset to a normal value, otherwise you won't see the new stroke. So
ColorPlus has an "auto-reset opacity" function: https://i.imgur.com/72jOEa5.png

    Set via the slider the level to which you want to reset the stroke transparency,
    every time you change color (I recommend choosing a value between 70% and 85%).


If you notice that the stroke just made contrasts too little with the underlying
color,  there  is  also a shortcut to decrease the transparency of the stroke. I
recommend assigning this function to the S key: https://i.imgur.com/PHRi71L.png



## Watercolor simulation

Watercolor is characterized (among other things!) by the fact that two transparent
strokes  blend together. You don't see the overlap of colors. Instead in Krita, if
you  use a transparent color and make two strokes, you will see the overlap at the
intersection point between them. The strokes do not blend together.

To  solve this problem, ColorPlus makes the layer transparent, not your
brush (which is 100% opaque). This way the brush will seem transparent,
but  at  the same time you will see strokes that blend together without
overlap. ColorPlus takes care of automatically creating layers when you
change color, so that strokes with the same color blend together, while
remaining transparent.

Note: The fact that ColorPlus automatically creates layers also allows
color post-correction (see dedicated section).

When you want to manually create a layer, just press the "dry paper" shortcut, which
I recommend associating with the D button: https://i.imgur.com/A2hIoeT.png



## Smart color history

You have a visual color history, which shows you recent colors, to which you can
switch by clicking directly on them. It is similar to Krita's color history, but
it doesn't show you all the colors produced by automix and dirty brush, but only
the original ones that you selected from Krita's color selector.


The color history is a docker that you can activate like this:

Settings -> Dockers -> ColorPlus color history.

## Main docker

ColorPlus has a main docker that contains all the settings you need to change
frequently. To activate it: from the menu: Settings -> Dockers -> ColorPlus

Here is a screenshot: https://i.imgur.com/ISNM3wA.png

Note also that in the ColorPlus menu there are some functions that
are missing in the docker: https://i.imgur.com/bunL1Wt.png

## Full-screen preview

There is a shortcut that shows your current painting in full screen, temporarily hiding all
floating  dockers. If pressed again, it restores the working layout, with floating dockers,
docked dockers, and the reference window if any.


I suggest assigning this function to the button immediately above the TAB button,
i.e., the first button on the keyboard: https://i.imgur.com/BY7BF2O.png

## Saving and restoring windows and their positions

ColorPlus provides a simple method for saving and restoring work sessions: it saves
and restores the work layout, i.e., which files are open, and in what position they
are located. You find two menu items for this: https://i.imgur.com/4ttc0XP.png

# Exporting layers and coordinates

ColorPlus offers a menu item that exports all layers whose name ends with -png, .png, -jpg or
.jpg. It also exports a .json file containing the coordinates of each layer within the image.

This is useful if you are developing a game or application that needs to
load backgrounds and characters, and know where to place the characters.

The function also exports layer groups. If you have a group with a name ending for example
with .png, it will export an image containing the merge of all layers in the group.

The .json and layers are saved in your Documents folder.

## Window autofocus

Autofocus means that the window you move the mouse over is automatically activated.

Some ColorPlus functions need the autofocus option to remain active.
For example, without it, automatic layer creation will not work.

# INSTALLATION

On Windows:

Close Krita. Go to the folder

C:\Users\yourname\AppData\Roaming\krita\pykrita

and copy the recent_color.desktop file and the recent_color folder here:
https://i.imgur.com/5SoFMpu.png

Then go to the folder

C:\Users\yourname\AppData\Roaming\krita\actions

and copy the .action files here: https://i.imgur.com/PR2xWr0.png

(before copying them, it would be better to delete the .action files that are already
there, but be sure not to delete action files that are from other plugins!)

Then start Krita. From the menu: Settings -> configure Krita. Python plugin manager.

Activate the plugin by checking it here: https://i.imgur.com/EDr7vdd.png

Then reassign the shortcuts here: https://i.imgur.com/7J5ZFXe.png

(In the screenshot above you can also see which keys I recommend
assigning to the various functions)