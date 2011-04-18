/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "PyGUI.h"

@interface PyImportWindow : PyGUI {}
- (NSInteger)accountCountAtIndex:(NSInteger)index;
- (NSString *)accountNameAtIndex:(NSInteger)index;
- (BOOL)canPerformSwap;
- (void)closePaneAtIndex:(NSInteger)index;
- (void)importSelectedPane;
- (NSInteger)numberOfAccounts;
- (void)performSwap:(BOOL)applyToAll;
- (NSInteger)selectedTargetAccountIndex;
- (void)setSelectedTargetAccountIndex:(NSInteger)index;
- (void)setSelectedAccountIndex:(NSInteger)index;
- (void)setSwapTypeIndex:(NSInteger)index;
- (NSArray *)targetAccountNames;
@end