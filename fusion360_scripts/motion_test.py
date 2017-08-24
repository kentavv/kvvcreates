# Example Fusion 360 script for driving a single joint while measuring other joints.
# Can be run with or without Contact Sets enabled.
# Ideally, would be able to perform inspections and make additional measurements, but API 
# may not currently support this. 
#
# Kent A. Vander Velden
# kent.vandervelden@gmail.com
# June 5, 2017
# Released to public domain

import adsk.core, adsk.fusion, traceback, math


def drive_motion(m1, m2, m3):
    # Drive the motion of m1 while recording the angular position of m1, m2, and m3.
    # Drive m1 between v1d and v1d_e in steps of delta degrees. If no progress is
    # made in the position of m2, backoff m1, halve delta, and continue.
    # Continue this way until m1 = v1d_e or delta < delta_min
    # Return a list of positions observed for m1, m2, m3.

    dat = []
    
    v1d = 0
    v1d_e = 50
    delta = 2
    delta_min = .000001
    pv2d = None
    
    while v1d <= v1d_e and delta >= delta_min:    
        v1 = math.radians(v1d)
        m1.rotationValue = v1

        v2 = m2.rotationValue
        v2d = math.degrees(v2)
        
        v3 = m3.rotationValue
        v3d = math.degrees(v3)
        
        dat += [[delta, v1d, v2d, v3d]]        

        # Update the Fusion 360 instance so we can observe the motion progress.        
        adsk.doEvents()

        # If the second joint did not move with the previous step of the first joint, back off and retry with smaller step.
        if pv2d == v2d:
            v1d -= 2*delta
            delta /= 2.
        pv2d = v2d
        
        v1d += delta

    return dat
        
        
def run(context):
    ui = None
    
    try:
        # Boilerplate code to access Fusion 360 instance.
        app = adsk.core.Application.get()
        ui  = app.userInterface

        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        if not design:
            ui.messageBox('It is not supported in current workspace, please change to MODEL workspace and try again.')
            return

        #j1 = ui.selectEntity('Select drive joint', 'Joints').entity
        
        # traverse the assembly tree to find the sub-assembly with the joints to test
        root = design.rootComponent
        part1 = root.occurrences.itemByName('_0006_SA02_Default:1').childOccurrences.itemByName('0006_001_MC01-5_Default:1')
        comp1 = part1.component
        
        # Name the joints in the order to test and extract and cast to their appropriate motion object.
        # For some unknown reason, was never able to access the first joint, Rev6, so ignore that one.
        joint_names = ['Rev6', 'Rev7', 'Rev10', 'Cyl15']
        joints = [part1.component.joints.itemByName(x) for x in joint_names]
        def h(x, f): return f(x.jointMotion) if x else None
        motions = [
            h(joints[0], adsk.fusion.RevoluteJointMotion.cast),
            h(joints[1], adsk.fusion.RevoluteJointMotion.cast),
            h(joints[2], adsk.fusion.RevoluteJointMotion.cast),
            h(joints[3], adsk.fusion.CylindricalJointMotion.cast)
            ]
        
        # Perform the measurements, using the first valid joint as the drive joint.
        dat = drive_motion(*motions[1:])
        
        # Construct and display a summary report
        msg = '\t'.join(['Delta'] + joint_names[1:]) + '\n'
        for lst in dat:
            msg += '{0:.2g}\t{1:.4f}\t{2:.4f}\t{3:.4f}\n'.format(*lst)        
        ui.messageBox(msg)
        
        # Write a CSV file for Excel
        f = open('C:/temp/test2.csv', 'w')
        f.write(msg.replace('\t', ','))

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

    adsk.terminate();
    