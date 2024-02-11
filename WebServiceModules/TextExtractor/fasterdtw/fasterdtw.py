#!/usr/bin/env python
# -*- coding: utf-8 -*-

def fastdtw(x, y, radius=5, dist=None):
    win=radius
    xpos=0
    ypos=0

    path=[]

    if len(y)==0:
        print("fasterdtw: Warning: len(y)=0; cannot make mappings")
        return (0,path)

    if len(x)==0:
        print("fasterdtw: Warning: len(x)=0; cannot make mappings")
        return (0,path)


    while xpos<len(x):
        cx=x[xpos]
        cy=y[ypos]

        if cx==cy:
            path.append([xpos,ypos])
            xpos+=1
            if ypos<len(y)-1: ypos+=1
        else:
            found=False
            for wx in range(0,min(win, len(x)-xpos)):
                for wy in range(0,min(win, len(y)-ypos)):
                    if x[xpos+wx]==y[ypos+wy]:
                        found=True
                        break
                if found: break

            if found:
                for i in range(0,wx):
                    path.append([xpos+i, ypos+min(i,wy)])
                xpos+=wx
                ypos+=wy
            else:
                print("fasterdtw: Warning: Force align ",xpos,ypos)
                path.append([xpos,ypos])
                xpos+=1
                if ypos<len(y)-1: ypos+=1

    return (0,path)
