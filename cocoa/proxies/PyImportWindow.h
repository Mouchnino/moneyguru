/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "PyGUI.h"

@interface PyImportWindow : PyGUI {}
- (NSInteger)accountCountAtIndex:(NSInteger)index;
- (NSString *)accountNameAtIndex:(NSInteger)index;
- (BOOL)canSwitchDayMonth;
- (BOOL)canSwitchMonthYear;
- (BOOL)canSwitchDayYear;
- (void)closePaneAtIndex:(NSInteger)index;
- (void)importSelectedPane;
- (NSInteger)numberOfAccounts;
- (NSInteger)selectedTargetAccountIndex;
- (void)setSelectedAccountIndex:(NSInteger)index;
- (void)setSelectedTargetAccountIndex:(NSInteger)index;
- (void)switchDayMonth:(BOOL)applyToAll;
- (void)switchMonthYear:(BOOL)applyToAll;
- (void)switchDayYear:(BOOL)applyToAll;
- (void)switchDescriptionPayee:(BOOL)applyToAll;
- (NSArray *)targetAccountNames;
@end