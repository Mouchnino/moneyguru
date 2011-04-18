/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGViewOptions.h"

/* We don't bother defining a PyViewOptions header file because we access py exclusively from XIB
   bindings which don't need any header file.
*/

@implementation MGViewOptions
- (id)initWithPyParent:(id)aPyParent
{
    self = [super initWithNibName:@"ViewOptions" pyClassName:@"PyViewOptions" pyParent:aPyParent];
    return self;
}
@end