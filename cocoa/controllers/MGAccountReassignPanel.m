/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGAccountReassignPanel.h"
#import "MGMainWindowController.h"
#import "HSPyUtil.h"

@implementation MGAccountReassignPanel
- (id)initWithParent:(MGMainWindowController *)aParent
{
    PyAccountReassignPanel *m = [[PyAccountReassignPanel alloc] initWithModel:[[aParent model] accountReassignPanel]];
    self = [super initWithNibName:@"AccountReassignPanel" model:m parent:aParent];
    [m bindCallback:createCallback(@"PanelView", self)];
    [m release];
    accountPopUp = [[HSPopUpList alloc] initWithPyRef:[[self model] accountList] popupView:accountSelector];
    return self;
}

- (void)dealloc
{
    [accountPopUp release];
    [super dealloc];
}

- (PyAccountReassignPanel *)model
{
    return (PyAccountReassignPanel *)model;
}

/* Override */
- (NSResponder *)firstField
{
    return accountSelector;
}
@end
