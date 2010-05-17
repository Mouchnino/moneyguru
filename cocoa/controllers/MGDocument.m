/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGDocument.h"
#import "MGMainWindowController.h"
#import "MGConst.h"
#import "Utils.h"
#import "Dialogs.h"
#import "MGUndoManager.h"
#import "MGRecurrenceScopeDialog.h"
#import "MGAppDelegate.h"
#import "MGPrintView.h"

@implementation MGDocument

- (id)init
{
    self = [super init];
    MGAppDelegate *app = [NSApp delegate];
    Class pyClass = [Utils classNamed:@"PyDocument"];
    py = [[pyClass alloc] initWithCocoa:self pyParent:[app py]];
    [self setUndoManager:[[[MGUndoManager alloc] initWithPy:[self py]] autorelease]];
    return self;
}

- (void)dealloc
{
    for (NSWindowController *wc in [self windowControllers]) {
        [wc release];
    }
    [py release];
    [super dealloc];
}

- (oneway void)release
{
    // See HSGUIController
    if ([self retainCount] == 2)
    {
        [py free];
    }
    [super release];
}
/* For GUI Proxies */

- (PyDocument *)py
{
    return py;
}

/* Override */

- (void)close
{
    [[self py] close];
    // This must not happen in dealloc, because when quitting the app, the dealloc method might not be called
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    [ud synchronize];
    [super close];
}

- (BOOL)isDocumentEdited
{
    return [py isDirty];
}

- (void)makeWindowControllers 
{
    MGMainWindowController *controller = [[MGMainWindowController alloc] initWithDocument:self];
    /* Ok, this call below to set docoument to nil is hacky, but the thing is that we need to set
     * the document during initialization to avoid crashes, and then we need to set it to nil here
     * or else the window controller won't really get added in addWindowController:
     */
    [controller setDocument:nil];
    [controller setShouldCloseDocument:YES];
    [self addWindowController:[controller autorelease]];
}

- (NSPrintOperation *)printOperationWithSettings:(NSDictionary *)printSettings error:(NSError **)outError
{
    NSPrintInfo *pi = [self printInfo];
    [pi setHorizontalPagination:NSFitPagination];
    MGMainWindowController *mw = [[self windowControllers] objectAtIndex:0];
    MGPrintView *viewToPrint = [mw viewToPrint];
    [viewToPrint setUpWithPrintInfo:pi];
    return [NSPrintOperation printOperationWithView:viewToPrint printInfo:pi];
}

- (BOOL)readFromURL:(NSURL *)url ofType:(NSString *)type error:(NSError **)outError
{
    if ([url isFileURL])
    {
        NSString *error = [py loadFromFile:[url path]];
        if (error == nil)
        {
            return YES;
        }
        else
        {
            NSDictionary *userInfo = [NSDictionary dictionaryWithObject:error forKey:NSLocalizedFailureReasonErrorKey];
            *outError = [NSError errorWithDomain:MGErrorDomain code:MGFileFormatErrorCode userInfo:userInfo];
        }
    }
    return NO;
}

- (BOOL)writeToURL:(NSURL *)url ofType:(NSString *)type error:(NSError **)outError
{
    if ([url isFileURL])
    {
        NSString *error = nil;
        // Eventually, it might be a good idea to make core.document raise RegistrationRequired,
        // which would then be caught in mg_cocoa and which would return a proper NSError to use here.
        MGAppDelegate *app = [NSApp delegate];
        if (![[app py] isRegistered])
        {
            if ([py transactionCount] > 100)
            {
                error = @"You have reached the limits of this demo version. You must buy moneyGuru to save the document.";
                NSDictionary *userInfo = [NSDictionary dictionaryWithObject:error forKey:NSLocalizedFailureReasonErrorKey];
                *outError = [NSError errorWithDomain:MGErrorDomain code:MGDemoLimitErrorCode userInfo:userInfo];
                return NO;
            }
        }
        [py saveToFile:[url path]];
        return YES;
    }
    return NO;
}

/* Actions */

- (IBAction)import:(id)sender
{
    NSOpenPanel *op = [NSOpenPanel openPanel];
    [op setCanChooseFiles:YES];
    [op setCanChooseDirectories:NO];
    [op setAllowsMultipleSelection:NO];
    [op setTitle:@"Select a file to import"];
    if ([op runModalForTypes:nil] == NSOKButton)
    {
        NSString *filename = [[op filenames] objectAtIndex:0];
        NSString *error = [py import:filename];
        if (error != nil)
        {
            [Dialogs showMessage:error];
        }
    }
}

- (IBAction)saveToQIF:(id)sender
{
    NSSavePanel *sp = [NSSavePanel savePanel];
    [sp setCanCreateDirectories:YES];
    [sp setTitle:@"Export to QIF"];
    if ([sp runModalForDirectory:nil file:@"export.qif"] == NSOKButton)
    {
        NSString *filename = [sp filename];
        [py saveToQIF:filename];
    }
}

/* Misc */
- (BOOL)isDirty
{
    return [py isDirty];
}

- (void)stopEdition
{
    [py stopEdition];
}

/* Python -> Cocoa */
// YES: affects the rest of the recurrence 
// NO: affects just this instance
- (BOOL)queryForScheduleScope
{
    if (([[NSApp currentEvent] modifierFlags] & NSShiftKeyMask) == NSShiftKeyMask)
        return ScheduleScopeGlobal;
    else
        return [MGRecurrenceScopeDialog shouldUseGlobalScope];
}

@end
