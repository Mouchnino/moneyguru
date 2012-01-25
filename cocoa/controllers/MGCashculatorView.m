/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGCashculatorView.h"
#import "Utils.h"

@implementation MGCashculatorView
- (id)initWithPyRef:(PyObject *)aPyRef
{
    PyCashculatorView *m = [[PyCashculatorView alloc] initWithModel:aPyRef];
    self = [super initWithModel:m];
    [m release];
    [NSBundle loadNibNamed:@"CashculatorView" owner:self];
    accountTable = [[MGCashculatorAccountTable alloc] initWithPyRef:[[self model] table] view:accountTableView];
    return self;
}

- (void)dealloc
{
    [accountTable release];
    [super dealloc];
}

- (PyCashculatorView *)model
{
    return (PyCashculatorView *)model;
}

- (NSString *)tabIconName
{
    return @"cashculator_16";
}

- (IBAction)exportDB:(id)sender
{
    [[self model] exportDB];
}

- (IBAction)launchCC:(id)sender
{
    [[self model] launchCC];
}
@end