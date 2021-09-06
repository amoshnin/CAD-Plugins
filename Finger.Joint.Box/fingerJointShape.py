#Author-Ian Jobson.
#Description-Create a finger joint Box
#This script was created to work with Fusion360
# license: MIT
# Date 06-2020
# Version 0.2.0 Beta
################################################################################################
##
## This is an improvement to the front of the script.
## Each side will have a seperate sub-routine (function) to create it. We will parse the data it needs
## finger_height is constant across all sides so that is created a global variable.
## The user will input the Length, Height and Width of the box.
## They will also input the thickness of the material and the number of fingers on each edge
##
## Each side creating sub routine will create a new sketch and draw the side then model it.
##
###################################################################################################

import adsk.core, adsk.fusion, adsk.cam, traceback
import math

# Globals
_app = adsk.core.Application.cast(None)
_ui = adsk.core.UserInterface.cast(None)
_units = ''
app = adsk.core.Application.get()
ui  = app.userInterface
finger_height = 0.5

# Command inputs
_imgInputOpen = adsk.core.ImageCommandInput.cast(None)
_imgInputClosed = adsk.core.ImageCommandInput.cast(None)
_boxtype = adsk.core.DropDownCommandInput.cast(None)
_length = adsk.core.ValueCommandInput.cast(None)
_fingersW = adsk.core.ValueCommandInput.cast(None)
_width = adsk.core.ValueCommandInput.cast(None)
_height = adsk.core.StringValueCommandInput.cast(None)
_fingersL = adsk.core.ValueCommandInput.cast(None)
_thickness = adsk.core.ValueCommandInput.cast(None)
_fingersH = adsk.core.ValueCommandInput.cast(None)
_overhang = adsk.core.TextBoxCommandInput.cast(None)
_errMessage = adsk.core.TextBoxCommandInput.cast(None)

_handlers = []

def run(context):
    try:
        global _app, _ui
        global finger_height
        _app = adsk.core.Application.get()
        _ui  = _app.userInterface

        cmdDef = _ui.commandDefinitions.itemById('adskFingerJointScript')
        if not cmdDef:
            # Create a command definition.
            cmdDef = _ui.commandDefinitions.addButtonDefinition('adskFingerJointScript', 'Finger Joint Box', 'Creates a finger joint box', 'Resources/FingerJoint')

        # Connect to the command created event.
        onCommandCreated = FingerJointCommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        _handlers.append(onCommandCreated)

        # Execute the command.
        cmdDef.execute()

        # prevent this module from being terminate when the script returns, because we are waiting for event handlers to fire
        adsk.autoTerminate(False)
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class FingerJointCommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandEventArgs.cast(args)

            # when the command is done, terminate the script
            # this will release all globals which will remove all event handlers
            adsk.terminate()
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Verfies that a value command input has a valid expression and returns the
# value if it does.  Otherwise it returns False.  This works around a
# problem where when you get the value from a ValueCommandInput it causes the
# current expression to be evaluated and updates the display.  Some new functionality
# is being added in the future to the ValueCommandInput object that will make
# this easier and should make this function obsolete.
def getCommandInputValue(commandInput, unitType):
    try:
        valCommandInput = adsk.core.ValueCommandInput.cast(commandInput)
        if not valCommandInput:
            return (False, 0)

        # Verify that the expression is valid.
        des = adsk.fusion.Design.cast(_app.activeProduct)
        unitsMgr = des.unitsManager

        if unitsMgr.isValidExpression(valCommandInput.expression, unitType):
            value = unitsMgr.evaluateExpression(valCommandInput.expression, unitType)
            return (True, value)
        else:
            return (False, 0)
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Event handler for the commandCreated event.
class FingerJointCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)

            # Verify that a Fusion design is active.
            des = adsk.fusion.Design.cast(_app.activeProduct)
            if not des:
                _ui.messageBox('A Fusion design must be active when invoking this command.')
                return()



            # We are going to use millimeters as the intial default.
            # Here we will set up some sensible defaults for the box.
            global _units

            _units = 'mm'
            boxtype = 'Closed'

            length = 12
            lengthAttrib = des.attributes.itemByName('FingerJoint', 'length')
            if lengthAttrib:
                length = float(lengthAttrib.value)

            width = 8
            widthAttrib = des.attributes.itemByName('FingerJoint', 'width')
            if widthAttrib:
                width = widthAttrib.value

            height = 6
            heightAttrib = des.attributes.itemByName('FingerJoint', 'height')
            if heightAttrib:
                height = heightAttrib.value

            thickness = 0.5
            thicknessAttrib = des.attributes.itemByName('FingerJoint', 'thickness')
            if thicknessAttrib:
                thickness = thicknessAttrib.value

            overhang = 0.05
            overhangAttrib = des.attributes.itemByName('FingerJoint', 'overhang')
            if overhangAttrib:
                overhang = overhangAttrib.value

            fingersW = 4
            fingersWAttrib = des.attributes.itemByName('FingerJoint', 'fingersW')
            if fingersWAttrib:
                fingersW = fingersWAttrib.value


            fingersL = 6
            fingersLAttrib = des.attributes.itemByName('FingerJoint', 'fingersL')
            if fingersLAttrib:
                fingersL = fingersLAttrib.value


            fingersH = 4
            fingersHAttrib = des.attributes.itemByName('FingerJoint', 'fingersH')
            if fingersHAttrib:
                fingersH = fingersHAttrib.value

            cmd = eventArgs.command
            cmd.isExecutedWhenPreEmpted = False
            inputs = cmd.commandInputs

            global _boxtype, _length, _width, _pitch, _height, _fingersL, _thickness, _fingersH, _overhang, _fingersW, _imgInputOpen, _imgInputClosed, _errMessage

            # Define the command dialog.
            # This is where we list all the inputs
            _imgInputOpen = inputs.addImageCommandInput('FingerJointImageOpen', '', 'Resources/OpenBox.png')
            _imgInputOpen.isFullWidth = True

            _imgInputClosed = inputs.addImageCommandInput('FingerJointImageClosed', '', 'Resources/ClosedBox.png')
            _imgInputClosed.isFullWidth = True

            _boxtype = inputs.addDropDownCommandInput('boxtype', 'Type', adsk.core.DropDownStyles.TextListDropDownStyle)
            if boxtype == "Open":
                _boxtype.listItems.add('Open', True)
                _boxtype.listItems.add('Closed', False)
                _imgInputClosed.isVisible = False
            else:
                _boxtype.listItems.add('Open', False)
                _boxtype.listItems.add('Closed', True)
                _imgInputOpen.isVisible = False


            _length = inputs.addValueInput('length', 'Length', _units, adsk.core.ValueInput.createByReal(float(length)))

            _width = inputs.addValueInput('width', 'Width', _units, adsk.core.ValueInput.createByReal(float(width)))

            _height = inputs.addValueInput('height', 'Height', _units, adsk.core.ValueInput.createByReal(float(height)))

            _thickness = inputs.addValueInput('thickness', 'Thickness', _units, adsk.core.ValueInput.createByReal(float(thickness)))

            _fingersL = inputs.addValueInput('fingersL', '# Fingers Length', '', adsk.core.ValueInput.createByReal(float(fingersL)))

            _fingersW = inputs.addValueInput('fingersW', '# Fingers Width', '', adsk.core.ValueInput.createByReal(float(fingersW)))

            _fingersH = inputs.addValueInput('fingersH', '# Fingers Height', '', adsk.core.ValueInput.createByReal(float(fingersH)))

            _overhang = inputs.addValueInput('overhang', 'Overhang', _units, adsk.core.ValueInput.createByReal(float(overhang)))

            _errMessage = inputs.addTextBoxCommandInput('errMessage', '', '', 2, True)
            _errMessage.isFullWidth = True

            # Connect to the command related events.
            onExecute = FingerJointCommandExecuteHandler()
            cmd.execute.add(onExecute)
            _handlers.append(onExecute)

            onInputChanged = FingerJointCommandInputChangedHandler()
            cmd.inputChanged.add(onInputChanged)
            _handlers.append(onInputChanged)

            onValidateInputs = FingerJointCommandValidateInputsHandler()
            cmd.validateInputs.add(onValidateInputs)
            _handlers.append(onValidateInputs)

            onDestroy = FingerJointCommandDestroyHandler()
            cmd.destroy.add(onDestroy)
            _handlers.append(onDestroy)
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Event handler for the execute event.
class FingerJointCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandEventArgs.cast(args)

            if _boxtype.selectedItem.name == 'Open':
                width = _width.value
            elif _boxtype.selectedItem.name == 'Closed':
                width = _width.value

            # Save the current values as attributes.
            des = adsk.fusion.Design.cast(_app.activeProduct)
            attribs = des.attributes
            attribs.add('FingerJoint', 'boxtype', _boxtype.selectedItem.name)
            attribs.add('FingerJoint', 'length', str(_length.value))
            attribs.add('FingerJoint', 'width', str(width))
            attribs.add('FingerJoint', 'height', str(_height.value))
            attribs.add('FingerJoint', 'fingersL', str(_fingersL.value))
            attribs.add('FingerJoint', 'thickness', str(_thickness.value))
            attribs.add('FingerJoint', 'fingersH', str(_fingersH.value))
            attribs.add('FingerJoint', 'fingersW', str(_fingersW.value))
            attribs.add('FingerJoint', 'overhang', str(_overhang.value))

            boxtype = _boxtype.selectedItem.name
            length = _length.value
            width = _width.value
            height = _height.value
            thickness = _thickness.value
            fingersL = int(_fingersL.value)
            fingersH = int(_fingersH.value)
            fingersW = int(_fingersW.value)
            overhang = _overhang.value

