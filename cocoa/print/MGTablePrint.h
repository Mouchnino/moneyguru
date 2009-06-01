#import <Cocoa/Cocoa.h>
#import "MGPrintView.h"

@interface MGTablePrint : MGPrintView
{
    NSTableView *tableView;
    
    float columnHeaderY;
    NSFont *rowFont;
    NSDictionary *rowAttributes;
    float rowTextHeight;
    float typicalRowHeight;
    float lastRowYOnLastPage;
    int rowCount;
    NSMutableArray *cellData;
    NSMutableArray *columnWidths;
    NSMutableArray *rowHeights;
}

- (id)initWithPyParent:(id)pyParent tableView:(NSTableView *)aTableView;

- (id)objectValueForTableColumn:(NSTableColumn *)aColumn row:(int)aRow;
- (void)willDisplayCell:(NSCell *)aCell forTableColumn:(NSTableColumn *)aColumn row:(int)aRow;
- (float)indentForTableColumn:(NSTableColumn *)aColumn row:(int)aRow;
- (float)heightForRow:(int)aRow;
- (NSArray *)unresizableColumns;
- (void)drawRow:(int)aRow inRect:(NSRect)aRect;
- (float)columnsTotalWidth;
@end