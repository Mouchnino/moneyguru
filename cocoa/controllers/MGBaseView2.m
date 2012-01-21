/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGBaseView2.h"

@implementation MGBaseView2
- (NSView *)view
{
    return wholeView;
}

- (MGPrintView *)viewToPrint
{
    return nil;
}

- (NSResponder *)mainResponder
{
    return mainResponder;
}
@end