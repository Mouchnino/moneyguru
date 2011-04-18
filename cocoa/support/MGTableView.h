/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "NSTableViewAdditions.h"


@interface MGTableView : NSTableView 
{
    BOOL manualEditionStop;
}
- (void)updateSelection;
- (void)stopEditing;
- (IBAction)copy:(id)sender;
@end

@interface NSObject(MGTableViewDelegate)
- (NSString *)autoCompletionForColumn:(NSTableColumn *)column partialWord:(NSString *)partialWord;
- (NSString *)currentValueForColumn:(NSTableColumn *)column;
- (NSString *)prevValueForColumn:(NSTableColumn *)column;
- (NSString *)nextValueForColumn:(NSTableColumn *)column;
- (NSIndexSet *)selectedIndexes;
- (NSString *)dataForCopyToPasteboard;
- (void)tableViewDidEndEditing:(MGTableView *)tableView;
- (void)tableViewCancelsEdition:(MGTableView *)tableView;
- (void)tableViewWasDoubleClicked:(MGTableView *)tableView;
@end

