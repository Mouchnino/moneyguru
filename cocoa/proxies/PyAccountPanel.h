/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "PyGUI.h"

@interface PyAccountPanel : PyGUI {}

- (NSString *)name;
- (void)setName:(NSString *)name;
- (int)typeIndex;
- (void)setTypeIndex:(int)index;
- (int)currencyIndex;
- (void)setCurrencyIndex:(int)index;
- (NSString *)budget;
- (void)setBudget:(NSString *)budget;
- (BOOL)budgetEnabled;
- (int)budgetTargetIndex;
- (void)setBudgetTargetIndex:(int)index;

- (NSArray *)availableCurrencies;
- (NSArray *)availableBudgetTargets;
- (BOOL)canLoadPanel;
- (void)loadPanel;
- (void)savePanel;
@end