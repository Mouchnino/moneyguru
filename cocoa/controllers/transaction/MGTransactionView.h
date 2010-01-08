/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "MGGUIControllerBase.h"
#import "MGDocument.h"
#import "MGTableView.h"
#import "AMButtonBar.h"
#import "MGTransactionTable.h"
#import "MGFilterBar.h"

@interface MGTransactionView : MGGUIControllerBase
{
    IBOutlet MGTableView *tableView;
    IBOutlet NSView *wholeView;
    IBOutlet AMButtonBar *filterBarView;
    IBOutlet NSTextField *totalsLabel;
    
    MGTransactionTable *transactionTable;
    MGFilterBar *filterBar;
}
- (id)initWithDocument:(MGDocument *)aDocument;

// Temporary
- (MGTransactionTable *)transactionTable;
@end