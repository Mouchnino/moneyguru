/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "PyPanel.h"
#import "PyCompletableEdit.h"

@interface PyMassEditionPanel : PyPanel {}
- (PyCompletableEdit *)completableEdit;
- (NSArray *)availableCurrencies;
- (BOOL)canChangeAccounts;
- (BOOL)canChangeAmount;
- (BOOL)dateEnabled;
- (void)setDateEnabled:(BOOL)enabled;
- (BOOL)descriptionEnabled;
- (void)setDescriptionEnabled:(BOOL)enabled;
- (BOOL)payeeEnabled;
- (void)setPayeeEnabled:(BOOL)enabled;
- (BOOL)checknoEnabled;
- (void)setChecknoEnabled:(BOOL)enabled;
- (BOOL)fromEnabled;
- (void)setFromEnabled:(BOOL)enabled;
- (BOOL)toEnabled;
- (void)setToEnabled:(BOOL)enabled;
- (BOOL)amountEnabled;
- (void)setAmountEnabled:(BOOL)enabled;
- (BOOL)currencyEnabled;
- (void)setCurrencyEnabled:(BOOL)enabled;
- (NSString *)date;
- (void)setDate:(NSString *)date;
- (NSString *)description;
- (void)setDescription:(NSString *)description;
- (NSString *)payee;
- (void)setPayee:(NSString *)payee;
- (NSString *)checkno;
- (void)setCheckno:(NSString *)checkno;
- (NSString *)fromAccount;
- (void)setFromAccount:(NSString *)checkno;
- (NSString *)to;
- (void)setTo:(NSString *)checkno;
- (NSString *)amount;
- (void)setAmount:(NSString *)checkno;
- (NSInteger)currencyIndex;
- (void)setCurrencyIndex:(NSInteger)index;
@end