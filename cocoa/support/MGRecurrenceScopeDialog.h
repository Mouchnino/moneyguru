#import <Cocoa/Cocoa.h>

@interface MGRecurrenceScopeDialog : NSWindowController {}
+ (BOOL)shouldUseGlobalScope;

- (IBAction)chooseGlobalScope:(id)sender;
- (IBAction)chooseLocalScope:(id)sender;
@end