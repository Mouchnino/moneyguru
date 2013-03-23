/* 
Copyright 2013 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGAccountLookup.h"

@implementation MGAccountLookup
- (id)initWithPyRef:(PyObject *)aPyRef
{
    self = [super initWithPyRef:aPyRef];
    [[self window] setTitle:NSLocalizedString(@"Account Lookup", @"")];
    return self;
}
@end