##################################################################################################################################
##
## Now lets calculate the finger widths that we need
##
##################################################################################################################################
            fingerwidthL = (length-(2*thickness))/((fingersL*2)+1)
            fingerwidthW = (width-(2*thickness))/((fingersW*2)+1)
            if boxtype == 'Closed':
                fingerwidthH = (height-(2*thickness))/((fingersH*2)+1)
            else:
                fingerwidthH = (height - thickness)/((fingersH*2)+1)
#################################################################################################################################
# And the finger height which is the thickness + extra length (overhang) that we enter
# If there is overhang, we should increase the box dimensions to compensate for this
#################################################################################################################################
            if overhang > 0:
                finger_height = thickness + overhang
                height = height + (2*overhang)
                width = width + (2*overhang)
                length = length + (2*overhang)
            else:
                finger_height = thickness

            if boxtype == 'Closed':
                CreateType1(length,height,fingerwidthL,fingerwidthH,fingersL,fingersH, finger_height,thickness)
                CreateType2(boxtype,length,width,fingerwidthL,fingerwidthW,fingersL,fingersW, finger_height,thickness)
                CreateType3(height,width,fingerwidthH,fingerwidthW,fingersH,fingersW, finger_height,thickness)
            else:
                height = height - overhang
                CreateType4(length,height,fingerwidthL,fingerwidthH,fingersL,fingersH, finger_height,thickness)
                CreateType2(boxtype,length,width,fingerwidthL,fingerwidthW,fingersL,fingersW, finger_height,thickness)
                CreateType5(height,width,fingerwidthH,fingerwidthW,fingersH,fingersW, finger_height,thickness)
            #DoStuff(boxtype, height, width, length, thickness, fingersL, fingersH, fingersW, overhang)


        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))



