/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "PyGUI.h"
#import "MGConst.h"

@interface PyMainWindow : PyGUI {}
- (void)setChildren:(NSArray *)children;
// Navigation
- (BOOL)canSelectEntryTable;
- (void)selectNextView;
- (void)selectPreviousView;
- (NSInteger)currentViewIndex;
- (void)setCurrentViewIndex:(NSInteger)index;
- (NSInteger)viewCount;
- (enum MGViewType)viewTypeAtIndex:(NSInteger)index;
- (void)closeViewAtIndex:(NSInteger)index;
- (void)showAccount;
- (void)navigateBack;
- (void)jumpToAccount;

// Item Management
- (void)deleteItem;
- (void)duplicateItem;
- (void)editItem;
- (void)makeScheduleFromSelected;
- (void)moveDown;
- (void)moveUp;
- (void)newGroup;
- (void)newItem;
@end