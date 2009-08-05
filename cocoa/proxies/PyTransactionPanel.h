/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "PyCompletion.h"

@interface PyTransactionPanel : PyCompletion {}
- (BOOL)canLoadPanel;
- (void)loadPanel;
- (void)savePanel;
- (void)mctBalance;
- (BOOL)canDoMCTBalance;
- (NSString *)date;
- (void)setDate:(NSString *)date;
- (NSString *)description;
- (void)setDescription:(NSString *)description;
- (NSString *)payee;
- (void)setPayee:(NSString *)payee;
- (NSString *)checkno;
- (void)setCheckno:(NSString *)checkno;
- (BOOL)isRecurrent;
- (int)repeatEvery;
- (void)setRepeatEvery:(int)value;
- (NSString *)repeatEveryDesc;
- (int)repeatIndex;
- (void)setRepeatIndex:(int)value;
- (NSArray *)repeatOptions;
@end