# Event handler for the inputChanged event.
class FingerJointCommandInputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.InputChangedEventArgs.cast(args)
            changedInput = eventArgs.input

            global _units
            if changedInput.id == 'boxtype':
                if _boxtype.selectedItem.name == 'Open':
                    _imgInputClosed.isVisible = False
                    _imgInputOpen.isVisible = True


                elif _boxtype.selectedItem.name == 'Closed':
                    _imgInputClosed.isVisible = True
                    _imgInputOpen.isVisible = False



                # Set each one to it's current value because otherwised if the user
                # has edited it, the value won't update in the dialog because
                # apparently it remembers the units when the value was edited.
                # Setting the value using the API resets this.
                _fingersW.value = _fingersW.value
               # _fingersW.unitType = _units
                _fingersL.value = _fingersL.value
                #_fingersL.unitType = _units
                _thickness.value = _thickness.value
                _thickness.unitType = _units
                _fingersH.value = _fingersH.value
               # _fingersH.unitType = _units
                _length.value = _length.value
                _length.unitType = _units
                _width.value = _width.value
                _height.value = _height.value
                _overhang.value = _overhang.value
                _boxtype.selectedItem.name = _boxtype.selectedItem.name


        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Event handler for the validateInputs event.
class FingerJointCommandValidateInputsHandler(adsk.core.ValidateInputsEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.ValidateInputsEventArgs.cast(args)

            _errMessage.text = ''






            des = adsk.fusion.Design.cast(_app.activeProduct)

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))



# Builds a finger joint box.
def DoStuff(boxtype, height, width, length, thickness, fingersL, fingersH, fingersW, overhang):
    try:
        height = str(height)
        width = str(width)
        length = str(length)
        thickness = str(thickness)
        fingersL = str(fingersL)
        fingersW = str(fingersW)
        fingersH = str(fingersH)
        overhang = str(overhang)
        _ui.messageBox("The box type is " + boxtype)
        _ui.messageBox("The height is " + height)
        _ui.messageBox("The width is " + width)
        _ui.messageBox("The length is " + length)
        _ui.messageBox("The thickness is " + thickness)
        _ui.messageBox("The # fingers Length is " + fingersL)
        _ui.messageBox("The # fingers width is " + fingersW)
        _ui.messageBox("The # fingers height is " + fingersH)
        _ui.messageBox("The overhang is " + overhang)



        return
    except Exception as error:
        _ui.messageBox("DoStuff Failed : " + str(error))
        return None
def CreateType1(length,height,fingerwidthL,fingerwidthH,fingercountL,fingercountH, finger_height,thickness):

    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    if not design:
        ui.messageBox('It is not supported in current workspace, please change to MODEL workspace and try again.')
        return
    currentDesignType = design.designType

    rootComp = design.rootComponent
    if rootComp is None:
        ui.messageBox('New component failed to create', 'New Component Failed')
        return

    sketches = rootComp.sketches
    #Create a new sketch
    sketch = sketches.add(rootComp.xYConstructionPlane)
    # add sketch curves
    lines = sketch.sketchCurves.sketchLines

    #################################################################################################
    # Draw the type 1 side geometry
    # points go x,y,z
    ################################################################################################
    heightmfh = height - finger_height
    numberpointsup = fingercountL * 2
    numberpointsdown = (fingercountL * 2) + 2
    numberpointsup = int(numberpointsup)
    numberpointsdown = int(numberpointsdown)
    pointleftup = finger_height + fingerwidthL
    pointleftdown = finger_height
    pointup = [0]
    pointdown = [0]
    pointupB = [0]
    pointdownB = [0]
    pointdownC = [0]
    pointupC = [0]
    pointupD = [0]
    pointdownD = [0]
    # This just loads the lists with enough entries for the box.
    for x in range (numberpointsdown+5):
        pointup.append(x)
        pointdown.append(x)
        pointupB.append(x)
        pointdownB.append(x)
        pointupC.append(x)
        pointdownC.append(x)
        pointupD.append(x)
        pointdownD.append(x)
        pass
    pointup[1] = adsk.core.Point3D.create(pointleftup,height,0)
    pointdown[1] = adsk.core.Point3D.create(pointleftdown,heightmfh,0)
    pointupB[1] = adsk.core.Point3D.create(pointleftup,0,0)
    pointdownB[1] = adsk.core.Point3D.create(pointleftdown,finger_height,0)
    for step in range (2,numberpointsup + 1):
        link = step - 1
        pointup[step] = adsk.core.Point3D.create(pointleftup + (link*fingerwidthL),height,0)
        pointupB[step] = adsk.core.Point3D.create(pointleftup + (link*fingerwidthL),0,0)
        pass
    for step in range (2,numberpointsdown + 1):
        link = step - 1
        pointdown[step] = adsk.core.Point3D.create(pointleftdown + (link*fingerwidthL),heightmfh,0)
        pointdownB[step] = adsk.core.Point3D.create(pointleftdown + (link*fingerwidthL),finger_height,0)
        pass
    for line in range (2,numberpointsup + 2,2):
        lines.addByTwoPoints(pointup[line - 1], pointup[line])
        lines.addByTwoPoints(pointup[line- 1],pointdown[line])
        lines.addByTwoPoints(pointup[line],pointdown[line + 1])
        lines.addByTwoPoints(pointupB[line - 1], pointupB[line])
        lines.addByTwoPoints(pointupB[line- 1],pointdownB[line])
        lines.addByTwoPoints(pointupB[line],pointdownB[line + 1])
        pass
    for line in range (2,numberpointsdown + 2,2):
        lines.addByTwoPoints(pointdown[line - 1], pointdown[line])
        lines.addByTwoPoints(pointdownB[line - 1], pointdownB[line])
        pass
