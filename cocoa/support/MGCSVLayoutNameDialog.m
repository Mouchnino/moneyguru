/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

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