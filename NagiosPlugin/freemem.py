#!/usr/bin/env python
#!-*- coding:utf-8 -*-

from optparse import OptionParser
import sys

OK=0
WARNING=1
CRITICAL=2
UNKNOWN=3
unit = {'g':2**30,'m':2**20,'k':2**10,'t':2**40,'b':1}

def opt():
    parser = OptionParser(usage="usage: %prog -w WARNING -c CRITICAL")
    parser.add_option("-c",default="100M",action="store",type="string",dest="critical")
    parser.add_option("-w",default="300M",action="store",type="string",dest="warning")
    return parser.parse_args()

def getFreeMem():
    with open('/proc/meminfo','r') as fd:
        for line in fd.readlines():
            if line.startswith('MemFree'):
                k, v, u = line.split()
                return int(v)*1024

def convertUnit(v):
    s = v.lower()
    lastchar = s[-1]
    num = int(s[:-1])
    if lastchar in unit:
        return num*unit[lastchar]
    else:
        return int(s)

def memParse():
    free_mem = getFreeMem()
    if free_mem >= 2**40:
        mem_free = '%s T' % str(free_mem/(2**40))
        return mem_free
    if free_mem >= 2**30:
        mem_free = '%s G' % str(free_mem/(2**30))
        return mem_free
    elif free_mem >= 2**20:
        mem_free = '%s M' % str(free_mem/(2**20))
        return mem_free
    elif free_mem >= 2**10:
        mem_free = '%s K' % str(free_mem/(2**10))
        return mem_free
    else:
        mem_free = '%s B' % str(free_mem)
        return mem_free

def alarm(mem_free,w,c):
    if w >= mem_free > c:
        print 'WARNING,%s' % memParse() 
        sys.exit(WARNING)
    elif mem_free <= c:
        print 'CRITICAL,%s' % memParse()
        sys.exit(CRITICAL)
    elif mem_free > w:
        print 'OK,%s' % memParse()
        sys.exit(OK)
    else:
        print 'UNKNOWN,%S' % memParse()
        sys.exit(UNKNOWN)     


def main():
    opts, args = opt()
    w = convertUnit(opts.warning)
    c = convertUnit(opts.critical)
    lastwd = memParse()[-1].lower()
    if lastwd in unit:
        w = w/(unit[lastwd])
        c = c/(unit[lastwd])
    mem_free = int(memParse()[:-2])
    alarm(mem_free,w,c)
                    

if __name__ == '__main__':
     main()   

