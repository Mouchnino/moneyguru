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