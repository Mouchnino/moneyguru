/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "HSGUIController2.h"
#import "AMButtonBar.h"
#import "PyFilterBar.h"

@interface MGFilterBar : HSGUIController2
{   
}
- (id)initWithPy:(id)aPyParent view:(AMButtonBar *)view forEntryTable:(BOOL)forEntryTable;
- (PyFilterBar *)model;
- (AMButtonBar *)view;
@end