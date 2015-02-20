#!/usr/bin/env python2
#
# wmctrl.py
#
# * developed by Benjamin Hutchins and Ryan Stringham
# * forked and edited by Jakob Lombacher
#   an attempt to make linux more usable.
# * forked and edited by Markus Schuetz to allow some more options
#
#
# MIT License
#
# https://github.com/jlombacher/wmctrl.git
#
# forked from: https://github.com/benhutchins/wmctrl

import sys
import os
import subprocess
import re
import argparse
import locale
import bisect

# Customizable variables
window_title_height = 0#21
window_border_width = 1
panel_height = 30
leway_percentage = .05

debug = False
encoding = locale.getdefaultlocale()[1]


def getCommandOutput(command):
    output =  subprocess.check_output(command, shell=True).decode(encoding)[0:-1]
    return output


def getMonitorConfig():
    """
    Returns ordered list of Monitor configuration as dict.

    The list is order by the x position from left to right.
    At the moment no support for "upper" Monitors

    returns a list of dict
    [ {'size_x': ..., 'size_y': ... , 'pos_x': ..., 'pos_y': ...} ...]
    """
    xrandr_output = getCommandOutput('xrandr').split('\n')
    expr = re.compile('\S+ connected (?P<size_x>\d+)x(?P<size_y>\d+)\+'
                      '(?P<pos_x>\d+)\+(?P<pos_y>\d+).*')
    mon = [m.groupdict() for m in [expr.match(l) for l in xrandr_output]
           if m is not None]

    for m in mon:
        for k in m.keys():
            m[k] = int(m[k])
    mon.sort(key=lambda x:  x['pos_x'])
    return mon


def initialize():
    """
    Get window and desktop information

    return (desktop,width,height, absoluteX, absoluteY, cW, cH, cMh, cMv)
    """
    desk_output = getCommandOutput("wmctrl -d").split("\n")
    #desk_list = [line.split()[0] for line in desk_output]

    current =  next(filter(lambda x: x.split()[1] == "*" , desk_output)).split()

    desktop = current[0]
    width  = current[8].split("x")[0]
    height = current[8].split("x")[1]
    orig_x = current[7].split(",")[0]
    orig_y = current[7].split(",")[1]

    # this is unreliable, xdpyinfo often does not know what is focused, we use xdotool now
    #window_id = commands.getoutput("xdpyinfo | grep focus | grep -E -o 0x[0-9a-f]+").strip()
    #window_id = hex(int(window_id, 16))

    current = getCommandOutput("xwininfo -id $(xdotool getactivewindow)").split("\n")
    absoluteX = int(current[3].split(':')[1])
    absoluteY = int(current[4].split(':')[1])
    relativeX = int(current[5].split(':')[1])
    relativeY = int(current[6].split(':')[1])
    cW = int(current[7].split(':')[1])
    cH = int(current[8].split(':')[1])

    #determine maximized state
    current = getCommandOutput("xwininfo -wm -id $(xdotool getactivewindow)")
    cMh = current.find('Maximized Horz') >= 0
    cMv = current.find('Maximized Vert') >= 0
    #Korrekturfaktor, warum auch immer
    absoluteX -= 1
    absoluteY -= 22
    return (desktop, width, height, absoluteX, absoluteY, cW, cH, cMh, cMv)


# calculate these
monitors = getMonitorConfig()
(junk, max_width, max_height, cX, cY, cW, cH, cMh, cMv) = initialize()
max_width = int(max_width)
max_height = int(max_height)

def get_current_monitor():
    """
    Determines monitor of current window
    """
    cMonId = 0
    for i in reversed(range(len(monitors))):
        m =monitors[i]
        if cX > m['pos_x']-5 and\
           cY > m['pos_y']-5:
            cMonId = i
            break;
    m = monitors[cMonId]
    if debug:
        print("Current Monitor ID: ", cMonId)
    return cMonId, m

def within_leway(w):
    global cW
    global leway_percentage

    leway = w * leway_percentage

    if cW - leway < w and cW + leway > w:
        return True
    else:
        return False

def is_active_window_maximized():
    return False

def maximize():
    unmaximize()

    command = "wmctrl -r :ACTIVE: -b add,maximized_vert,maximized_horz"
    os.system(command)

def maximize_vert():
    unmaximize()

    command = "wmctrl -r :ACTIVE: -b add,maximized_vert"
    os.system(command)

def maximize_horz():
    unmaximize()

    command = "wmctrl -r :ACTIVE: -b add,maximized_horz"
    os.system(command)


def unmaximize():
    command = "wmctrl -r :ACTIVE: -b remove,maximized_vert,maximized_horz,hidden,below"
    os.system(command)


def minimize():
    unmaximize()

    #command = "wmctrl -r :ACTIVE: -b add,below"
    #os.system(command)