#############################################################################################################
# Vertical sides next
#############################################################################################################
    numberpointsupV = fingercountH * 2
    numberpointsdownV = (fingercountH * 2) + 2
    numberpointsupV = int(numberpointsupV)
    numberpointsdownV = int(numberpointsdownV)
    pointdownC[1] = pointdownB[1]
    pointupC[1] = adsk.core.Point3D.create(0,finger_height + fingerwidthH,0)
    pointdownD[1] = adsk.core.Point3D.create(length - finger_height,finger_height,0)
    pointupD[1] = adsk.core.Point3D.create(length,finger_height + fingerwidthH,0)
    for step in range (2,numberpointsupV + 1):
        link = step - 1
        pointupC[step] = adsk.core.Point3D.create(0, (finger_height+fingerwidthH )+ (link*fingerwidthH),0)
        #lines.addByTwoPoints(pointupC[step - 1], pointupC[step])
        pointupD[step] = adsk.core.Point3D.create(length,(finger_height+fingerwidthH )+ (link*fingerwidthH),0)
        pass
    for step in range (2,numberpointsdownV + 1):
        link = step - 1
        pointdownC[step] = adsk.core.Point3D.create(finger_height,pointleftdown + (link*fingerwidthH),0)
        pointdownD[step] = adsk.core.Point3D.create(length - finger_height,pointleftdown + (link*fingerwidthH),0)
        pass
    for line in range (2,numberpointsupV + 2,2):
        lines.addByTwoPoints(pointupC[line - 1], pointupC[line])
        lines.addByTwoPoints(pointupC[line- 1],pointdownC[line])
        lines.addByTwoPoints(pointupC[line],pointdownC[line + 1])
        lines.addByTwoPoints(pointupD[line - 1], pointupD[line])
        lines.addByTwoPoints(pointupD[line- 1],pointdownD[line])
        lines.addByTwoPoints(pointupD[line],pointdownD[line + 1])
        pass
    for line in range (2,numberpointsdownV + 2,2):
        lines.addByTwoPoints(pointdownC[line - 1], pointdownC[line])
        lines.addByTwoPoints(pointdownD[line - 1], pointdownD[line])
        pass
    prof = sketch.profiles.item(0)
    extrudeSide(prof,thickness)
    extrudeSide(prof,thickness)
    return
def CreateType2(boxtype,length,width,fingerwidthL,fingerwidthW,fingercountL,fingercountW, finger_height,thickness):

    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    if not design:
        ui.messageBox('It is not supported in current workspace, please change to MODEL workspace and try again.')
        return
    currentDesignType = design.designType

    rootComp = design.rootComponent
    if rootComp is None:
        ui.messageBox('New component failed to create', 'New Component Failed')
        return

    sketches = rootComp.sketches
    #Create a new sketch
    sketch = sketches.add(rootComp.xYConstructionPlane)
    # add sketch curves
    lines = sketch.sketchCurves.sketchLines


    #################################################################################################
    # Draw the type 2 side geometry
    # points go x,y,z
    ################################################################################################
    widthmfh = width - finger_height
    numberpointsup = (fingercountL *2) + 4
    numberpointsdown = (fingercountL *2) + 1
    numberpointsup = int(numberpointsup)
    numberpointsdown = int(numberpointsdown)
    pointleftup = finger_height + fingerwidthL
    pointleftdown = finger_height + fingerwidthL
    pointup = [0]
    pointdown = [0]
    pointupB = [0]
    pointdownB = [0]
    pointdownC = [0]
    pointupC = [0]
    pointupD = [0]
    pointdownD = [0]
    # This just loads the lists with enough entries for the box.
    for x in range (numberpointsdown+5):
        pointup.append(x)
        pointdown.append(x)
        pointupB.append(x)
        pointdownB.append(x)
        pointupC.append(x)
        pointdownC.append(x)
        pointupD.append(x)
        pointdownD.append(x)
        pass
    pointup[1] = adsk.core.Point3D.create(pointleftup,width,0)
    pointdown[1] = adsk.core.Point3D.create(pointleftdown,widthmfh,0)
    pointupB[1] = adsk.core.Point3D.create(pointleftup,0,0)
    pointdownB[1] = adsk.core.Point3D.create(pointleftdown,finger_height,0)
    pointupS = adsk.core.Point3D.create(0,width,0)
    pointupS2 = adsk.core.Point3D.create(0,0,0)
    pointupE = adsk.core.Point3D.create(length,width,0)
    pointupE2 = adsk.core.Point3D.create(length,0,0)
    for step in range (2,numberpointsup + 1):
        link = step - 1
        pointup[step] = adsk.core.Point3D.create(pointleftup + (link*fingerwidthL),width,0)
        pointupB[step] = adsk.core.Point3D.create(pointleftup + (link*fingerwidthL),0,0)
        pass
    for step in range (2,numberpointsdown + 1):
        link = step - 1
        pointdown[step] = adsk.core.Point3D.create(pointleftdown + (link*fingerwidthL),widthmfh,0)
        pointdownB[step] = adsk.core.Point3D.create(pointleftdown + (link*fingerwidthL),finger_height,0)
        pass
    lines.addByTwoPoints(pointup[1], pointupS)
    lines.addByTwoPoints(pointupB[1], pointupS2)
    lines.addByTwoPoints(pointup[numberpointsup -4], pointupE)
    lines.addByTwoPoints(pointupB[numberpointsup - 4], pointupE2)

    for line in range (2,numberpointsup -2,2):
        lines.addByTwoPoints(pointup[line], pointup[line + 1])
        lines.addByTwoPoints(pointup[line - 1],pointdown[line-1])
        lines.addByTwoPoints(pointup[line],pointdown[line])
        lines.addByTwoPoints(pointupB[line], pointupB[line + 1])
        lines.addByTwoPoints(pointupB[line- 1],pointdownB[line - 1])
        lines.addByTwoPoints(pointupB[line],pointdownB[line])
        pass
    for line in range (2,numberpointsdown,2):
        lines.addByTwoPoints(pointdown[line - 1], pointdown[line])
        lines.addByTwoPoints(pointdownB[line - 1], pointdownB[line])
        pass
    #############################################################################################################
    # Vertical sides next
    #############################################################################################################
    numberpointsupV = (fingercountW *2) + 4
    numberpointsdownV = (fingercountW *2) + 1
    numberpointsupV = int(numberpointsupV)
    numberpointsdownV = int(numberpointsdownV)
    pointupC[1] = adsk.core.Point3D.create(0,width,0)
    pointdownC[1] = adsk.core.Point3D.create(pointleftdown,widthmfh,0)
    pointupD[1] = adsk.core.Point3D.create(pointleftup,0,0)
    pointdownD[1] = adsk.core.Point3D.create(pointleftdown,finger_height,0)
    pointupT = adsk.core.Point3D.create(0,0,0)
    pointupT2 = adsk.core.Point3D.create(0,width,0)
    pointupF = adsk.core.Point3D.create(length,0,0)
    pointupF2 = adsk.core.Point3D.create(length,width,0)
    for step in range (2,numberpointsupV):
        link = step - 1
        pointupC[step] = adsk.core.Point3D.create(0,((link*fingerwidthW) + finger_height),0)
        pointupD[step] = adsk.core.Point3D.create(length,((link*fingerwidthW)+ finger_height),0)
        pass
    for step in range (2,numberpointsdownV + 2):
        link = step - 1
        pointdownC[step] = adsk.core.Point3D.create(finger_height,((link*fingerwidthW)+finger_height),0)
        pointdownD[step] = adsk.core.Point3D.create(length - finger_height,(link*fingerwidthW)+finger_height,0)
        pass
    lines.addByTwoPoints(pointupC[2], pointupT)
    lines.addByTwoPoints(pointupC[numberpointsupV -2], pointupT2)
    lines.addByTwoPoints(pointupD[2], pointupF)
    lines.addByTwoPoints(pointupD[numberpointsupV -2], pointupF2)
    for line in range (3,numberpointsupV -2,2):
        lines.addByTwoPoints(pointupC[line], pointupC[line +1])
        lines.addByTwoPoints(pointupC[line - 1],pointdownC[line - 1])
        lines.addByTwoPoints(pointupC[line],pointdownC[line])
        lines.addByTwoPoints(pointupD[line], pointupD[line+1])
        lines.addByTwoPoints(pointupD[line -1],pointdownD[line -1])
        lines.addByTwoPoints(pointupD[line],pointdownD[line])
        pass
    for line in range (3,numberpointsdownV + 2,2):
        lines.addByTwoPoints(pointdownC[line - 1], pointdownC[line])
        lines.addByTwoPoints(pointdownD[line - 1], pointdownD[line])
        pass
    prof = sketch.profiles.item(0)
    extrudeSide(prof,thickness)
    if boxtype == "Closed":
        extrudeSide(prof,thickness)


    return

