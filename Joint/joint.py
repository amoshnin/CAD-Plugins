import adsk.core, adsk.fusion, traceback

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        # Create a document.
        doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)

        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)

        # Get the root component of the active design
        rootComp = design.rootComponent

        # Create sketch in root component
        sketches = rootComp.sketches
        sketch = sketches.add(rootComp.xZConstructionPlane)
        sketchCircles = sketch.sketchCurves.sketchCircles
        sketchLines = sketch.sketchCurves.sketchLines
        centerPoint = adsk.core.Point3D.create(0, 0, 0)
        circle = sketchCircles.addByCenterRadius(centerPoint, 5.0)
        point0 = adsk.core.Point3D.create(0, 10, 0)
        point1 = adsk.core.Point3D.create(10, 10, 0)
        line = sketchLines.addByTwoPoints(point0, point1)

        # Get the profile defined by the circle
        prof = sketch.profiles.item(0)

        # Create an extrusion input and make sure it's in a new component
        extrudes = rootComp.features.extrudeFeatures
        extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewComponentFeatureOperation)

        # Set the extrusion input
        distance = adsk.core.ValueInput.createByReal(5)
        extInput.setDistanceExtent(True, distance)
        extInput.isSolid = True

        # Create the extrusion
        ext = extrudes.add(extInput)

        # Get the end face of the created extrusion body
        endFace = ext.endFaces.item(0)

        # Create the first joint geometry with the end face
        geo0 = adsk.fusion.JointGeometry.createByPlanarFace(endFace, None, adsk.fusion.JointKeyPointTypes.CenterKeyPoint)

        # Create the second joint geometry with the sketch line
        geo1 = adsk.fusion.JointGeometry.createByCurve(line, adsk.fusion.JointKeyPointTypes.EndKeyPoint)

        # Create joint input
        joints = rootComp.joints
        jointInput = joints.createInput(geo0, geo1)

        # Set the joint input
        angle = adsk.core.ValueInput.createByString('90 deg')
        jointInput.angle = angle
        offset = adsk.core.ValueInput.createByString('1 cm')
        jointInput.offset = offset
        jointInput.isFlipped = True
        jointInput.setAsRevoluteJointMotion(adsk.fusion.JointDirections.ZAxisJointDirection)

        # Create the joint
        joint = joints.add(jointInput)

        # Lock the joint
        joint.isLocked = True

        # Get health state of a joint
        health = joint.healthState
        if health == adsk.fusion.FeatureHealthStates.ErrorFeatureHealthState or health == adsk.fusion.FeatureHealthStates.WarningFeatureHealthState:
            message = joint.errorOrWarningMessage

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))