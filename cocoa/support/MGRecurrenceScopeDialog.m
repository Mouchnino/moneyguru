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