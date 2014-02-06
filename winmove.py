#!/usr/bin/python
#
# wmctrl.py
#
# developed by Benjamin Hutchins and Ryan Stringham
#
# forked and edited by Jakob Lombacher
#
# an attempt to make linux more usable.
#
# MIT License
#
# https://github.com/jlombacher/wmctrl.git
#
# forked from: https://github.com/benhutchins/wmctrl


import sys
import os
import commands
import re
import argparse

# Customizable variables
window_title_height = 0#21
window_border_width = 1
panel_height = 30
leway_percentage = .05

debug = False

def getMonitorConfig():
    """ 
    Returns ordered list of Monitor configuration as dict.
    
    The list is order by the x position from left to right.
    At the moment no support for "upper" Monitors

    returns a list of dict
    [ {'size_x': ..., 'size_y': ... , 'pos_x': ..., 'pos_y': ...} ...]
    """
    xrandr_output = commands.getoutput('xrandr').split('\n')
    expr = re.compile('\S+ connected (?P<size_x>\d+)x(?P<size_y>\d+)\+'
                      '(?P<pos_x>\d+)\+(?P<pos_y>\d+).*')
    mon = [m.groupdict() for m in [expr.match(l) for l in xrandr_output]
           if m is not  None]

    for m in mon:
        for k in m.keys():
            m[k] = int(m[k])
    mon.sort(key=lambda x:  x['pos_x']  )
    return mon

def initialize():
    """
    Get window and desktop information

    return (desktop,width,height, absoluteX, absoluteY, cW, cH, cMh, cMv)
    """
    desk_output = commands.getoutput("wmctrl -d").split("\n")
    desk_list = [line.split()[0] for line in desk_output]

    current =  filter(lambda x: x.split()[1] == "*" , desk_output)[0].split()

    desktop = current[0]
    width =  current[8].split("x")[0]
    height =  current[8].split("x")[1]
    orig_x =  current[7].split(",")[0]
    orig_y =  current[7].split(",")[1]

    # this is unreliable, xdpyinfo often does not know what is focused, we use xdotool now
    #window_id = commands.getoutput("xdpyinfo | grep focus | grep -E -o 0x[0-9a-f]+").strip()
    #window_id = hex(int(window_id, 16))

    current = commands.getoutput("xwininfo -id $(xdotool getactivewindow)").split("\n")
    absoluteX = int(current[3].split(':')[1])
    absoluteY = int(current[4].split(':')[1])
    relativeX = int(current[5].split(':')[1])
    relativeY = int(current[6].split(':')[1])
    cW = int(current[7].split(':')[1])
    cH = int(current[8].split(':')[1])

    #determine maximized state
    current = commands.getoutput("xwininfo -wm -id $(xdotool getactivewindow)")
    cMh = current.find('Maximized Horz') >= 0
    cMv = current.find('Maximized Vert') >= 0
    #Korrekturfaktor, warum auch immer
    absoluteX -= 1
    absoluteY -= 22
    return (desktop,width,height, absoluteX, absoluteY, cW, cH, cMh, cMv)


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
        print "Current Monitor ID: ", cMonId
    return cMonId,m

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
        print "move to: ", x, y, w, h

    # Sanity check, make sure bottom of window does not end up hidden
    if (y+h) > max_height:
        h = max_height - y

    if debug:
        print x, y, w, h

    command = "wmctrl -r :ACTIVE: -e 0," + str(int(x)) + "," + str(int(y))+ "," + str(int(w)) + "," + str(int(h))
    os.system(command)

    command = "wmctrl -a :ACTIVE: "
    os.system(command)

def half(mvright = True):
    """Resize  Window to half, and move it right or left"""

    [cMonId, m] = get_current_monitor()

    if mvright:
        if cX < (m['pos_x'] + m['size_x']/4) or (len(monitors) - 1) == cMonId:
            # move to rigth half
            x = m['pos_x'] + m['size_x']/2
        else:
            m = monitors[cMonId+1]
            x = m['pos_x']
    else: 
        if (cX >= (m['pos_x'] + m['size_x']/4) or 0 == cMonId) and cX < (m['pos_x'] + m['size_x']*3/4) :
            # move to left half
            x = m['pos_x']
        else:
            m = monitors[max(cMonId-1,0)]
            x = m['pos_x'] + m['size_x']/2
        
    y = m['pos_y']
    w = m['size_x']/2
    h = m['size_y'] - window_title_height

    move_active(x, panel_height, w - window_border_width, h)
    maximize_vert()


#TODO
def up(shift = False):
    if not shift:
        if is_active_window_maximized():
            unmaximize()
        else:
            maximize()

    else:
        w = max_width - window_border_width
        h = max_height/2 - window_title_height - window_border_width
        move_active(0, panel_height, w, h)
 
#TODO
def down(shift = False):
    if not shift:
        if is_active_window_maximized():
            unmaximize()
        else:
            minimize()

    if shift:
        w = max_width - window_border_width
        h = max_height/2 - window_title_height - window_border_width
        y = max_height/2 + window_title_height + window_border_width
        move_active(0, y, w, h)

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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='tool to move windows')
    parser.add_argument('-v', action='store_true', default=False, 
                        help="Verbose: Enables debug output" )
    subparsers = parser.add_subparsers()
    sub = subparsers.add_parser('half-left', help='resize window to half to the left')
    sub.set_defaults(func=lambda:half(False))
    sub = subparsers.add_parser('half-right',  help='resize window to half to the right')
    sub.set_defaults(func=lambda:half(True))
    sub = subparsers.add_parser('next', help='moves window to next monitor')
    sub.set_defaults(func=next_monitor)
    sub = subparsers.add_parser('prev', help='moves window to prev monitor')
    sub.set_defaults(func=lambda:next_monitor(reverse=True))
    sub = subparsers.add_parser('max', help='maximize window')
    sub.set_defaults(func=maximize)
    sub = subparsers.add_parser('unmax', help='unmaximize window')
    sub.set_defaults(func=unmaximize)


    
    args = parser.parse_args()
    debug=args.v
    if debug:
        print "args: ", args
        print {'junk': junk, 'max_width': max_width, 'max_height': max_height, 
               'cX': cX, 'cY': cY, 'cW': cW, 'cH': cH, 'cMh': cMh, 'cMv': cMv}
        print monitors

    args.func()
