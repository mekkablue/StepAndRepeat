# encoding: utf-8

###########################################################################################################
#
#
#	Palette Plugin
#
#	Read the docs:
#	https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/Palette
#
#
###########################################################################################################

from __future__ import division, print_function, unicode_literals
import objc
import math
from copy import copy as copy
from GlyphsApp import *
from GlyphsApp.plugins import *
from AppKit import NSAffineTransform, NSAffineTransformStruct

def transform(shiftX=0.0, shiftY=0.0, rotate=0.0, skew=0.0, scale=1.0):
	"""
	Returns an NSAffineTransform object for transforming layers.
	Apply an NSAffineTransform t object like this:
		Layer.transform_checkForSelection_doComponents_(t,False,True)
	Access its transformation matrix like this:
		tMatrix = t.transformStruct() # returns the 6-float tuple
	Apply the matrix tuple like this:
		Layer.applyTransform(tMatrix)
		Component.applyTransform(tMatrix)
		Path.applyTransform(tMatrix)
	Chain multiple NSAffineTransform objects t1, t2 like this:
		t1.appendTransform_(t2)
	"""
	myTransform = NSAffineTransform.transform()
	if rotate:
		myTransform.rotateByDegrees_(rotate)
	if scale != 1.0:
		myTransform.scaleBy_(scale)
	if not (shiftX == 0.0 and shiftY == 0.0):
		myTransform.translateXBy_yBy_(shiftX,shiftY)
	if skew:
		skewStruct = NSAffineTransformStruct()
		skewStruct.m11 = 1.0
		skewStruct.m22 = 1.0
		skewStruct.m21 = math.tan(math.radians(skew))
		skewTransform = NSAffineTransform.transform()
		skewTransform.setTransformStruct_(skewStruct)
		myTransform.appendTransform_(skewTransform)
	return myTransform

class StepAndRepeat(PalettePlugin):
	
	dialog = objc.IBOutlet()
	xField = objc.IBOutlet()
	yField = objc.IBOutlet()
	stepsField = objc.IBOutlet()

	@objc.python_method
	def settings(self):
		self.name = Glyphs.localize({
			'en': 'Step & Repeat',
			'de': 'Wiederholen',
			'fr': 'Répéter',
			'es': 'Repetir',
			'pt': 'Repetir',
			})
		
		# Load .nib dialog (without .extension)
		self.loadNib('IBdialog', __file__)

	@objc.python_method
	def start(self):
		Glyphs.registerDefault('com.mekkablue.StepAndRepeat.x', 0.0)
		Glyphs.registerDefault('com.mekkablue.StepAndRepeat.y', 50.0)
		Glyphs.registerDefault('com.mekkablue.StepAndRepeat.steps', 5)
		self.xField.setStringValue_(Glyphs.defaults['com.mekkablue.StepAndRepeat.x'])
		self.yField.setStringValue_(Glyphs.defaults['com.mekkablue.StepAndRepeat.y'])
		self.stepsField.setStringValue_(Glyphs.defaults['com.mekkablue.StepAndRepeat.steps'])

	# Actions triggered by UI
	@objc.IBAction
	def setXValue_( self, sender ):
		Glyphs.defaults['com.mekkablue.StepAndRepeat.x'] = sender.floatValue()
		
	@objc.IBAction
	def setYValue_( self, sender ):
		Glyphs.defaults['com.mekkablue.StepAndRepeat.y'] = sender.floatValue()
		
	@objc.IBAction
	def setStepsValue_( self, sender ):
		Glyphs.defaults['com.mekkablue.StepAndRepeat.steps'] = sender.intValue()
		
	@objc.IBAction
	def exchangeXandY_(self, sender):
		newY = Glyphs.defaults['com.mekkablue.StepAndRepeat.x']
		newX = Glyphs.defaults['com.mekkablue.StepAndRepeat.y']
		self.xField.setStringValue_(newX)
		self.yField.setStringValue_(newY)
		Glyphs.defaults['com.mekkablue.StepAndRepeat.x'] = newX
		Glyphs.defaults['com.mekkablue.StepAndRepeat.y'] = newY

	@objc.IBAction
	def stepAndRepeat_(self, sender):
		# Extract font from sender
		font = Glyphs.font

		# We’re in the Edit View
		if font and font.currentTab:

			# Check whether glyph is open and there is a selection:
			if len(font.selectedLayers) == 1:
				layer = font.selectedLayers[0]
				if layer and layer.selection:
					
					stepX = Glyphs.defaults["com.mekkablue.StepAndRepeat.x"]
					stepY = Glyphs.defaults["com.mekkablue.StepAndRepeat.y"]
					times = Glyphs.defaults["com.mekkablue.StepAndRepeat.steps"]
					
					repeatingShapes = []
					
					if (stepX != 0.0 or stepY != 0.0) and times > 1:
						for item in layer.selection:
							if type(item) == GSNode:
								path = item.parent
								if not path in repeatingShapes:
									repeatingShapes.append(path)
							elif type(item) != GSAnchor:
								if not item in repeatingShapes:
									repeatingShapes.append(item)
						if repeatingShapes:
							for i in range(1,times):
								shiftMatrix = transform(
									shiftX=stepX*(i),
									shiftY=stepY*(i)
									).transformStruct()
								for shape in repeatingShapes:
									repeatedShape = copy(shape)
									repeatedShape.applyTransform(shiftMatrix)
									layer.shapes.append(repeatedShape)
									if type(repeatedShape) == GSPath:
										for node in repeatedShape.nodes:
											layer.selection.append(node)
									else:
										layer.selection.append(repeatedShape)
					else:
						Message(
							title="Step & Repeat Error",
							message="The current values make no sense. X and Y cannot both be zero, and Steps must be at least 2. You may need to tab out of the field or press the Return key to confirm an entry.",
							OKButton=None
							)

	@objc.python_method
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
