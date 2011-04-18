/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "PyTransactionTable.h"
#import "MGEditableTable.h"
#import "MGTableView.h"

@interface MGTransactionTable : MGEditableTable {}
- (id)initWithPyParent:(id)aPyParent view:(MGTableView *)aTableView;
- (void)initializeColumns;

/* Public */
- (PyTransactionTable *)py;
- (void)showFromAccount:(id)sender;
- (void)showToAccount:(id)sender;
@end
