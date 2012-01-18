/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGCashculatorView.h"
#import "Utils.h"

@implementation MGCashculatorView
- (id)initWithPy:(id)aPy
{
    self = [super initWithPy:aPy];
    [NSBundle loadNibNamed:@"CashculatorView" owner:self];
    accountTable = [[MGCashculatorAccountTable alloc] initWithPy:[[self py] table] view:accountTableView];
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

- (IBAction)exportDB:(id)sender
{
    [[self py] exportDB];
}

- (IBAction)launchCC:(id)sender
{
    [[self py] launchCC];
}
@end