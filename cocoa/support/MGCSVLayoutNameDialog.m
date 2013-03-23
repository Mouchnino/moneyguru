/* 
Copyright 2013 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGCSVLayoutNameDialog.h"
#import "MGCSVLayoutNameDialog_UI.h"
#import "MGConst.h"

@implementation MGCSVLayoutNameDialog

@synthesize nameTextField;

+ (NSString *)askForLayoutName
{
    return [MGCSVLayoutNameDialog askForLayoutNameBasedOnOldName:@""];
}

+ (NSString *)askForLayoutNameBasedOnOldName:(NSString *)oldName
{
    MGCSVLayoutNameDialog *dialog = [[MGCSVLayoutNameDialog alloc] initWithWindow:nil];
    [dialog setWindow:createMGCSVLayoutNameDialog_UI(dialog)];
    [dialog setLayoutName:oldName];
    NSString *result = [NSApp runModalForWindow:[dialog window]] == NSRunStoppedResponse ? [dialog layoutName] : nil;
    [[dialog window] close];
    [dialog release];
    return result;
}

- (void)ok
{
    [NSApp stopModal];
}

- (void)cancel
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