/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGRecurrenceScopeDialog.h"
#import "MGConst.h"
#import "MGRecurrenceScopeDialog_UI.h"

@implementation MGRecurrenceScopeDialog
+ (NSInteger)shouldUseGlobalScope
{
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    if (![ud boolForKey:ShowRecurrenceScopeDialog])
        return ScheduleScopeLocal;
    MGRecurrenceScopeDialog *dialog = [[MGRecurrenceScopeDialog alloc] initWithWindow:nil];
    [dialog setWindow:createMGRecurrenceScopeDialog_UI(dialog)];
    NSInteger result = [NSApp runModalForWindow:[dialog window]];
    [[dialog window] close];
    [dialog release];
    return result;
}

- (void)cancel
{
    [NSApp stopModalWithCode:ScheduleScopeCancel];
}

- (void)chooseGlobalScope
{
    [NSApp stopModalWithCode:ScheduleScopeGlobal];
}

- (void)chooseLocalScope
{
    [NSApp stopModalWithCode:ScheduleScopeLocal];
}

@end