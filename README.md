wmctrl.py
======

A simple Python script to add some basic tiling support to Linux.
This is useful for example for old XFCE installations without tiling.

The fraction based resizing of the window is especially useful for big wide-screen displays (21:9).

This application relies on wmctrl, ensure you have it installed before use.

For Debian-based distros use:
    sudo apt-get install wmctrl xdotool x11-xserver-utils

For Arch linux use:
   sudo pacman -S wmctrl xorg-utils xdotool

Add keyboard shortcuts calling a command from the list below like:

Get help:
    python winmove.py --help
    python winmove.py move --help
    
Resize active window to one half of the current screen:
    python winmove.py move --direction left
    python winmove.py move --direction down
    
Resize active window to one fourth of the current screen:
    python winmove.py move --direction up --fraction 4
    
Maximize and unmaximize the active window:
    python winmove.py max
    python winmove.py max --unmaximize

Move window to other next screen:
    python winmove.py smon --direction next

Available commands are:

    command           | description                                                   | recommended shortcut
    --------------------------------------------------------------------------------------------------------
    left                Position active window on the left-half of your desktop.        Super+Left
    right               Position active window on the right-half of your desktop        Super+Right
    up                  Toggle maximized state of active window (TODO)                  Super+Up
    down                Demaximize window if maximized, if not, minimize window.        Super+Down
    shift-left          Position window to take up 1/3 or 2/3 of desktop on left.       Super+Shift+Left
    shift-right         Position window to take up 1/3 or 2/3 of desktop on right.      Super+Shift+Right
    shift-up            Position a window to take up 1/2 of desktop on top.             Super+Shift+Up
    shift-down          Position a window to take up 1/2 of desktop on bottom.          Super+Shift+Down
