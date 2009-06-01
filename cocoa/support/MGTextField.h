#import <Cocoa/Cocoa.h>
#import "MGFieldEditor.h"

@interface MGTextField : NSTextField {}
- (NSString *)fieldEditor:(MGFieldEditor *)fieldEditor wantsCompletionFor:(NSString *)text;
@end

@interface NSObject(MGTextFieldDelegate)
- (NSString *)autoCompletionForTextField:(MGTextField *)textField partialWord:(NSString *)text;
- (NSString *)currentValueForTextField:(MGTextField *)textField;
- (NSString *)prevValueForTextField:(MGTextField *)textField;
- (NSString *)nextValueForTextField:(MGTextField *)textField;
@end
