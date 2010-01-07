/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGRecurrenceScopeDialog.h"
#import "MGConst.h"

@implementation MGRecurrenceScopeDialog
+ (int)shouldUseGlobalScope
{
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    if (![ud boolForKey:ShowRecurrenceScopeDialog])
        return ScheduleScopeLocal;
    MGRecurrenceScopeDialog *dialog = [[MGRecurrenceScopeDialog alloc] initWithWindowNibName:@"RecurrenceScopeDialog"];
    int result = [NSApp runModalForWindow:[dialog window]];
    [[dialog window] close];
    [dialog release];
    return result;
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