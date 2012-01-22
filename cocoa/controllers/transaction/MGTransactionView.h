/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
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
- (id)initWithPy:(id)aPy;

- (PyTransactionView *)model;

- (id)fieldEditorForObject:(id)asker;
@end