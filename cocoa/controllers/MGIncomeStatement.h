/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "HSTableColumnManager.h"
#import "MGDocument.h"
#import "MGReport.h"
#import "MGPieChart.h"
#import "MGBarGraph.h"
#import "MGDoubleView.h"
#import "PyIncomeStatement.h"

@interface MGIncomeStatement : MGReport
{
    HSTableColumnManager *columnsManager;
}
- (id)initWithDocument:(MGDocument *)document view:(MGOutlineView *)aOutlineView;
- (PyIncomeStatement *)py;
@end