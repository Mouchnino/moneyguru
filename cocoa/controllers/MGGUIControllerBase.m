/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGGUIControllerBase.h"

@implementation MGGUIControllerBase
- (NSView *)view
{
    // abstract
    return nil;
}

- (MGPrintView *)viewToPrint
{
    return nil;
}
@end