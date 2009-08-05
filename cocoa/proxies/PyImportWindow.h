/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "PyGUI.h"

@interface PyImportWindow : PyGUI {}
- (int)accountCountAtIndex:(int)index;
- (NSString *)accountNameAtIndex:(int)index;
- (BOOL)canSwitchDayMonth;
- (BOOL)canSwitchMonthYear;
- (BOOL)canSwitchDayYear;
- (void)closePaneAtIndex:(int)index;
- (void)importSelectedPane;
- (int)numberOfAccounts;
- (int)selectedTargetAccountIndex;
- (void)setSelectedAccountIndex:(int)index;
- (void)setSelectedTargetAccountIndex:(int)index;
- (void)switchDayMonth:(BOOL)applyToAll;
- (void)switchMonthYear:(BOOL)applyToAll;
- (void)switchDayYear:(BOOL)applyToAll;
- (void)switchDescriptionPayee:(BOOL)applyToAll;
- (NSArray *)targetAccountNames;
@end