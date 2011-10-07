/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "HSGUIController.h"
#import "AMButtonBar.h"
#import "PyFilterBarBase.h"
#import "PyEntryFilterBar.h"

@interface MGFilterBar : HSGUIController
{   
}
- (id)initWithPyParent:(id)aPyParent view:(AMButtonBar *)view forEntryTable:(BOOL)forEntryTable;
- (PyFilterBarBase *)py;
- (AMButtonBar *)view;
@end