def CreateType3(height,width,fingerwidthH,fingerwidthW,fingercountH,fingercountW, finger_height,thickness):
    test="OFF"
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    if not design:
        ui.messageBox('It is not supported in current workspace, please change to MODEL workspace and try again.')
        return
    currentDesignType = design.designType

    rootComp = design.rootComponent
    if rootComp is None:
        ui.messageBox('New component failed to create', 'New Component Failed')
        return

    sketches = rootComp.sketches
    #Create a new sketch
    sketch = sketches.add(rootComp.xYConstructionPlane)
    # add sketch curves
    lines = sketch.sketchCurves.sketchLines
    #Test draw a box in the sketch
    if test == "ON":
        point0 = adsk.core.Point3D.create(0, 0, 0)
        point1 = adsk.core.Point3D.create(length, 0, 0)
        point2 = adsk.core.Point3D.create(length, width, 0)
        point3 = adsk.core.Point3D.create(0, width, 0)
        lines.addByTwoPoints(point0, point1)
        lines.addByTwoPoints(point1, point2)
        lines.addByTwoPoints(point2, point3)
        lines.addByTwoPoints(point3, point0)
        prof = sketch.profiles.item(0)
        extrudeSide(prof,thickness)
    #################################################################################################
    # Draw the type 3 side geometry
    # points go x,y,z
    ################################################################################################
    heightmfh = height - finger_height
    numberpointsup = fingercountW * 2
    numberpointsdown = (fingercountW * 2) + 2
    numberpointsup = int(numberpointsup)
    numberpointsdown = int(numberpointsdown)
    pointleftup = finger_height + fingerwidthW
    pointleftdown = finger_height + fingerwidthW
    pointup = [0]
    pointdown = [0]
    pointupB = [0]
    pointdownB = [0]
    pointdownC = [0]
    pointupC = [0]
    pointupD = [0]
    pointdownD = [0]
    # This just loads the lists with enough entries for the box.
    for x in range (numberpointsdown+5):
        pointup.append(x)
        pointdown.append(x)
        pointupB.append(x)
        pointdownB.append(x)
        pointupC.append(x)
        pointdownC.append(x)
        pointupD.append(x)
        pointdownD.append(x)
        pass
    pointup[1] = adsk.core.Point3D.create(pointleftup,height,0)
    pointdown[1] = adsk.core.Point3D.create(pointleftdown,heightmfh,0)
    pointupB[1] = adsk.core.Point3D.create(pointleftup,0,0)
    pointdownB[1] = adsk.core.Point3D.create(pointleftdown,finger_height,0)
    pointbl = adsk.core.Point3D.create(0,finger_height,0)
    pointtl = adsk.core.Point3D.create(0,heightmfh,0)
    pointbr = adsk.core.Point3D.create(width,finger_height)
    pointtr = adsk.core.Point3D.create(width,heightmfh)
    for step in range (2,numberpointsup + 1):
        link = step - 1
        pointup[step] = adsk.core.Point3D.create(pointleftup + (link*fingerwidthW),height,0)
        pointupB[step] = adsk.core.Point3D.create(pointleftup + (link*fingerwidthW),0,0)
        pass
    for step in range (2,numberpointsdown + 1):
        link = step - 1
        pointdown[step] = adsk.core.Point3D.create(pointleftdown + (link*fingerwidthW),heightmfh,0)
        pointdownB[step] = adsk.core.Point3D.create(pointleftdown + (link*fingerwidthW),finger_height,0)
        pass
    for line in range (2,numberpointsup + 2,2):
        lines.addByTwoPoints(pointup[line - 1], pointup[line])
        lines.addByTwoPoints(pointup[line- 1],pointdown[line -1])
        lines.addByTwoPoints(pointup[line],pointdown[line])
        lines.addByTwoPoints(pointupB[line - 1], pointupB[line])
        lines.addByTwoPoints(pointupB[line- 1],pointdownB[line -1])
        lines.addByTwoPoints(pointupB[line],pointdownB[line])
        pass
    for line in range (2,numberpointsdown,2):
        lines.addByTwoPoints(pointdown[line], pointdown[line + 1])
        lines.addByTwoPoints(pointdownB[line], pointdownB[line + 1])
        pass
    lines.addByTwoPoints(pointbl,pointdownB[1])
    lines.addByTwoPoints(pointtl,pointdown[1])
    lines.addByTwoPoints(pointbr,pointdownB[numberpointsdown - 2])
    lines.addByTwoPoints(pointtr,pointdown[numberpointsdown - 2])
    ###################################################################################################
    # Now lets create the vertical sides
    ###################################################################################################
    numberpointsupV = fingercountH * 2
    numberpointsdownV = (fingercountH * 2) + 2
    numberpointsupV = int(numberpointsupV)
    numberpointsdownV = int(numberpointsdownV)
    pointleftupV = finger_height + fingerwidthH
    pointleftdownV = finger_height + fingerwidthH
    pointdownC[1] = adsk.core.Point3D.create(finger_height,finger_height + fingerwidthH,0)
    pointupC[1] = adsk.core.Point3D.create(0,finger_height + fingerwidthH,0)
    pointdownD[1] = adsk.core.Point3D.create(width - finger_height,finger_height + fingerwidthH,0)
    pointupD[1] = adsk.core.Point3D.create(width,finger_height + fingerwidthH,0)
    for step in range (2,numberpointsupV + 2):
        link = step - 1
        pointupC[step] = adsk.core.Point3D.create(0, (finger_height+fingerwidthH )+ (link*fingerwidthH),0)
        pointupD[step] = adsk.core.Point3D.create(width,(finger_height+fingerwidthH )+ (link*fingerwidthH),0)
        pass
    for step in range (2,numberpointsdownV + 1):
        link = step - 1
        pointdownC[step] = adsk.core.Point3D.create(finger_height,pointleftdownV + (link*fingerwidthH),0)
        pointdownD[step] = adsk.core.Point3D.create(width - finger_height,pointleftdownV + (link*fingerwidthH),0)
        pass
    for line in range (2,numberpointsupV + 2,2):
        lines.addByTwoPoints(pointupC[line], pointupC[line + 1])
        lines.addByTwoPoints(pointupC[line- 1],pointdownC[line - 1])
        lines.addByTwoPoints(pointupC[line],pointdownC[line])
        lines.addByTwoPoints(pointupD[line], pointupD[line + 1])
        lines.addByTwoPoints(pointupD[line- 1],pointdownD[line - 1])
        lines.addByTwoPoints(pointupD[line],pointdownD[line])
        pass
    for line in range (2,numberpointsdownV,2):
        lines.addByTwoPoints(pointdownC[line - 1], pointdownC[line])
        lines.addByTwoPoints(pointdownD[line - 1], pointdownD[line])
        pass
    lines.addByTwoPoints(pointbl, pointupC[1])
    lines.addByTwoPoints(pointbr, pointupD[1])
    prof = sketch.profiles.item(0)
    extrudeSide(prof,thickness)
    extrudeSide(prof,thickness)
    return
