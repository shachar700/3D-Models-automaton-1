# -*- coding: utf-8 -*-

import time
from ctypes import *
from SendKeys import SendKeys as key
import win32gui
import Image, ImageGrab

PUL = POINTER(c_ulong)

slowFactor = 1
def setSlowFactor(factor):
	global slowFactor
	slowFactor = factor

def sleep(t):
	global slowFactor
	return time.sleep(t * slowFactor)

class KeyBdInput(Structure):
	_fields_ = [
		("wVk", c_ushort),
		("wScan", c_ushort),
		("dwFlags", c_ulong),
		("time", c_ulong),
		("dwExtraInfo", PUL)
	]

class HardwareInput(Structure):
	_fields_ = [
		("uMsg", c_ulong),
		("wParamL", c_short),
		("wParamH", c_ushort)
	]

class MouseInput(Structure):
	_fields_ = [
		("dx", c_long),
		("dy", c_long),
		("mouseData", c_ulong),
		("dwFlags", c_ulong),
		("time",c_ulong),
		("dwExtraInfo", PUL)
	]

class Input_I(Union):
	_fields_ = [
		("ki", KeyBdInput),
		("mi", MouseInput),
		("hi", HardwareInput)
	]

class Input(Structure):
	_fields_ = [
		("type", c_ulong),
		("ii", Input_I)
	]

class POINT(Structure):
	_fields_ = [
		("x", c_ulong),
		("y", c_ulong)
	]

def ensurealt(delay=.1):
	sleep(delay)
	key('%')
	sleep(0.1)
	key('%')
	sleep(delay)

def mouse(x, y):
	orig = POINT()
	windll.user32.GetCursorPos(byref(orig))
	windll.user32.SetCursorPos(x,y)
	return (orig.x, orig.y)

def click(x,y=None,delay=0.1,fixalt=True):
	if y is None and type(x) in (type(()), type([])):
		return click(x[0], x[1],delay=delay,fixalt=fixalt)
	if fixalt:
		ensurealt()
	m = mouse(x, y)
	if delay:
		sleep(delay)
	FInputs = Input * 2
	extra = c_ulong(0)
	ii_ = Input_I()
	ii_.mi = MouseInput(0, 0, 0, 2, 0, pointer(extra))
	ii2_ = Input_I()
	ii2_.mi = MouseInput(0, 0, 0, 4, 0, pointer(extra))
	x = FInputs((0, ii_), (0, ii2_))
	windll.user32.SendInput(2, pointer(x), sizeof(x[0]))
	return m

def doubleclick(x, y=None, delay=.02):
	click(x, y, delay=0, fixalt=False)
	sleep(delay)
	result = click(x, y, delay=0, fixalt=False)
	sleep(delay * 2)
	return result

def find(findimg, insideimg=None, fail=False, clickpoint=False):
	r = subfind(findimg, insideimg=insideimg)
	if r is None:
		return None
	if clickpoint:
		click(r)
	return r

def subfind(findimg,insideimg=None):
	if type(findimg) in(type(()),type([])):
		for i in findimg:
			r = subfind(i, insideimg=insideimg)
			if r is not None:
				return r
		return None
	if type(findimg) is type({}):
		for i in findimg.keys():
			r = subfind(i, insideimg=insideimg)
			if r is not None:
				return (r[0] + findimg[i][0], r[1] + findimg[i][1])
		return None
	if type(findimg) in (type(''),type(u'')):
		findimg = Image.open(findimg).convert('RGB')
	else:
		findimg = findimg.convert('RGB')
	if insideimg is None:
		insideimg = ImageGrab.grab().convert('RGB')
	elif type(insideimg) in (type(''),type(u'')):
		insideimg = Image.open(insideimg).convert('RGB')
	else:
		insideimg = insideimg.convert('RGB')
	findload=findimg.load()
	insideload=insideimg.load()
	point=None
	for x in range(insideimg.size[0]-findimg.size[0]):
		for y in range(insideimg.size[1]-findimg.size[1]):
			sofarsogood = True
			for x2 in range(findimg.size[0]):
				for y2 in range(findimg.size[1]):
					p1 = findload[x2, y2]
					p2 = insideload[x + x2, y + y2]
					if abs(p1[0] - p2[0]) > 8 or abs(p1[1] - p2[1]) > 8 or abs(p1[2] - p2[2]) > 8:
						sofarsogood = False
						break
				if not sofarsogood:
					break
			if sofarsogood:
				point = (x, y)
				break
		if point is not None:
			break
	return point