/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>

@interface PyDateWidget : NSObject {}
- (id)init;

- (NSString *)text;
- (NSArray *)selection; // I can't find a way to pass around a NSRange using the pyobjc signatures

- (void)decrease;
- (void)increase;
- (void)left;
- (void)right;
- (void)backspace;
- (void)exit;
- (void)type:(NSString *)something;
- (void)setDate:(NSString *)str_date;
@end