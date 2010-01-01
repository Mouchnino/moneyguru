/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "MGGUIController.h"
#import "MGDocument.h"
#import "AMButtonBar.h"
#import "PyFilterBar.h"
#import "PyEntryFilterBar.h"

@interface MGFilterBar : MGGUIController
{   
    AMButtonBar *view;
}
- (id)initWithDocument:(MGDocument *)aDocument view:(AMButtonBar *)view forEntryTable:(BOOL)forEntryTable;
- (PyFilterBar *)py;
@end