def move_active(x,y,w,h):
    unmaximize()

    if debug:
        print("move to: ", x, y, w, h)

    # Sanity check, make sure bottom of window does not end up hidden
    if (y+h) > max_height:
        h = max_height - y

    if debug:
        print(x, y, w, h)

    command = "wmctrl -r :ACTIVE: -e 0," + str(int(x)) + "," + str(int(y))+ "," + str(int(w)) + "," + str(int(h))
    os.system(command)

    command = "wmctrl -a :ACTIVE: "
    os.system(command)

def move(direction = 'right', fraction = 2):
    """Resize  Window to half, and move it right or left"""

    [cMonId, m] = get_current_monitor()

    if direction == 'right' or direction == 'left':
        horizontal = True
        oldVal = cX
        pos = 'pos_x'
        size = 'size_x'
        lowerBound = 'left'
        upperBound = 'right'
    else:
        horizontal = False
        oldVal = cY
        pos = 'pos_y'
        size = 'size_y'
        lowerBound = 'up'
        upperBound = 'down'


    binboundaries = [];
    boundaryMonitor = [];
    for monitor in monitors:
        for i in range(fraction):
            binboundaries.append(monitor[pos] + round(i * monitor[size] / fraction))
            boundaryMonitor.append(monitor)

    if direction == upperBound:
        calcbin = bisect.bisect_right(binboundaries, oldVal + 20)
        binidx = min(calcbin, len(binboundaries)-1);
    elif direction == lowerBound:
        calcbin = bisect.bisect_left(binboundaries, oldVal - 20) - 1;
        binidx = max(calcbin, 0);

    newVal = binboundaries[binidx];
    m = boundaryMonitor[binidx]

    if debug:
        print('newVal: ')
        print(newVal)
        print('calcbin: ')
        print(calcbin)
        print('Boundaries: ')
        print(binboundaries)


    if horizontal:
        x = newVal
        y = m['pos_y']
        w = m['size_x']/fraction - window_border_width
        h = m['size_y'] - window_title_height
        move_active(x, panel_height, w, h)
        maximize_vert()
    else:
        x = m['pos_x']
        y = newVal
        w = m['size_x'] - window_border_width
        h = m['size_y']/fraction
        move_active(x, y, w, h)
        maximize_horz()

def next_monitor(reverse=False):
    """
    Moves Window to next monitor
    """
    [id, m] = get_current_monitor()
    if reverse:
        nid = (id-1)%len(monitors)
    else:
        nid = (id+1)%len(monitors)
    nm = monitors[nid]

    xrel = float(cX-m['pos_x'])/m['size_x']
    yrel = float(cY-m['pos_y'])/m['size_y']
    x = max(xrel * nm['size_x'] + nm['pos_x'], nm['pos_x'])
    y = yrel * nm['size_y'] + nm['pos_y']
    w = cW * nm['size_x']/m['size_x']
    h = cH * nm['size_y']/m['size_y']

    move_active(x,y,w,h)

    if cMv and cMh:
        maximize()
    elif cMv:
        maximize_vert()
    elif cMh:
        maximize_horz()

def maxFun(args):
    if (args.unmaximize):
        unmaximize()
    else:
        maximize()

def smonFun(args):
    if(args.direction == 'next'):
        next_monitor()
    elif(args.direction == 'prev'):
        next_monitor(reverse=True)

def moveFun(args):
    move(args.direction, args.fraction)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='winmove', description='Small tool to move and tile the current windows. Use it by registering shortcuts.')
    parser.add_argument('--verbose','-v', action='store_true', default=False,
                        help="Verbose: Enable debug output" )

    subparsers = parser.add_subparsers();

    sub = subparsers.add_parser('move', help='Moves the window horizotally while maximizing it vertically')
    sub.add_argument('--direction', '-d', choices=['left', 'right', 'up', 'down'], default='right', help="Movement direction")
    sub.add_argument('--fraction', '-f', choices=[2, 3, 4, 5, 6, 7, 8], type=int, default=2, help="Width/Height of window  resized to 1/FRACTION")
    sub.set_defaults(func=moveFun)

    sub = subparsers.add_parser('smon', help='Switches window to other monitors')
    sub.add_argument('--direction', '-d', choices=['next', 'prev'], default='next', help='Selects the monitor to switch to')
    sub.set_defaults(func=smonFun)

    sub = subparsers.add_parser('max', help='(Un-)Maximizes window')
    sub.add_argument('--unmaximize', '-u', help='Unmaximize', action='store_true', default=False)
    sub.set_defaults(func=maxFun)

    args = parser.parse_args()
    debug = args.verbose
    if debug:
        print ("Arguments: ", args)
        print ({'junk': junk, 'max_width': max_width, 'max_height': max_height,
               'cX': cX, 'cY': cY, 'cW': cW, 'cH': cH, 'cMh': cMh, 'cMv': cMv})
        print (monitors)

    args.func(args)
