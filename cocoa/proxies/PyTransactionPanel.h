/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "PyPanel.h"

@interface PyTransactionPanel : PyPanel {}
- (NSString *)date;
- (void)setDate:(NSString *)date;
- (NSString *)description;
- (void)setDescription:(NSString *)description;
- (NSString *)payee;
- (void)setPayee:(NSString *)payee;
- (NSString *)checkno;
- (void)setCheckno:(NSString *)checkno;
- (NSString *)amount;
- (void)setAmount:(NSString *)amount;
- (void)mctBalance;
- (BOOL)canDoMCTBalance;
@end