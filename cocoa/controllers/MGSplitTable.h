#import <Cocoa/Cocoa.h>
#import "MGTableView.h"
#import "MGDocument.h"
#import "PySplitTable.h"
#import "PyTransactionPanel.h"
#import "MGEditableTable.h"

@interface MGSplitTable : MGEditableTable {}

- (void)setTransactionPanel:(PyTransactionPanel *)aPanel;

- (IBAction)addSplit:(id)sender;
- (IBAction)deleteSplit:(id)sender;
@end