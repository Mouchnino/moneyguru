#import <Cocoa/Cocoa.h>
#import "PyGUI.h"

@interface PyAccountReassignPanel : PyGUI {}
- (void)loadPanel;
- (void)ok;
- (NSArray *)availableAccounts;
- (int)accountIndex;
- (void)setAccountIndex:(int)index;
@end