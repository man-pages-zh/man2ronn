#!/usr/bin/env python3

'''
Generate ronn-format man pages from standard man pages

AUTHOR: sadhen <sadhen1992@gmail.com>
LICENSE: MIT
'''
import sys
import os
import re

from argparse import ArgumentParser

def boldrepl(obj):
    text = obj.group(1)
    if text.startswith("-"):
        return "`" + text + "`"
    else:
        return "**" + text + "**"

def main(argv=None): 
    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    parser = ArgumentParser()
    parser.add_argument('-i', '--input', 
                        metavar='<man_file>', dest='input', 
                        help="Specifies man input file to convert")
        
    args = parser.parse_args()
    
    try:
        with open(args.input, 'r') as f:
            text = []
            for line in f:
                line = line.replace('\-', '-').replace('\n\r', '\n')
                line = line.replace('\.', '.').replace('\\e','\\')
                line = line.replace('<', '&lt;')
                line = line.replace('\(aq', "'").replace('\(co', '©')
                line = re.sub('\\\\fB(.*?)\\\\fR', boldrepl, line)
                line = re.sub('\\\\fB(.*?)\\\\fP', boldrepl, line)
                line = re.sub('\\\\fI(.*?)\\\\fR',
                              lambda obj: "<"+obj.group(1)+">",
                              line)
                line = re.sub('\\\\fI(.*?)\\\\fP',
                              lambda obj: "<"+obj.group(1)+">",
                              line)
                if line.startswith(r'.\"'):
                    line = line.replace(r'.\"', '..')
                elif line == '.\n':
                    line = ''
                elif line == '.br\n':
                    text.append(text.pop().rstrip("\n"))
                    line = "<br>\n"
                elif line == '.P\n':
                    line = "\n"
                elif line.startswith('.TH '):
                    line = line.replace('.TH ', '')
                    line = line + '='*(len(line)-1) + '\n'
                elif line.startswith('.SH '):
                    line = "\n## " + line.replace('.SH ', '').replace('"', '')
                elif line.startswith('.B '):
                    line = line.replace('.B ', '')
                    if line.startswith("-"):
                        line = "`" + line.rstrip("\n") + "`\n"
                    else:
                        line = "**" + line.rstrip("\n") + "**\n"
                elif line.startswith('.I '):
                    line = line.replace('.I ', '*'
                                    ).replace('\n', '').rstrip() + '*\n'
                elif line.startswith('.IP '):
                    line = line.replace('.IP ', '*'
                                    ).replace('\n', '').rstrip() + '*\n'
                elif line.startswith('.PP'):
                    line = line.replace('.PP', ''
                                    ).replace('\n', '').rstrip() + '\n'
                else:
                    pass
                    
                if len(text) > 0:
                    if text[-1].startswith("\n## NAME"):
                        text.pop()
                        line = line + '='*(len(line)-1) + '\n'
                    if text[-1] == ".TP\n":
                        text.pop()
                        line = "* " + line
                    elif text[-1].startswith("* "):
                        text[-1] = text[-1].rstrip("\n") + ":\n"
                        line = "  " + line
                    else:
                        pass
                
                if len(line) > 0:
                    text.append(line)
                    
            for i, line in enumerate(text):
                if line[-2:] == '*\n':
                    text[i] = line.replace('*\n', '* ')
                    
            padding = [0] * (len(text) + 1)
            pads = 0
            for i, line in enumerate(text):
                padding[i] = pads
                if line.startswith('.RS'):
                    pads += 2
                    text[i] = '\n\n'
                elif '.RS\n' in line:
                    text[i] = line.replace('.RS\n', '\n\n')
                    pads += 2
                elif line.startswith('.RE'):
                    pads -= 2
                    text[i] = '\n'
                elif '.RE\n' in line:
                    pads -= 2
                    text[i] = line.replace('.RE\n', '\n')
                
            for i in range(len(text)):
                text[i] = text[i].ljust(padding[i])
        
    except IOError:
        sys.stderr.write("Cannot load input file: '%s'\n" % args.input)
        sys.exit(1)

    print(''.join(text))
        
if __name__ == "__main__":
    sys.exit(main())
