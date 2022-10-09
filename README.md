This plugin contains several actions that can be assigned to different shortcuts. 

Here is a video to illustrate all the functions: https://www.youtube.com/watch?v=Muz3o2Wuoi4

Dry paper (default shortcut: D)
====================================

Basically it allows watercolor style. It's difficult to explain, so please refer to the video here: https://www.youtube.com/watch?v=Muz3o2Wuoi4

Basically, with this technique, colors merge together instead of overlapping, until you decide to dry the paper. 

More precisely: you can paint with a semi-transparent brush. If you lift the pen, and make another stroke, you don't see the "overlap". The strokes "merge together". Only when you press a shortcut to "dry the paper", subsequent strokes overlap. 

Note: you need to have two layers. Put the two layers in a group. These need to be the only layers in that group. The top layer needs to be partially transparent (typically from 50% to 70%). You will only paint on the top layer. You need to use a completely opaque brush. In particular, the brush should not have pressure assigned to opacity, or to flow. (I suggest pressure size).

Most of the time, I suggest to use the action "dry paper and pick color at the same time". See below.


LastColor (defaut shortcut: V)
====================

This action switches to the previously used color. This is equivalent to pressing the color on top of the color history.

I suggest binding it to the V key, replacing the default behavior.

Why is this action useful? Typical scenario: most of the time, I paint by combining two colors: a dark and a light color. The goal is to mix them in the correct proportion, to obtain the right contrast and texture. First, there is a "search" phase , where I am searching for the two colors. Once I  found these colors, the second phase starts, where I need to quickly swap between them, to create the correct proportion and texture. I could use the color history to toggle between them, clicking the color on top of the list, but there is a lot of mouse travel involved. It's better to have a shortcut that switches to the last color, allowing me to constantly toggle between them. 

Question: what is the difference with pressing X (swap foreground and background color)? This too allows you to quickly toggle between two colors. Answer: here is a typical scenario: You ctrl+click  to pick a light color. You paint for a while with it. Then you realize you need more contrast. You Ctrl+click to pick a dark color. You paint for a while with it. Then you realize you exaggerated, and you need some more light color. With this plugin, you press D, and you have your light  color back. Pressing X wouldn't help, because you didn't press X before CTRL+click the second time. Because you didn't know you'd need the light color again. In other words, the default behavior of X requires too much foresight. With this action, if you realize late you need the previous color, you just press D. 

What is the difference with pressing the color on top of the history? None, except there is a lot of mouse travel involved.


MixColor  (default shortcut: X)
==========

It mixes the foreground color with the color under cursor (on the canvas). , By default, it picks 45% of the canvas color and leaves 55% of the current foreground color.

The amount of color it picks (45% by default) can be changed with other shortcuts in this plugin.  ("increase mixing" and "decrease mixing")

Usage: when you paint, you realize you have picked a color that's too different from the color you are overwriting. You are creating too much contrast. Then, you press X and make your foreground color more similar to the destination.

Special usage: in conjunction with the PickColor action (bound to the C key, see below). You press C to pick a color, then move the mouse/pen, and press X to introduce a bit of another color. Then paint.



Pick Color (default shortcut: F)
==========

This is an easier way to pick a color from the canvas, easier than CTRL+click. You just position the mouse/pen on a pixel and press F. No need to hold a key. Once you get used to it, you'll never want to go back. Especially useful for pixel art, where it's clear what color your cursor is hovering.

Originally, this function was assigned to C by default, which is easier to press than F. Now I suggest to use "dry paper and pick color", so this action is assigned to F by default. If you prefer to use "pick" instead of "dry and pick" (for example because you don't use the watercolor system with the dry paper technique), you may want to reassign this to C.




Dry paper and pick color (default shortcut: C)
===================

If you are using a watercolor style, usually when you change color you also want to dry the paper, so I created this shortcut that does both things at once. It is like pressing F and D in sequence.


INSTALLATION
=================

In Windows:

exit Krita. Enter  the folder

C:\Users\yourname\AppData\Roaming\krita\pykrita

and copy here the .desktop file and the recent_color folder:  https://i.imgur.com/5SoFMpu.png

Then enter the folder 

C:\Users\yourname\AppData\Roaming\krita\actions

and copy the .action files here: https://i.imgur.com/zspj4uc.png

Then start Krita. Activate the plugin by checking it here: https://i.imgur.com/CKH6wDs.png

Then reassign the shortcuts here: https://i.imgur.com/14IRqxa.png

