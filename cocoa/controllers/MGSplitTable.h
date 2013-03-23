/* 
Copyright 2013 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "MGTableView.h"
#import "PySplitTable.h"
#import "PyPanel.h"
#import "MGEditableTable.h"

@interface MGSplitTable : MGEditableTable {}
- (id)initWithPyRef:(PyObject *)aPyRef tableView:(MGTableView *)aTableView;
- (void)initializeColumns;
- (PySplitTable *)model;
@end