def CreateType4(length,height,fingerwidthL,fingerwidthH,fingercountL,fingercountH, finger_height,thickness):

    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    if not design:
        ui.messageBox('It is not supported in current workspace, please change to MODEL workspace and try again.')
        return
    currentDesignType = design.designType

    rootComp = design.rootComponent
    if rootComp is None:
        ui.messageBox('New component failed to create', 'New Component Failed')
        return

    sketches = rootComp.sketches
    #Create a new sketch
    sketch = sketches.add(rootComp.xYConstructionPlane)
    # add sketch curves
    lines = sketch.sketchCurves.sketchLines

    #################################################################################################
    # Draw the type 1 side geometry
    # points go x,y,z
    ################################################################################################
    heightmfh = height - finger_height
    numberpointsup = fingercountL * 2
    numberpointsdown = (fingercountL * 2) + 2
    numberpointsup = int(numberpointsup)
    numberpointsdown = int(numberpointsdown)
    pointleftup = finger_height + fingerwidthL
    pointleftdown = finger_height
    pointup = [0]
    pointdown = [0]
    pointupB = [0]
    pointdownB = [0]
    pointdownC = [0]
    pointupC = [0]
    pointupD = [0]
    pointdownD = [0]
    # This just loads the lists with enough entries for the box.
    for x in range (numberpointsdown+5):
        pointup.append(x)
        pointdown.append(x)
        pointupB.append(x)
        pointdownB.append(x)
        pointupC.append(x)
        pointdownC.append(x)
        pointupD.append(x)
        pointdownD.append(x)
        pass
    pointup[1] = adsk.core.Point3D.create(pointleftup,height,0)
    pointdown[1] = adsk.core.Point3D.create(pointleftdown,heightmfh,0)
    pointupB[1] = adsk.core.Point3D.create(pointleftup,0,0)
    pointdownB[1] = adsk.core.Point3D.create(pointleftdown,finger_height,0)
    pointTopFlat1 = adsk.core.Point3D.create(finger_height,height,0)
    pointTopFlat2 = adsk.core.Point3D.create((length-finger_height),height,0)
    lines.addByTwoPoints(pointTopFlat1, pointTopFlat2)
    for step in range (2,numberpointsup + 1):
        link = step - 1
        #pointup[step] = adsk.core.Point3D.create(pointleftup + (link*fingerwidthL),height,0)
        pointupB[step] = adsk.core.Point3D.create(pointleftup + (link*fingerwidthL),0,0)
        pass
    for step in range (2,numberpointsdown + 1):
        link = step - 1
        #pointdown[step] = adsk.core.Point3D.create(pointleftdown + (link*fingerwidthL),heightmfh,0)
        pointdownB[step] = adsk.core.Point3D.create(pointleftdown + (link*fingerwidthL),finger_height,0)
        pass
    for line in range (2,numberpointsup + 2,2):
        #lines.addByTwoPoints(pointup[line - 1], pointup[line])
        #lines.addByTwoPoints(pointup[line- 1],pointdown[line])
        #lines.addByTwoPoints(pointup[line],pointdown[line + 1])
        lines.addByTwoPoints(pointupB[line - 1], pointupB[line])
        lines.addByTwoPoints(pointupB[line- 1],pointdownB[line])
        lines.addByTwoPoints(pointupB[line],pointdownB[line + 1])
        pass
    for line in range (2,numberpointsdown + 2,2):
        #lines.addByTwoPoints(pointdown[line - 1], pointdown[line])
        lines.addByTwoPoints(pointdownB[line - 1], pointdownB[line])
        pass
