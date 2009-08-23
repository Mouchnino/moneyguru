/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "PyPanel.h"

@interface PyBudgetPanel : PyPanel {}
- (NSString *)startDate;
- (void)setStartDate:(NSString *)startDate;
- (NSString *)stopDate;
- (void)setStopDate:(NSString *)stopDate;
- (int)repeatEvery;
- (void)setRepeatEvery:(int)value;
- (NSString *)repeatEveryDesc;
- (int)repeatTypeIndex;
- (void)setRepeatTypeIndex:(int)value;
- (NSArray *)repeatOptions;
- (int)accountIndex;
- (void)setAccountIndex:(int)index;
- (int)targetIndex;
- (void)setTargetIndex:(int)index;
- (NSString *)amount;
- (void)setAmount:(NSString *)amount;

- (NSArray *)accountOptions;
- (NSArray *)targetOptions;
@end