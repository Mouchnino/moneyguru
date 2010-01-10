/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

/*
TEMPORARY UNIT
This unit is created as a temporary hack for the basic view migration. Will disappear when views
have correspondant classes down in the core.
*/

#import <Cocoa/Cocoa.h>
#import "MGPrintView.h"

@interface MGGUIControllerBase : NSObject {}
- (NSView *)view;
- (MGPrintView *)viewToPrint;
@end
