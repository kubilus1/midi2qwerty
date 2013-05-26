#!/usr/bin/env python
#
# Midi2Key - Convert midi commands into keystrokes.
#
#  Matt Kubilus 2013
#

import sys
import shelve

from subprocess import call
from optparse import OptionParser

NOTES=['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']

class Midi2Key(object):
    def __init__(self, midi_map, device="/dev/midi1", command="xte '%s'"):
        self.midi_map = midi_map
        self.device = device
        self.command = command

    def learn_keys(self):
        with open(self.device,'r') as h:
            while True:
                status = ord(h.read(1))
                note = ord(h.read(1))
                velocity = ord(h.read(1))

                if status != 0x80:
                    continue

                print "%x %x %x" % (status, note, velocity)
                print "Press a key:", 
                inkey = sys.stdin.readline()
                print "Pressed:(%s)" % inkey[0]
                if inkey[0] == '\n':
                    break
                
                midi_map[note] = inkey[0]


    def capture_keys(self):
        with open(self.device,'r') as h:
            while True:
                status = ord(h.read(1))
                note = ord(h.read(1))
                velocity = ord(h.read(1))
                
                if status == 0x80:
                    print "Up: %x %x %x" % (status, note, velocity)
                    outkey = midi_map.get(note)
                    if outkey:
                        cmd = "xte 'keyup %s'" % outkey
                        call(cmd, shell=True)
                elif status == 0x90:
                    print "Down: %x %x %x" % (status, note, velocity)
                    outkey = midi_map.get(note)
                    if outkey:
                        cmd = "xte 'keydown %s'" % outkey
                        call(cmd, shell=True)


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option(
            "-l",
            "--learn",
            default = False,
            action = "store_true",
            dest = "learn",
            help = "Learn key presses"
    )
    parser.add_option(
            "-d",
            "--device",
            default = "/dev/midi1",
            dest = "device",
            action = "store",
            help = "Midi device to use."
    )
    parser.add_option(
            "-c",
            "--command",
            default = "xte 'key %s'",
            dest = "command",
            action = "store",
            help = "Control command to use."
    )
    parser.add_option(
            "-s",
            "--show",
            dest = "show",
            action = "store_true",
            default = False,
            help = "Show command map."
    )
    opts, args = parser.parse_args()

    data = shelve.open('midi_map')
    if not data.has_key('midi_map'):
        midi_map = {}
    else:
        midi_map = data['midi_map']

    try:
        if(opts.show):
            midi_map = data['midi_map']
            print "CODE    KEY    NOTE"
            print "-------------------"
            for key, value in midi_map.items():
                print "0x%x    %s     " % (key, value),
                print NOTES[key % 12],
                print (key/12)-1

            sys.exit(0)

        if(opts.learn):
            m2k = Midi2Key(midi_map, opts.device, opts.command)
            try:
                m2k.learn_keys()
            finally:
                data['midi_map'] = m2k.midi_map
        else:
            midi_map = data['midi_map']
            m2k = Midi2Key(midi_map, opts.device, opts.command)
            m2k.capture_keys()
    finally:
        data.close()


