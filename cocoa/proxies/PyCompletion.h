#import <Cocoa/Cocoa.h>
#import "PyGUI.h"

@interface PyCompletion : PyGUI {}

- (NSString *)completeValue:(NSString *)value forAttribute:(NSString *)column;
- (NSString *)currentCompletion;
- (NSString *)nextCompletion;
- (NSString *)prevCompletion;
@end