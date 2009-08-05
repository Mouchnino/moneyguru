/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGRecurrenceScopeDialog.h"
#import "MGConst.h"

#define MGLocalScopeChosen 1
#define MGGlobalScopeChosen 2

@implementation MGRecurrenceScopeDialog
+ (BOOL)shouldUseGlobalScope
{
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    if (![ud boolForKey:ShowRecurrenceScopeDialog])
        return NO;
    MGRecurrenceScopeDialog *dialog = [[MGRecurrenceScopeDialog alloc] initWithWindowNibName:@"RecurrenceScopeDialog"];
    BOOL result = [NSApp runModalForWindow:[dialog window]] == MGGlobalScopeChosen;
    [[dialog window] close];
    [dialog release];
    return result;
}

- (IBAction)chooseGlobalScope:(id)sender
{
    [NSApp stopModalWithCode:MGGlobalScopeChosen];
}

- (IBAction)chooseLocalScope:(id)sender
{
    [NSApp stopModalWithCode:MGLocalScopeChosen];
}

@end