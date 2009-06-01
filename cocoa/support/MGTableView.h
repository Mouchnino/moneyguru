#import <Cocoa/Cocoa.h>
#import "NSTableViewAdditions.h"


@interface MGTableView : NSTableView 
{
    BOOL manualEditionStop;
}
- (void)updateSelection;
- (void)stopEditing;
@end

@interface NSObject(MGTableViewDelegate)
- (NSString *)autoCompletionForColumn:(NSTableColumn *)column partialWord:(NSString *)partialWord;
- (NSString *)currentValueForColumn:(NSTableColumn *)column;
- (NSString *)prevValueForColumn:(NSTableColumn *)column;
- (NSString *)nextValueForColumn:(NSTableColumn *)column;
- (NSIndexSet *)selectedIndexes;
- (void)tableViewDidEndEditing:(MGTableView *)tableView;
- (void)tableViewCancelsEdition:(MGTableView *)tableView;
@end

