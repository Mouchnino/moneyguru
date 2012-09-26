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

@synthesize showDialogNextTime;

- (id)init
{
    self = [super initWithWindow:nil];
    self.showDialogNextTime = YES; // If we're showing this, it means that our pref is set to true
    [self setWindow:createMGRecurrenceScopeDialog_UI(self)];
    return self;
}

- (NSInteger)run
{
    NSInteger result = [NSApp runModalForWindow:[self window]];
    [[self window] close];
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