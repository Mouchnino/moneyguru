/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGCashculatorView.h"
#import "Utils.h"

@implementation MGCashculatorView
- (id)initWithPyParent:(id)aPyParent
{
    self = [super initWithPyClassName:@"PyCashculatorView" pyParent:aPyParent];
    [NSBundle loadNibNamed:@"CashculatorView" owner:self];
    accountTable = [[MGCashculatorAccountTable alloc] initWithPyParent:[self py] view:accountTableView];
    NSArray *children = [NSArray arrayWithObjects:[accountTable py], nil];
    [[self py] setChildren:children];
    return self;
}

- (void)dealloc
{
    [accountTable release];
    [super dealloc];
}

- (PyCashculatorView *)py
{
    return (PyCashculatorView *)py;
}

- (IBAction)updateDB:(id)sender
{
    [[self py] updateDB];
}
@end