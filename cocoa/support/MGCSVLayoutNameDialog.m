#import "MGCSVLayoutNameDialog.h"
#import "MGConst.h"

@implementation MGCSVLayoutNameDialog
+ (NSString *)askForLayoutName
{
    return [MGCSVLayoutNameDialog askForLayoutNameBasedOnOldName:@""];
}

+ (NSString *)askForLayoutNameBasedOnOldName:(NSString *)oldName
{
    MGCSVLayoutNameDialog *dialog = [[MGCSVLayoutNameDialog alloc] initWithWindowNibName:@"CSVLayoutName"];
    [dialog window]; // Initialize outlets
    [dialog setLayoutName:oldName];
    NSString *result = [NSApp runModalForWindow:[dialog window]] == NSRunStoppedResponse ? [dialog layoutName] : nil;
    [[dialog window] close];
    [dialog release];
    return result;
}

- (IBAction)ok:(id)sender
{
    [NSApp stopModal];
}

- (IBAction)cancel:(id)sender
{
    [NSApp abortModal];
}

- (NSString *)layoutName
{
    return [nameTextField stringValue];
}

- (void)setLayoutName:(NSString *)name
{
    [nameTextField setStringValue:name];
}

@end