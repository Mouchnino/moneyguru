#import <Cocoa/Cocoa.h>
#import "MGTableView.h"
#import "MGTable.h"
#import "PyTable.h"

@interface MGEditableTable : MGTable
{
}

/* Private */

- (void)changeColumns; // call this right after init

/* Public */

- (void)add;
- (void)deleteSelected;
- (void)startEditing;
- (void)stopEditing;

@end