#############################################################################################################
# Vertical sides next
#############################################################################################################
    numberpointsupV = fingercountH * 2
    numberpointsdownV = (fingercountH * 2) + 2
    numberpointsupV = int(numberpointsupV)
    numberpointsdownV = int(numberpointsdownV)
    pointdownC[1] = pointdownB[1]
    pointupC[1] = adsk.core.Point3D.create(0,finger_height + fingerwidthH,0)
    pointdownD[1] = adsk.core.Point3D.create(length - finger_height,finger_height,0)
    pointupD[1] = adsk.core.Point3D.create(length,finger_height + fingerwidthH,0)
    for step in range (2,numberpointsupV + 1):
        link = step - 1
        pointupC[step] = adsk.core.Point3D.create(0, (finger_height+fingerwidthH )+ (link*fingerwidthH),0)
        #lines.addByTwoPoints(pointupC[step - 1], pointupC[step])
        pointupD[step] = adsk.core.Point3D.create(length,(finger_height+fingerwidthH )+ (link*fingerwidthH),0)
        pass
    for step in range (2,numberpointsdownV + 1):
        link = step - 1
        pointdownC[step] = adsk.core.Point3D.create(finger_height,pointleftdown + (link*fingerwidthH),0)
        pointdownD[step] = adsk.core.Point3D.create(length - finger_height,pointleftdown + (link*fingerwidthH),0)
        pass
    for line in range (2,numberpointsupV + 2,2):
        lines.addByTwoPoints(pointupC[line - 1], pointupC[line])
        lines.addByTwoPoints(pointupC[line- 1],pointdownC[line])
        lines.addByTwoPoints(pointupC[line],pointdownC[line + 1])
        lines.addByTwoPoints(pointupD[line - 1], pointupD[line])
        lines.addByTwoPoints(pointupD[line- 1],pointdownD[line])
        lines.addByTwoPoints(pointupD[line],pointdownD[line + 1])
        pass
    for line in range (2,numberpointsdownV + 2,2):
        lines.addByTwoPoints(pointdownC[line - 1], pointdownC[line])
        lines.addByTwoPoints(pointdownD[line - 1], pointdownD[line])
        pass
    prof = sketch.profiles.item(0)
    extrudeSide(prof,thickness)
    extrudeSide(prof,thickness)
    return
