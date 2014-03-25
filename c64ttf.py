#!/usr/bin/env python
"""
C64 Character Set to TrueType Converter
Version 1.1

Copyright (c) 2013-2014, A.T.Brask (atbrask[at]gmail[dot]com)
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met: 

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer. 
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution. 

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import argparse
from datetime import date
import getpass
import math
import time
import numpy
import os

from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables import ttProgram
from fontTools.ttLib.tables._c_m_a_p import cmap_format_4, cmap_format_0
from fontTools.ttLib.tables._h_e_a_d import mac_epoch_diff
from fontTools.ttLib.tables._g_l_y_f import Glyph
from fontTools.ttLib.tables.O_S_2f_2 import Panose
from fontTools.ttLib.tables._n_a_m_e import NameRecord

# DATA SECTION

# Map from a subset of C64 PETSCII to ASCII as well as a few Unicode points.
# Not all PETSCII characters can be mapped into Unicode.
# Each tuple is [C64 character generator index, AGL name, [unicode codes]]
# The rest of the C64 glyphs can be included at 0xEE00...0xEFFF by using the
# command line argument --add-all
# The chars are in the C64 character generator order.

CHAR_HI = [[0, "at", [0x40]],
           [1, "A", [0x41]],
           [2, "B", [0x42]],
           [3, "C", [0x43]],
           [4, "D", [0x44]],
           [5, "E", [0x45]],
           [6, "F", [0x46]],
           [7, "G", [0x47]],
           [8, "H", [0x48]],
           [9, "I", [0x49]],
           [10, "J", [0x4a]],
           [11, "K", [0x4b]],
           [12, "L", [0x4c]],
           [13, "M", [0x4d]],
           [14, "N", [0x4e]],
           [15, "O", [0x4f]],
           [16, "P", [0x50]],
           [17, "Q", [0x51]], 
           [18, "R", [0x52]],
           [19, "S", [0x53]],
           [20, "T", [0x54]],
           [21, "U", [0x55]],
           [22, "V", [0x56]],
           [23, "W", [0x57]],
           [24, "X", [0x58]],
           [25, "Y", [0x59]],
           [26, "Z", [0x5a]],
           [27, "bracketleft", [0x5b]],
           [28, "sterling", [0xa3]],
           [29, "bracketright", [0x5d]],
           [30, "arrowup", [0x2191]],
           [31, "arrowleft", [0x2190]],
           [32, "space", [0x20, 0xa0]],
           [33, "exclam", [0x21]],
           [34, "quotedblright", [0x22, 0x201c, 0x201d]],
           [35, "numbersign", [0x23]],
           [36, "dollar", [0x24]],
           [37, "percent", [0x25]],
           [38, "ampersand", [0x26]],
           [39, "quoteright", [0x27, 0x92, 0x2019]],
           [40, "parenleft", [0x28]],
           [41, "parenright", [0x29]],
           [42, "asterisk", [0x2a]],
           [43, "plus", [0x2b]],
           [44, "comma", [0x2c]],
           [45, "hyphen", [0x2d]],
           [46, "period", [0x2e]],
           [47, "slash", [0x2f]],
           [48, "zero", [0x30]],
           [49, "one", [0x31]],
           [50, "two", [0x32]],
           [51, "three", [0x33]],
           [52, "four", [0x34]],
           [53, "five", [0x35]],
           [54, "six", [0x36]],
           [55, "seven", [0x37]],
           [56, "eight", [0x38]],
           [57, "nine", [0x39]],
           [58, "colon", [0x3a]],
           [59, "semicolon", [0x3b]],
           [60, "less", [0x3c]],
           [61, "equal", [0x3d]],
           [62, "greater", [0x3e]],
           [63, "question", [0x3f]],
           [64, "SF100000", [0x2500, 0x2501]],
           [65, "spade", [0x2660]],
           [66, "SF110000", [0x2502, 0x2503]],
           [73, "uni256e", [0x256e]],
           [74, "uni2570", [0x2570]],
           [75, "uni256F", [0x256f]],
           [77, "uni2572", [0x2572]],
           [78, "uni2571", [0x2571]],
           [81, "periodcentered", [0xb7, 0x2022, 0x2219, 0x25cf]],
           [83, "heart", [0x2665]],
           [85, "uni256D", [0x256d]],
           [86, "uni2573", [0x2573]],
           [87, "circle", [0x25cb]],
           [88, "club", [0x2663]],
           [90, "diamond", [0x25c6, 0x2666]],
           [91, "SF050000", [0x253c, 0x254b]],
           [94, "pi", [0x3c0]],
           [95, "uni25e5", [0x25e5]],
           [97, "lfblock", [0x258c]],
           [98, "dnblock", [0x2584]],
           [99, "uni2594", [0x2594]],
           [100, "uni2581", [0x2581]],
           [101, "uni258E", [0x258e]],
           [102, "shade", [0x2592]],
           [105, "uni25E4", [0x25e4]],
           [107, "SF080000", [0x251c, 0x2523]],
           [108, "uni2597", [0x2597]],
           [109, "SF020000", [0x2514, 0x2517]],
           [110, "SF030000", [0x2510, 0x2513]],
           [111, "uni2582", [0x2582]],
           [112, "SF010000", [0x250c, 0x250f]],
           [113, "SF070000", [0x2534, 0x253b]],
           [114, "SF060000", [0x252c, 0x2533]],
           [115, "SF090000", [0x2524, 0x252b]],
           [117, "uni258D", [0x258d]],
           [121, "uni2583", [0x2583]],
           [123, "uni2596", [0x2596]],
           [124, "uni259D", [0x259d]],
           [125, "SF040000", [0x2518, 0x251b]],
           [126, "uni2598", [0x2598]],
           [127, "uni259A", [0x259a]],
           [160, "uni2588", [0x2588]],
           [223, "uni25E3", [0x25e3]],
           [225, "uni2590", [0x2590]],
           [226, "uni2580", [0x2580]],
           [227, "uni2587", [0x2587]],
           [231, "uni258A", [0x258a]],
           [233, "uni25E2", [0x25e2]],
           [236, "uni259B", [0x259b]],
           [246, "uni258B", [0x258b]],
           [247, "uni2586", [0x2586]],
           [248, "uni2585", [0x2585]],
           [251, "uni259C", [0x259c]],
           [252, "uni2599", [0x2599]],
           [254, "uni259F", [0x259f]],
           [255, "uni259E", [0x259e]]]

CHAR_LO = [[0, "at", [0x40]],
           [1, "a", [0x61]],
           [2, "b", [0x62]],
           [3, "c", [0x63]],
           [4, "d", [0x64]],
           [5, "e", [0x65]],
           [6, "f", [0x66]],
           [7, "g", [0x67]],
           [8, "h", [0x68]],
           [9, "i", [0x69]],
           [10, "j", [0x6a]],
           [11, "k", [0x6b]],
           [12, "l", [0x6c]],
           [13, "m", [0x6d]],
           [14, "n", [0x6e]],
           [15, "o", [0x6f]],
           [16, "p", [0x70]],
           [17, "q", [0x71]],
           [18, "r", [0x72]],
           [19, "s", [0x73]],
           [20, "t", [0x74]],
           [21, "u", [0x75]],
           [22, "v", [0x76]],
           [23, "w", [0x77]],
           [24, "x", [0x78]],
           [25, "y", [0x79]],
           [26, "z", [0x7a]],
           [27, "bracketleft", [0x5b]],
           [28, "sterling", [0xa3]],
           [29, "bracketright", [0x5d]],
           [30, "arrowup", [0x2191]],
           [31, "arrowleft", [0x2190]],
           [32, "space", [0x20, 0xa0]],
           [33, "exclam", [0x21]],
           [34, "quotedblright", [0x22, 0x201c, 0x201d]],
           [35, "numbersign", [0x23]],
           [36, "dollar", [0x24]],
           [37, "percent", [0x25]],
           [38, "ampersand", [0x26]],
           [39, "quoteright", [0x27, 0x92, 0x2019]],
           [40, "parenleft", [0x28]],
           [41, "parenright", [0x29]],
           [42, "asterisk", [0x2a]],
           [43, "plus", [0x2b]],
           [44, "comma", [0x2c]],
           [45, "hyphen", [0x2d]],
           [46, "period", [0x2e]],
           [47, "slash", [0x2f]],
           [48, "zero", [0x30]],
           [49, "one", [0x31]],
           [50, "two", [0x32]],
           [51, "three", [0x33]],
           [52, "four", [0x34]],
           [53, "five", [0x35]],
           [54, "six", [0x36]],
           [55, "seven", [0x37]],
           [56, "eight", [0x38]],
           [57, "nine", [0x39]],
           [58, "colon", [0x3a]],
           [59, "semicolon", [0x3b]],
           [60, "less", [0x3c]],
           [61, "equal", [0x3d]],
           [62, "greater", [0x3e]],
           [63, "question", [0x3f]],
           [64, "SF100000", [0x2500, 0x2501]],
           [65, "A", [0x41]],
           [66, "B", [0x42]],
           [67, "C", [0x43]],
           [68, "D", [0x44]],
           [69, "E", [0x45]],
           [70, "F", [0x46]],
           [71, "G", [0x47]],
           [72, "H", [0x48]],
           [73, "I", [0x49]],
           [74, "J", [0x4a]],
           [75, "K", [0x4b]],
           [76, "L", [0x4c]],
           [77, "M", [0x4d]],
           [78, "N", [0x4e]],
           [79, "O", [0x4f]],
           [80, "P", [0x50]],
           [81, "Q", [0x51]],
           [82, "R", [0x52]],
           [83, "S", [0x53]],
           [84, "T", [0x54]],
           [85, "U", [0x55]],
           [86, "V", [0x56]],
           [87, "W", [0x57]],
           [88, "X", [0x58]],
           [89, "Y", [0x59]],
           [90, "Z", [0x5a]],
           [91, "SF050000", [0x253c, 0x254b]],
           [93, "SF110000", [0x2502, 0x2503]],
           [97, "lfblock", [0x258c]],
           [98, "dnblock", [0x2584]],
           [99, "uni2594", [0x2594]],
           [100, "uni2581", [0x2581]],
           [101, "uni258E", [0x258e]],
           [102, "shade", [0x2592]],
           [107, "SF080000", [0x251c, 0x2523]],
           [108, "uni2597", [0x2597]],
           [109, "SF020000", [0x2514, 0x2517]],
           [110, "SF030000", [0x2510, 0x2513]],
           [111, "uni2582", [0x2582]],
           [112, "SF010000", [0x250c, 0x250f]],
           [113, "SF070000", [0x2534, 0x253b]],
           [114, "SF060000", [0x252c, 0x2533]],
           [115, "SF090000", [0x2524, 0x252b]],
           [117, "uni258D", [0x258d]],
           [121, "uni2583", [0x2583]],
           [122, "uni2713", [0x2713]],
           [123, "uni2596", [0x2596]],
           [124, "uni259D", [0x259d]],
           [125, "SF040000", [0x2518, 0x251b]],
           [126, "uni2598", [0x2598]],
           [127, "uni259A", [0x259a]],
           [160, "uni2588", [0x2588]],
           [225, "uni2590", [0x2590]],
           [226, "uni2580", [0x2580]],
           [227, "uni2587", [0x2587]],
           [231, "uni258A", [0x258a]],
           [236, "uni259B", [0x259b]],
           [246, "uni258B", [0x258b]],
           [247, "uni2586", [0x2586]],
           [248, "uni2585", [0x2585]],
           [251, "uni259C", [0x259c]],
           [252, "uni2599", [0x2599]],
           [254, "uni259F", [0x259f]],
           [255, "uni259E", [0x259e]]]

# The Mac OS Roman mapping is an 8-bit encoding including 7-bit ASCII and a few
# bits and pieces. The format is [mac roman code, glyph name]
# Indices not in this table will be mapped to ".notdef"

CMAP_MACROMAN = [[0x0, ".null"],
                 [0x8, ".null"],
                 [0x9, "nonmarkingreturn"],
                 [0xd, "nonmarkingreturn"],
                 [0x1d, ".null"],
                 [0x20, "space"],
                 [0x21, "exclam"],
                 [0x23, "numbersign"],
                 [0x24, "dollar"],
                 [0x25, "percent"],
                 [0x26, "ampersand"],
                 [0x28, "parenleft"],
                 [0x29, "parenright"],
                 [0x2a, "asterisk"],
                 [0x2b, "plus"],
                 [0x2c, "comma"],
                 [0x2d, "hyphen"],
                 [0x2e, "period"],
                 [0x2f, "slash"],
                 [0x30, "zero"],
                 [0x31, "one"],
                 [0x32, "two"],
                 [0x33, "three"],
                 [0x34, "four"],
                 [0x35, "five"],
                 [0x36, "six"],
                 [0x37, "seven"],
                 [0x38, "eight"],
                 [0x39, "nine"],
                 [0x3a, "colon"],
                 [0x3b, "semicolon"],
                 [0x3c, "less"],
                 [0x3d, "equal"],
                 [0x3e, "greater"],
                 [0x3f, "question"],
                 [0x40, "at"],
                 [0x41, "A"],
                 [0x42, "B"],
                 [0x43, "C"],
                 [0x44, "D"],
                 [0x45, "E"],
                 [0x46, "F"],
                 [0x47, "G"],
                 [0x48, "H"],
                 [0x49, "I"],
                 [0x4a, "J"],
                 [0x4b, "K"],
                 [0x4c, "L"],
                 [0x4d, "M"],
                 [0x4e, "N"],
                 [0x4f, "O"],
                 [0x50, "P"],
                 [0x51, "Q"],
                 [0x52, "R"],
                 [0x53, "S"],
                 [0x54, "T"],
                 [0x55, "U"],
                 [0x56, "V"],
                 [0x57, "W"],
                 [0x58, "X"],
                 [0x59, "Y"],
                 [0x5a, "Z"],
                 [0x5b, "bracketleft"],
                 [0x5c, "backslash"],
                 [0x5d, "bracketright"],
                 [0x5e, "asciicircum"],
                 [0x5f, "underscore"],
                 [0x60, "grave"],
                 [0x61, "a"],
                 [0x62, "b"],
                 [0x63, "c"],
                 [0x64, "d"],
                 [0x65, "e"],
                 [0x66, "f"],
                 [0x67, "g"],
                 [0x68, "h"],
                 [0x69, "i"],
                 [0x6a, "j"],
                 [0x6b, "k"],
                 [0x6c, "l"],
                 [0x6d, "m"],
                 [0x6e, "n"],
                 [0x6f, "o"],
                 [0x70, "p"],
                 [0x71, "q"],
                 [0x72, "r"],
                 [0x73, "s"],
                 [0x74, "t"],
                 [0x75, "u"],
                 [0x76, "v"],
                 [0x77, "w"],
                 [0x78, "x"],
                 [0x79, "y"],
                 [0x7a, "z"],
                 [0x7b, "braceleft"],
                 [0x7c, "bar"],
                 [0x7d, "braceright"],
                 [0x7e, "asciitilde"],
                 [0x81, "Aring"],
                 [0x8c, "aring"],
                 [0xa3, "sterling"],
                 [0xae, "AE"],
                 [0xaf, "Oslash"],
                 [0xb9, "pi"],
                 [0xbe, "ae"],
                 [0xbf, "oslash"],
                 [0xca, "space"],
                 [0xd3, "quotedblright"],
                 [0xd5, "quoteright"]]

def makeEmptyGlyphs():
    bitmap = dict()

    bitmap[".notdef"] = [[0b00000000,
                          0b01111110,
                          0b01000010,
                          0b01000010,
                          0b01000010,
                          0b01000010,
                          0b01111110,
                          0b00000000], []]

    bitmap[".null"] = [[],[]]

    bitmap["nonmarkingreturn"] = [[],[]]

    return bitmap

def makeMissingDanishChars():
    print "Adding Danish characters..."
    bitmap = dict()
    bitmap["ae"] = [[0b00000000,
                     0b00000000,
                     0b01110110,
                     0b00011011,
                     0b01111111,
                     0b11011000,
                     0b01111110,
                     0b00000000], [0xe6]]

    bitmap["oslash"] = [[0b00000000,
                         0b00000000,
                         0b00111011,
                         0b01101110,
                         0b01111110,
                         0b01110110,
                         0b11011100,
                         0b00000000], [0xf8]]

    bitmap["aring"] = [[0b00011000,
                        0b00000000,
                        0b00111100,
                        0b00000110,
                        0b00111110,
                        0b01100110,
                        0b00111110,
                        0b00000000], [0xe5]]

    bitmap["AE"] = [[0b00011111,
                     0b00111100,
                     0b01101100,
                     0b01111111,
                     0b01101100,
                     0b01101100,
                     0b01101111,
                     0b00000000], [0xc6]]

    bitmap["Oslash"] = [[0b00111011,
                         0b01101110,
                         0b01101110,
                         0b01111110,
                         0b01110110,
                         0b01110110,
                         0b11011100,
                         0b00000000], [0xd8]]

    bitmap["Aring"] = [[0b00011000,
                        0b00000000,
                        0b00111100,
                        0b01100110,
                        0b01111110,
                        0b01100110,
                        0b01100110,
                        0b00000000], [0xc5]]
    return bitmap

def makeMissingASCII():
    print "Adding the 8 missing ASCII characters in C64 PETSCII..."
    bitmap = dict()

    # Grave accent
    bitmap["grave"] = [[0b00100000,
                        0b00010000,
                        0b00001000,
                        0b00000000,
                        0b00000000,
                        0b00000000,
                        0b00000000,
                        0b00000000], [0x60]]

    # Curly left brace
    bitmap["braceleft"] = [[0b00001100,
                            0b00011000,
                            0b00011000,
                            0b00110000,
                            0b00011000,
                            0b00011000,
                            0b00001100,
                            0b00000000], [0x7b]]

    # Curly right brace
    bitmap["braceright"] = [[0b00110000,
                             0b00011000,
                             0b00011000,
                             0b00001100,
                             0b00011000,
                             0b00011000,
                             0b00110000,
                             0b00000000], [0x7d]]

    # Vertical bar
    bitmap["bar"] = [[0b00011000,
                      0b00011000,
                      0b00011000,
                      0b00011000,
                      0b00011000,
                      0b00011000,
                      0b00011000,
                      0b00011000], [0x7c]]

    # Tilde
    bitmap["asciitilde"] = [[0b00000000,
                             0b00000000,
                             0b00000000,
                             0b00111001,
                             0b01001110,
                             0b00000000,
                             0b00000000,
                             0b00000000], [0x7e]]

    # Caret
    bitmap["asciicircum"] = [[0b00001000,
                              0b00011100,
                              0b00110110,
                              0b01100011,
                              0b01000001,
                              0b00000000,
                              0b00000000,
                              0b00000000], [0x5e]]

    # Backslash
    bitmap["backslash"] = [[0b00000000,
                            0b01100000,
                            0b00110000,
                            0b00011000,
                            0b00001100,
                            0b00000110,
                            0b00000011,
                            0b00000000], [0x5c]]

    # Underscore
    bitmap["underscore"] = [[0b00000000,
                             0b00000000,
                             0b00000000,
                             0b00000000,
                             0b00000000,
                             0b00000000,
                             0b00000000,
                             0b11111111], [0x5f]]

    return bitmap

# THE VECTORIZATION ALGORITHM

def vectorizeGlyph(glyphData, pixelSize, descent):
    if glyphData is None or len(glyphData) == 0:
        return []

    bitmap = unpackChar(glyphData)
    edges = generateEdges(bitmap)
    scaledEdges = scaleEdges(edges, pixelSize, descent)
    return mergeContours(scaledEdges)

# 1) First, we need to unpack the bits in the bitmap and reverse the order so
#    that [0,0] is the lower left corner. This will make the next step easier
#    to understand.
def unpackChar(glyphData):
    return [[((row >> bit) & 1) == 1 for bit in range(7, -1, -1)] for row in reversed(glyphData)]

# 2) A simple way of vectorizing a b/w bitmap is to simply generate (up to)
#    four edges going clockwise around each opaque pixel.
def generateEdges(bitmap):
    edges = []
    height = len(bitmap)
    width = len(bitmap[0])
    for y in range(height):
        for x in range(width):
            if bitmap[y][x]:
                # Insert edge to the left of the pixel?
                if x == 0 or not bitmap[y][x - 1]:
                    edges.append([[x, y], [x, y + 1]])

                # Insert edge above the pixel?
                if y == height - 1 or not bitmap[y + 1][x]:
                    edges.append([[x, y + 1], [x + 1, y + 1]])
                
                # Insert edge to the right of the pixel?
                if x == width - 1 or not bitmap[y][x + 1]:
                    edges.append([[x + 1, y + 1], [x + 1, y]])
                
                # Insert edge below the pixel?
                if y == 0 or not bitmap[y - 1][x]:
                    edges.append([[x + 1, y], [x, y]])
    return edges

# 3) Scaling and translation of the vectorized pixels.
def scaleEdges(edges, pixelSize, descent):
    return [[[point[0] * pixelSize, (point[1] - descent) * pixelSize] for point in edge] for edge in edges]

# 4) In a TTF file we have to provide contours rather than just a bunch of
#    unordered edges. If possible, consecutive edges are merged.
def mergeContours(edges):
    edgeList = sorted(edges)
    contours = []

    while len(edgeList) > 1:
        start = edgeList[0]
        edgeList.remove(start)
        current = start
        contour = [start[0], start[1]]

        while current[1] != start[0]:
            next = [edge for edge in edgeList if edge[0] == current[1]][0]
            if next[1][0] == current[0][0] or next[1][1] == current[0][1]:
                contour[-1] = next[1]
            else:
                contour.append(next[1])
            current = next
            edgeList.remove(current)
        
        # We don't need to include the last edge as it's implicit.
        contours.append(contour[:-1])

    return contours

# TRUETYPE FONT HANDLING

def saveFont(glyphs, outputFileName, asXML, pixelSize, descent, fontName, copyrightYear, creator, version):
    f = TTFont()

    vectorizedGlyphs = {glyph : [vectorizeGlyph(glyphs[glyph][0], pixelSize, descent), glyphs[glyph][1]] for glyph in glyphs}
    unicodes = [code for glyph in glyphs for code in glyphs[glyph][1]]

    # Populate basic tables (there are a few dependencies so order matters)
    makeTable_glyf(f, vectorizedGlyphs)
    makeTable_maxp(f)
    makeTable_loca(f)
    makeTable_head(f)
    makeTable_hmtx(f)
    makeTable_hhea(f, pixelSize, descent)
    makeTable_OS2(f, pixelSize, descent, min(unicodes), max(unicodes))
    makeTable_cmap(f, glyphs)
    makeTable_name(f, fontName, "Regular", copyrightYear, creator, version)
    makeTable_post(f, pixelSize, descent)

    if asXML:
        # We have to compile the TTFont manually when saving as TTX
        # (to auto-calculate stuff here and there)
        f["glyf"].compile(f)
        f["maxp"].compile(f)
        f["loca"].compile(f)
        f["head"].compile(f)
        f["hmtx"].compile(f)
        f["hhea"].compile(f)
        f["OS/2"].compile(f)
        f["cmap"].compile(f)
        f["name"].compile(f)
        f["post"].compile(f)
        print "PLEASE NOTE: When exporting directly to XML, the checkSumAdjustment value in the head table will be 0."
        f.saveXML(outputFileName)
    else:
        f.save(outputFileName)

# glyf - Glyph Data
def makeTable_glyf(ttf, glyphs):

    glyf = newTable("glyf")

    glyf.glyphs = {glyph: makeTTFGlyph(glyphs[glyph][0]) for glyph in glyphs}
    glyf.glyphOrder = sorted(glyf.glyphs.keys())
    ttf["glyf"] = glyf
    ttf.glyphOrder = glyf.glyphOrder

def makeTTFGlyph(polygons):
    result = Glyph()
    result.numberOfContours = len(polygons)
    result.coordinates = numpy.array([coordinate for polygon in polygons for coordinate in polygon])
    result.flags = numpy.array([1] * len(result.coordinates), numpy.int8)
    result.endPtsOfContours = [sum(len(polygon) for polygon in polygons[:idx + 1]) - 1 for idx in range(len(polygons))]
    result.program = ttProgram.Program()
    result.program.assembly = []
    return result

# maxp - Maximum Profile
def makeTable_maxp(ttf):
    maxp = newTable("maxp")
    
    maxp.tableVersion = 0x00010000
    maxp.numGlyphs  = 0           # Auto-calculated by maxp.compile()
    maxp.maxPoints = 0            # Auto-calculated by maxp.compile()
    maxp.maxContours = 0          # Auto-calculated by maxp.compile()
    maxp.maxCompositePoints = 0   # Auto-calculated by maxp.compile()
    maxp.maxCompositeContours = 0 # Auto-calculated by maxp.compile()
    maxp.maxZones = 2
    maxp.maxTwilightPoints = 0
    maxp.maxStorage = 0
    maxp.maxFunctionDefs = 0
    maxp.maxInstructionDefs = 0
    maxp.maxStackElements = 0
    maxp.maxSizeOfInstructions = 0
    maxp.maxComponentElements = 0
    maxp.maxComponentDepth = 0    # Auto-calculated by maxp.compile()

    ttf["maxp"] = maxp

# loca - Index to Location
def makeTable_loca(ttf):
    # Nothing to do here... Locations are auto-calculated by glyf.compile()
    ttf["loca"] = newTable("loca")

# head - Font Header
def makeTable_head(ttf):
    head = newTable("head")
    
    head.tableVersion = 1.0
    head.fontRevision = 1.0
    head.checkSumAdjustment = 0   # Auto-calculated when writing the TTF.
    head.magicNumber = 0x5F0F3CF5
    head.flags = 11               # bits 0, 1, and 3 = 1 + 2 + 8 = 11
    head.unitsPerEm = 2048
    head.created = long(time.time() - mac_epoch_diff)
    head.modified = long(time.time() - mac_epoch_diff)
    head.xMin = 0                 # Auto-calculated by maxp.compile()
    head.xMax = 0                 # Auto-calculated by maxp.compile()
    head.yMin = 0                 # Auto-calculated by maxp.compile()
    head.yMax = 0                 # Auto-calculated by maxp.compile()
    head.macStyle = 0
    head.lowestRecPPEM = 8
    head.fontDirectionHint = 0
    head.indexToLocFormat = 0
    head.glyphDataFormat = 0
    
    ttf["head"] = head

# hmtx - Horizontal Metrics
def makeTable_hmtx(ttf):
    hmtx = newTable("hmtx")
    hmtx.metrics = dict()

    for glyphName in ttf["glyf"].keys():
        if glyphName == ".null":
            hmtx[".null"] = (0, 0)
        else:
            glyph = ttf["glyf"].glyphs[glyphName]
            lsb = 0
            if hasattr(glyph, "coordinates") and len(glyph.coordinates) > 0:
                lsb = min([coord[0] for coord in glyph.coordinates])
            hmtx[glyphName] = (2048, lsb)
    
    ttf["hmtx"] = hmtx

# hhea - Horizontal Header
def makeTable_hhea(ttf, pixelSize, descent):
    hhea = newTable("hhea")
    
    hhea.tableVersion = 1.0
    hhea.ascent = (8 - descent) * pixelSize
    hhea.descent = -descent * pixelSize
    hhea.lineGap = 0
    hhea.advanceWidthMax = 0      # Auto-calculated by hhea.compile()
    hhea.minLeftSideBearing = 0   # Auto-calculated by hhea.compile()
    hhea.minRightSideBearing = 0  # Auto-calculated by hhea.compile()
    hhea.xMaxExtent = 0           # Auto-calculated by hhea.compile()
    hhea.caretSlopeRise = 1
    hhea.caretSlopeRun = 0
    hhea.caretOffset = 0
    hhea.reserved0 = 0
    hhea.reserved1 = 0
    hhea.reserved2 = 0
    hhea.reserved3 = 0
    hhea.metricDataFormat = 0
    hhea.numOfLongHorMetrics = 0  # Auto-calculated by hmtx.compile()

    ttf["hhea"] = hhea

# OS/2 - OS/2 and Windows Specific Metrics
def makeTable_OS2(ttf, pixelSize, descentPixels, minUnicode, maxUnicode):
    size = 8 * pixelSize
    descent = pixelSize * descentPixels

    os_2 = newTable("OS/2")
    
    os_2.version = 4
    os_2.xAvgCharWidth = size
    os_2.usWeightClass = 400      # Meaning "Normal (Regular)"
    os_2.usWidthClass = 5         # Meaing "Medium (normal)"
    os_2.fsType = 0               # Windows-only licensing bits...
    os_2.ySubscriptXSize = size
    os_2.ySubscriptYSize = size / 2
    os_2.ySubscriptXOffset = 0
    os_2.ySubscriptYOffset = descent
    os_2.ySuperscriptXSize = size / 2
    os_2.ySuperscriptYSize = size / 2
    os_2.ySuperscriptXOffset = 0
    os_2.ySuperscriptYOffset = size / 2
    os_2.yStrikeoutSize = pixelSize
    os_2.yStrikeoutPosition = size / 2 - descent
    os_2.sFamilyClass = 0x080a    # Class ID = 8 (Sans Serif), Subclass ID = 10 (Matrix)
    panose = Panose()
    panose.bFamilyType = 2        # Text and Display
    panose.bSerifStyle = 1        # No Fit
    panose.bWeight = 6            # Medium
    panose.bProportion = 9        # Monospaced
    panose.bContrast = 6          # Medium
    panose.bStrokeVariation = 2   # Gradual/Diagonal
    panose.bArmStyle = 2          # Straight Arms/Horizontal
    panose.bLetterForm = 8        # Normal/Square
    panose.bMidline = 1           # No Fit
    panose.bXHeight = 1           # No Fit
    os_2.panose = panose
    os_2.ulUnicodeRange1 = 0b10000000000000000000000010000011 # Basic Latin + Latin-1 supplement + Greek and Coptic + General punctuation
    os_2.ulUnicodeRange2 = 0b00010000000000001111100001100000 # Arrows + Mathematical operators + Box drawing + Block elements + Geometric shapes + Misc. symbols + Dingbats + Private use area
    os_2.ulUnicodeRange3 = 0b00000000000000000000000000000000 # n/a
    os_2.ulUnicodeRange4 = 0b00000000000000000000000000000000 # n/a
    os_2.achVendID = "C=64"       # :-)
    os_2.fsSelection = 64         # Regular
    os_2.fsFirstCharIndex = minUnicode
    os_2.fsLastCharIndex = maxUnicode
    os_2.sTypoAscender = size - descent
    os_2.sTypoDescender = 0 - descent
    os_2.sTypoLineGap = 0
    os_2.usWinAscent = size - descent
    os_2.usWinDescent = descent
    os_2.ulCodePageRange1 = 0b00000000000000000000000000000001 # Latin 1 (Code page 1252)
    os_2.ulCodePageRange2 = 0b11000000000000000000000000000000 # WE/Latin 1 (Code page 850) + US (Code page 437)
    os_2.sxHeight = 6 * pixelSize - descent                    # Guess (we don't always have a lower-case "x" at 0x78 to measure (as the standard suggests))
    os_2.sCapHeight = size - descent
    os_2.usDefaultChar = 0
    os_2.usBreakChar = 32
    os_2.usMaxContex = 0

    ttf["OS/2"] = os_2

# cmap - Character to Glyph Mapping
def makeTable_cmap(ttf, glyphs):
    unicodeCMAP = {index: glyph for glyph in glyphs if glyph in ttf["glyf"].glyphs for index in glyphs[glyph][1]}
    macRoman = dict(CMAP_MACROMAN)
    macRomanCMAP = {index: macRoman[index] if index in macRoman and macRoman[index] in ttf["glyf"].glyphs else '.notdef' for index in range(256)}

    # Unicode
    cmap4_0_3 = cmap_format_4(4)
    cmap4_0_3.platformID = 0
    cmap4_0_3.platEncID = 3
    cmap4_0_3.language = 0
    cmap4_0_3.cmap = unicodeCMAP

    # Mac Roman
    cmap0_1_0 = cmap_format_0(0)
    cmap0_1_0.platformID = 1
    cmap0_1_0.platEncID = 0
    cmap0_1_0.language = 0
    cmap0_1_0.cmap = macRomanCMAP

    # Windows
    cmap4_3_1 = cmap_format_4(4)
    cmap4_3_1.platformID = 3
    cmap4_3_1.platEncID = 1
    cmap4_3_1.language = 0
    cmap4_3_1.cmap = unicodeCMAP

    cmap = newTable("cmap")
    cmap.tableVersion = 0
    cmap.tables = [cmap4_0_3, cmap0_1_0, cmap4_3_1]
    ttf["cmap"] = cmap

# name - Naming Table
def makeTable_name(ttf, fontName, subFamily, copyrightYear, creator, version):
    copyright = "Copyright {0} {1}".format(copyrightYear, creator)
    fullName = "{0} {1}".format(fontName, subFamily)
    uniqueID = "{0} {1}".format(creator, fullName)
    versionText = "Version {0}".format(version)
    psFontName = "{0}-{1}".format("".join([b for b in fontName if 32 < ord(b) < 127]), creator)
    nameEntries = [copyright, fontName, subFamily, uniqueID, fullName, versionText, psFontName]

    unicodeEnc = [0, 3, 0, "utf_16_be"]
    macintoshEnc = [1, 0, 0, "latin1"]
    microsoftEnc = [3, 1, 0x409, "utf_16_be"]
    encodings = [unicodeEnc, macintoshEnc, microsoftEnc]

    name = newTable("name")
    name.names = [makeNameRecord(idx, entry, *conf) for idx, entry in enumerate(nameEntries) for conf in encodings]

    ttf["name"] = name

def makeNameRecord(nameID, string, platformID, platEncID, langID, encoding):
    rec = NameRecord()
    rec.nameID = nameID
    rec.platformID = platformID
    rec.platEncID = platEncID
    rec.langID = langID
    rec.string = unicode(string, "utf8").encode(encoding)
    return rec

# post - Postscript Information
def makeTable_post(ttf, pixelSize, descent):
    post = newTable("post")

    post.glyphOrder = []
    post.extraNames = []
    post.mapping = dict()

    post.formatType = 2
    post.italicAngle = 0
    post.underlinePosition = descent
    post.underlineThickness = pixelSize
    post.isFixedPitch = 1
    post.minMemType42 = 0
    post.maxMemType42 = 0
    post.minMemType1 = 0
    post.maxMemType1 = 0

    ttf["post"] = post

# MAIN METHODS

def readCharBitmaps(fileName):
    if fileName is None:
        return []

    print "Processing input file {0}...".format(fileName)
    data = [ord(b) for b in open(fileName).read()]

    # Shave off magic bytes and append zeroes so the length of the remaining
    # data is an integer multiple of 8.
    data = data[2:]
    while len(data) % 8 != 0:
        data.append(0)

    if len(data) == 0:
        print "No data found. "
        return []
    elif len(data) > 2048:
        print "More than 256 chars detected. Are you sure this is a C64 character set???"
        return []
    else:
        print "{0} glyphs loaded...".format(len(data) / 8)
        return [data[idx:idx + 8] for idx in range(0, len(data), 8)]

def mapGlyphs(glyphData, charset):
    return {char[1] : [glyphData[char[0]], char[2]] for char in charset if char[0] < len(glyphData)}

def mapAllGlyphs(existingGlyphs, newGlyphBitmaps, unicodeOffset):
    newGlyphs = {"uni{0}".format(hex(unicodeOffset + index).upper()[2:]) : [data, [unicodeOffset + index]] for index, data in enumerate(newGlyphBitmaps)}
    updates = {}

    for newGlyph in newGlyphs:
        newBitmap = newGlyphs[newGlyph][0]
        newUnicodes = newGlyphs[newGlyph][1]
        foundGlyph = False
        for oldGlyph in existingGlyphs:
            oldBitmap = existingGlyphs[oldGlyph][0]
            oldUnicodes = existingGlyphs[oldGlyph][1]
            if oldBitmap == newBitmap:
                if oldGlyph in updates:
                    updates[oldGlyph] = [oldBitmap, list(set(updates[oldGlyph][1] + newUnicodes))]
                else:
                    updates[oldGlyph] = [oldBitmap, list(set(oldUnicodes + newUnicodes))]
                foundGlyph = True
                break
        if not foundGlyph:
            updates[newGlyph] = newGlyphs[newGlyph]

    return updates    

def processCharFiles(lowercaseInputFileName, uppercaseInputFileName, outputFileName, asXML, addMissingASCII, addMissingDanish, pixelSize, descent, addAll, fontName, copyrightYear, creator, version):
    glyphs = makeEmptyGlyphs()
    lowercaseBitmaps = []
    uppercaseBitmaps = []

    if uppercaseInputFileName is not None:
        uppercaseBitmaps = readCharBitmaps(uppercaseInputFileName)
        glyphs.update(mapGlyphs(uppercaseBitmaps, CHAR_HI))
    
    if lowercaseInputFileName is not None:
        lowercaseBitmaps = readCharBitmaps(lowercaseInputFileName)
        glyphs.update(mapGlyphs(lowercaseBitmaps, CHAR_LO))

    if addMissingASCII:
        glyphs.update(makeMissingASCII())

    if addMissingDanish:
        glyphs.update(makeMissingDanishChars())

    if addAll:
        glyphs.update(mapAllGlyphs(glyphs, uppercaseBitmaps, 0xee00))
        glyphs.update(mapAllGlyphs(glyphs, lowercaseBitmaps, 0xef00))

    saveFont(glyphs, outputFileName, asXML, pixelSize, descent, fontName, copyrightYear, creator, version)

# "static void main()"
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="c64ttf.py v1.1 - C64 Character Set to TrueType Converter (c) 2013-14 atbrask")
    
    # Files
    parser.add_argument("-l", "--lowercase", help="Input 64C file with lowercase and uppercase characters.")
    parser.add_argument("-u", "--uppercase", help="Input 64C file with uppercase and graphics characters.")
    parser.add_argument("-o", "--output", help="Output filename (default is font name + '.TTF' or '.TTX')")
    parser.add_argument("-x", "--xml", help="Enable XML output (for debugging purposes)", action="store_true")
    parser.add_argument("-m", "--add-missing-ascii", help="Add non-PETSCII characters for ASCII compatibility (ie. grave accent, curly braces, vertical bar, tilde, caret, backslash, and underscore)", action="store_true")
    parser.add_argument("-i", "--add-missing-danish", help="Add special Danish characters. Needed for proper compatibility with the Danish version of MAC OSX.", action="store_true")

    # Vectorization
    parser.add_argument("-p", "--pixelsize", help="Pixel size in the resulting TTF file (default is 256)", default=256)
    parser.add_argument("-d", "--descent", help="The descent below baseline in pixels (default is 1)", default=1)

    # Font stuff
    parser.add_argument("-a", "--add-all", help="Inserts the uppercase character set (if any) at 0xEE00...0xEEFF and the lowercase character set (if any) at 0xEF00...0xEFFF", action="store_true")
    parser.add_argument("-n", "--name", help="Font name (default is C64)")
    parser.add_argument("-y", "--copyrightyear", help="Sets copyright year (default is {0})".format(date.today().year), default=date.today().year)
    parser.add_argument("-c", "--creator", help="Font creator (default is '{0}')".format(getpass.getuser()), default=getpass.getuser())
    parser.add_argument("-v", "--version", help="Sets font version number (default is '1.00')", default="1.00")

    args = parser.parse_args()

    if args.lowercase is None and args.uppercase is None:
        parser.print_help()
        print ""
        print "No input files! Aborting..."
        exit(1)

    fontName = args.name
    if fontName is None:
        fontName = "C64"

    outputFileName = args.output
    if outputFileName is None:
        if args.xml:
            outputFileName = fontName + ".ttx"
        else:
            outputFileName = fontName + ".ttf"

    processCharFiles(args.lowercase, args.uppercase, outputFileName, args.xml, args.add_missing_ascii, args.add_missing_danish, int(args.pixelsize), int(args.descent), args.add_all, fontName, int(args.copyrightyear), args.creator, args.version)
