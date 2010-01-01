/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

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