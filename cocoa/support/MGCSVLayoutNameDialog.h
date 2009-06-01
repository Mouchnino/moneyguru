#import <Cocoa/Cocoa.h>

@interface MGCSVLayoutNameDialog : NSWindowController
{
    IBOutlet NSTextField *nameTextField;
}
+ (NSString *)askForLayoutName;
+ (NSString *)askForLayoutNameBasedOnOldName:(NSString *)oldName;

- (IBAction)ok:(id)sender;
- (IBAction)cancel:(id)sender;

- (NSString *)layoutName;
- (void)setLayoutName:(NSString *)name;
@end