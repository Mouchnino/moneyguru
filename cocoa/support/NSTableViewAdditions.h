/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

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
- (BOOL)shouldEditTableColumn:(NSTableColumn *)column row:(NSInteger)row;
@end