winmove.py
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

Recommended shortcuts are: (Super is the "windows key". Mnemonic: "shift window to the left" => Shift+Windows+Left)

    Description                                                   | Recommended shortcut
    --------------------------------------------------------------------------------------------------------
    Position active window on the left-half of your desktop.        Super+Shift+Left
    Position active window on the right-half of your desktop        Super+Shift+Right
    Position active window on the upper-half of your desktop.       Super+Shift+Up
    Position active window on the lower-half of your desktop.       Super+Shift+Down
    Move to next screen                                             Super+Shift+n
    Move to previous screen                                         Super+Shift+p
    Maximize window.                                                Super+Up
    Unmaximize window.                                              Super+Down
