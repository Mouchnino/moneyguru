#import <Cocoa/Cocoa.h>
#import "MGTableView.h"
#import "MGGUIController.h"
#import "PyTable.h"

@interface MGTable : MGGUIController
{
    IBOutlet MGTableView *tableView;
    IBOutlet NSView *wholeView;
}

/* Virtual */

- (PyTable *)py;

/* Public */

- (MGTableView *)tableView;

- (void)refresh;
- (void)showSelectedRow;
- (void)updateSelection;

@end
