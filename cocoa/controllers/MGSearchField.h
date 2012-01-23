/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "HSGUIController.h"
#import "PyTextField.h"

@interface MGSearchField : HSGUIController
{   
    IBOutlet NSSearchField *linkedView; // XXX Why not create the view programmatically?
}
- (id)initWithPyRef:(PyObject *)aPyRef;
- (PyTextField *)model;
- (IBAction)changeQuery:(id)sender;
@end