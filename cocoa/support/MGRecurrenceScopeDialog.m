/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGRecurrenceScopeDialog.h"
#import "MGConst.h"

@implementation MGRecurrenceScopeDialog
+ (NSInteger)shouldUseGlobalScope
{
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    if (![ud boolForKey:ShowRecurrenceScopeDialog])
        return ScheduleScopeLocal;
    MGRecurrenceScopeDialog *dialog = [[MGRecurrenceScopeDialog alloc] initWithWindowNibName:@"RecurrenceScopeDialog"];
    NSInteger result = [NSApp runModalForWindow:[dialog window]];
    [[dialog window] close];
    [dialog release];
    return result;
}

- (IBAction)cancel:(id)sender
{
    [NSApp stopModalWithCode:ScheduleScopeCancel];
}

- (IBAction)chooseGlobalScope:(id)sender
{
    [NSApp stopModalWithCode:ScheduleScopeGlobal];
}

- (IBAction)chooseLocalScope:(id)sender
{
    [NSApp stopModalWithCode:ScheduleScopeLocal];
}

@end