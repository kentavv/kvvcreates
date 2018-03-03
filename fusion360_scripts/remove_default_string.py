# Recursively traverse the Fusion 360 assembly tree, removing the trailing 
# "_Default" string from component names, which is common with STEP files 
# imported from Misumi
#
# Kent A. Vander Velden
# kent.vandervelden@gmail.com
# June 5, 2017
# Released to public domain

import adsk.core, adsk.fusion, traceback, re

        
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

        # Traverse the assembly tree updating component names by replacing
        # the re_str (a regular expression) with repl_str.
        # Accumulate name changes into a string that's finally returned.
        root = design.rootComponent
        def h(comp, re_str, repl_str):
            msg = ''
            if comp:
                for x in comp.occurrences:
                    x = x.component
                    new_name = re.sub(re_str, repl_str, x.name)
                    if x.name != new_name:
                        msg += x.name + ' -> ' + new_name + '\n'
                        x.name = new_name
                    msg += h(x, re_str, repl_str)
            return msg
            
        msg = h(root, '_Default$', '')

        if msg == '':
            msg = 'No names changed'
        else:
            msg = 'Name changes:\n' + msg
        ui.messageBox(msg)
        
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

    adsk.terminate();
    