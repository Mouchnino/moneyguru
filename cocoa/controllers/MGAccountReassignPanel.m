/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGAccountReassignPanel.h"
#import "MGMainWindowController.h"
#import "Utils.h"
#import "ObjP.h"

@implementation MGAccountReassignPanel
- (id)initWithParent:(MGMainWindowController *)aParent
{
    PyObject *pRef = getHackedPyRef([[aParent py] accountReassignPanel]);
    PyAccountReassignPanel *m = [[PyAccountReassignPanel alloc] initWithModel:pRef];
    OBJP_LOCKGIL;
    Py_DECREF(pRef);
    OBJP_UNLOCKGIL;
    self = [super initWithNibName:@"AccountReassignPanel" model:m parent:aParent];
    [m bindCallback:createCallback(@"PanelView", self)];
    [m release];
    accountPopUp = [[HSPopUpList2 alloc] initWithPyRef:[[self model] accountList] popupView:accountSelector];
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
