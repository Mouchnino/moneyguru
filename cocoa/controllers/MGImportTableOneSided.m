/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGImportTableOneSided.h"
#import "Utils.h"
#import "MGConst.h"

@implementation MGImportTableOneSided
- (id)initWithImportWindow:(PyImportWindow *)aWindow view:(MGTableView *)aTableView
{
    self = [super initWithPyClassName:@"PyImportTable" pyParent:aWindow view:aTableView];
    [self initializeColumns];
    return self;
}

- (void)initializeColumns
{
    MGColumnDef defs[] = {
        {@"will_import", @"", 14, 14, 14, NO, [NSButtonCell class]},
        {@"date_import", @"Date", 55, 10, 0, NO, nil},
        {@"description_import", @"Description", 107, 10, 0, NO, nil},
        {@"payee_import", @"Payee", 106, 10, 0, NO, nil},
        {@"checkno_import", @"Check #", 60, 10, 0, NO, nil},
        {@"transfer_import", @"Transfer", 95, 10, 0, NO, nil},
        {@"amount_import", @"Amount", 71, 10, 0, NO, nil},
        nil
    };
    [[self columns] initializeColumns:defs];
    NSTableColumn *c = [[self tableView] tableColumnWithIdentifier:@"will_import"];
    NSButtonCell *cell = [c dataCell];
    [cell setButtonType:NSSwitchButton];
    [cell setControlSize:NSSmallControlSize];
    c = [[self tableView] tableColumnWithIdentifier:@"amount_import"];
    [[c headerCell] setAlignment:NSRightTextAlignment];
    [[c dataCell] setAlignment:NSRightTextAlignment];
}

- (PyImportTable *)py
{
    return (PyImportTable *)py;
}

- (BOOL)tableViewHadSpacePressed:(NSTableView *)tableView
{
    [[self py] toggleImportStatus];
    return YES;
}
@end