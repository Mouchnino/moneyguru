#import <Cocoa/Cocoa.h>


@interface NSTableView(NSTableViewAdditions)
- (BOOL)dispatchSpecialKeys:(NSEvent *)event;
- (NSNotification *)processTextDidEndEditing:(NSNotification *)notification;
- (void)startEditing;
@end

@interface NSObject(NSTableViewAdditionsDelegate)
- (BOOL)tableViewHadDeletePressed:(NSTableView *)tableView;
- (BOOL)tableViewHadReturnPressed:(NSTableView *)tableView;
- (BOOL)tableViewHadSpacePressed:(NSTableView *)tableView;
- (BOOL)shouldEditTableColumn:(NSTableColumn *)column row:(int)row;
@end