def CreateType5(height,width,fingerwidthH,fingerwidthW,fingercountH,fingercountW, finger_height,thickness):
    test="OFF"
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    if not design:
        ui.messageBox('It is not supported in current workspace, please change to MODEL workspace and try again.')
        return
    currentDesignType = design.designType

    rootComp = design.rootComponent
    if rootComp is None:
        ui.messageBox('New component failed to create', 'New Component Failed')
        return

    sketches = rootComp.sketches
    #Create a new sketch
    sketch = sketches.add(rootComp.xYConstructionPlane)
    # add sketch curves
    lines = sketch.sketchCurves.sketchLines
    #Test draw a box in the sketch
    if test == "ON":
        point0 = adsk.core.Point3D.create(0, 0, 0)
        point1 = adsk.core.Point3D.create(length, 0, 0)
        point2 = adsk.core.Point3D.create(length, width, 0)
        point3 = adsk.core.Point3D.create(0, width, 0)
        lines.addByTwoPoints(point0, point1)
        lines.addByTwoPoints(point1, point2)
        lines.addByTwoPoints(point2, point3)
        lines.addByTwoPoints(point3, point0)
        prof = sketch.profiles.item(0)
        extrudeSide(prof,thickness)
    #################################################################################################
    # Draw the type 3 side geometry
    # points go x,y,z
    ################################################################################################
    heightmfh = height - finger_height
    numberpointsup = fingercountW * 2
    numberpointsdown = (fingercountW * 2) + 2
    numberpointsup = int(numberpointsup)
    numberpointsdown = int(numberpointsdown)
    pointleftup = finger_height + fingerwidthW
    pointleftdown = finger_height + fingerwidthW
    pointup = [0]
    pointdown = [0]
    pointupB = [0]
    pointdownB = [0]
    pointdownC = [0]
    pointupC = [0]
    pointupD = [0]
    pointdownD = [0]
    # This just loads the lists with enough entries for the box.
    for x in range (numberpointsdown+5):
        pointup.append(x)
        pointdown.append(x)
        pointupB.append(x)
        pointdownB.append(x)
        pointupC.append(x)
        pointdownC.append(x)
        pointupD.append(x)
        pointdownD.append(x)
        pass
    pointup[1] = adsk.core.Point3D.create(pointleftup,height,0)
    pointdown[1] = adsk.core.Point3D.create(pointleftdown,heightmfh,0)
    pointupB[1] = adsk.core.Point3D.create(pointleftup,0,0)
    pointdownB[1] = adsk.core.Point3D.create(pointleftdown,finger_height,0)
    pointbl = adsk.core.Point3D.create(0,finger_height,0)
    pointtl = adsk.core.Point3D.create(0,heightmfh,0)
    pointbr = adsk.core.Point3D.create(width,finger_height)
    pointtr = adsk.core.Point3D.create(width,heightmfh)
    pointTopFlat3 = adsk.core.Point3D.create(0,height,0)
    pointTopFlat4 = adsk.core.Point3D.create(width,height,0)
    lines.addByTwoPoints(pointTopFlat3, pointTopFlat4)
    for step in range (2,numberpointsup + 1):
        link = step - 1
        #pointup[step] = adsk.core.Point3D.create(pointleftup + (link*fingerwidthW),height,0)
        pointupB[step] = adsk.core.Point3D.create(pointleftup + (link*fingerwidthW),0,0)
        pass
    for step in range (2,numberpointsdown + 1):
        link = step - 1
        #pointdown[step] = adsk.core.Point3D.create(pointleftdown + (link*fingerwidthW),heightmfh,0)
        pointdownB[step] = adsk.core.Point3D.create(pointleftdown + (link*fingerwidthW),finger_height,0)
        pass
    for line in range (2,numberpointsup + 2,2):
        #lines.addByTwoPoints(pointup[line - 1], pointup[line])
        #lines.addByTwoPoints(pointup[line- 1],pointdown[line -1])
        #lines.addByTwoPoints(pointup[line],pointdown[line])
        lines.addByTwoPoints(pointupB[line - 1], pointupB[line])
        lines.addByTwoPoints(pointupB[line- 1],pointdownB[line -1])
        lines.addByTwoPoints(pointupB[line],pointdownB[line])
        pass
    for line in range (2,numberpointsdown,2):
        #lines.addByTwoPoints(pointdown[line], pointdown[line + 1])
        lines.addByTwoPoints(pointdownB[line], pointdownB[line + 1])
        pass
    lines.addByTwoPoints(pointbl,pointdownB[1])
    #lines.addByTwoPoints(pointtl,pointdown[1])
    lines.addByTwoPoints(pointbr,pointdownB[numberpointsdown - 2])
    #lines.addByTwoPoints(pointtr,pointdown[numberpointsdown - 2])
    ###################################################################################################
    # Now lets create the vertical sides
    ###################################################################################################
    numberpointsupV = fingercountH * 2
    numberpointsdownV = (fingercountH * 2) + 2
    numberpointsupV = int(numberpointsupV)
    numberpointsdownV = int(numberpointsdownV)
    pointleftupV = finger_height + fingerwidthH
    pointleftdownV = finger_height + fingerwidthH
    pointdownC[1] = adsk.core.Point3D.create(finger_height,finger_height + fingerwidthH,0)
    pointupC[1] = adsk.core.Point3D.create(0,finger_height + fingerwidthH,0)
    pointdownD[1] = adsk.core.Point3D.create(width - finger_height,finger_height + fingerwidthH,0)
    pointupD[1] = adsk.core.Point3D.create(width,finger_height + fingerwidthH,0)
    for step in range (2,numberpointsupV + 2):
        link = step - 1
        pointupC[step] = adsk.core.Point3D.create(0, (finger_height+fingerwidthH )+ (link*fingerwidthH),0)
        pointupD[step] = adsk.core.Point3D.create(width,(finger_height+fingerwidthH )+ (link*fingerwidthH),0)
        pass
    for step in range (2,numberpointsdownV + 1):
        link = step - 1
        pointdownC[step] = adsk.core.Point3D.create(finger_height,pointleftdownV + (link*fingerwidthH),0)
        pointdownD[step] = adsk.core.Point3D.create(width - finger_height,pointleftdownV + (link*fingerwidthH),0)
        pass
    for line in range (2,numberpointsupV + 2,2):
        lines.addByTwoPoints(pointupC[line], pointupC[line + 1])
        lines.addByTwoPoints(pointupC[line- 1],pointdownC[line - 1])
        lines.addByTwoPoints(pointupC[line],pointdownC[line])
        lines.addByTwoPoints(pointupD[line], pointupD[line + 1])
        lines.addByTwoPoints(pointupD[line- 1],pointdownD[line - 1])
        lines.addByTwoPoints(pointupD[line],pointdownD[line])
        pass
    for line in range (2,numberpointsdownV,2):
        lines.addByTwoPoints(pointdownC[line - 1], pointdownC[line])
        lines.addByTwoPoints(pointdownD[line - 1], pointdownD[line])
        pass
    lines.addByTwoPoints(pointbl, pointupC[1])
    lines.addByTwoPoints(pointbr, pointupD[1])
    prof = sketch.profiles.item(0)
    extrudeSide(prof,thickness)
    extrudeSide(prof,thickness)
    return
def extrudeSide(prof,thickness):
    # We will extrude the shapes once we complete the sketches
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    if not design:
        ui.messageBox('It is not supported in current workspace, please change to MODEL workspace and try again.')
        return
    currentDesignType = design.designType
    rootComp = design.rootComponent
    if rootComp is None:
        ui.messageBox('New component failed to create', 'New Component Failed')
        return

    profile = prof
    extrudes = rootComp.features.extrudeFeatures
    ext_input = extrudes.createInput(profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    distance = adsk.core.ValueInput.createByReal(thickness)
    ext_input.setDistanceExtent(False, distance)
    ext_input.isSolid = True
    extrudes.add(ext_input)
    return