/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "PyTransactionView.h"
#import "MGBaseView.h"
#import "MGTableView.h"
#import "AMButtonBar.h"
#import "MGTransactionTable.h"
#import "MGFilterBar.h"

@interface MGTransactionView : MGBaseView
{
    IBOutlet MGTableView *tableView;
    IBOutlet AMButtonBar *filterBarView;
    
    MGTransactionTable *transactionTable;
    MGFilterBar *filterBar;
}
- (id)initWithPyParent:(id)aPyParent;

- (PyTransactionView *)py;

- (id)fieldEditorForObject:(id)asker;
@end