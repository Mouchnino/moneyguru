/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "PyGUI.h"

@interface PyAccountPanel : PyGUI {}

- (NSString *)name;
- (void)setName:(NSString *)name;
- (NSInteger)typeIndex;
- (void)setTypeIndex:(NSInteger)index;
- (NSInteger)currencyIndex;
- (void)setCurrencyIndex:(NSInteger)index;
- (NSString *)accountNumber;
- (void)setAccountNumber:(NSString *)accountNumber;
- (NSString *)notes;
- (void)setNotes:(NSString *)notes;

- (NSArray *)availableCurrencies;
- (void)savePanel;
@end