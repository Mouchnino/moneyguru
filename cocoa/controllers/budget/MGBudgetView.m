/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGBudgetView.h"
#import "MGBudgetPrint.h"
#import "Utils.h"
#import "ObjP.h"

@implementation MGBudgetView
- (id)initWithPy:(id)aPy
{
    PyObject *pRef = getHackedPyRef(aPy);
    PyBudgetView *m = [[PyBudgetView alloc] initWithModel:pRef];
    OBJP_LOCKGIL;
    Py_DECREF(pRef);
    OBJP_UNLOCKGIL;
    self = [super initWithModel:m];
    [m release];
    [NSBundle loadNibNamed:@"BudgetTable" owner:self];
    budgetTable = [[MGBudgetTable alloc] initWithPyRef:[[self model] table] tableView:tableView];
    return self;
}
        
- (void)dealloc
{
    [budgetTable release];
    [super dealloc];
}

- (PyBudgetView *)model
{
    return (PyBudgetView *)model;
}

- (MGPrintView *)viewToPrint
{
    return [[[MGBudgetPrint alloc] initWithPyParent:[self model] tableView:[budgetTable tableView]] autorelease];
}
@end