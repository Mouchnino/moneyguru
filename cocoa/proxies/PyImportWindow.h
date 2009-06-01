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