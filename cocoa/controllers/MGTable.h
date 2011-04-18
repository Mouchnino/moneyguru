/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "HSTable.h"
#import "MGTableView.h"
#import "MGColumns.h"
#import "PyTable.h"

@interface MGTable : HSTable
{
    MGColumns *columns;
}
- (id)initWithPyClassName:(NSString *)aClassName pyParent:(id)aPyParent view:(MGTableView *)aTableView;

/* Public */
- (PyTable *)py;
- (MGTableView *)tableView;
- (MGColumns *)columns;
@end
