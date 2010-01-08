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
    return self;
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