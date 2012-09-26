/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGDocument.h"
#import "MGMainWindowController.h"
#import "MGConst.h"
#import "Dialogs.h"
#import "MGUndoManager.h"
#import "MGRecurrenceScopeDialog.h"
#import "MGAppDelegate.h"
#import "MGPrintView.h"
#import "HSPyUtil.h"

@implementation MGDocument
- (id)init
{
    self = [super init];
    MGAppDelegate *app = [NSApp delegate];
    model = [[PyDocument alloc] initWithApp:[[app model] pyRef]];
    [self setUndoManager:[[[MGUndoManager alloc] initWithDocumentModel:model] autorelease]];
    [model bindCallback:createCallback(@"DocumentView", self)];
    return self;
}

- (void)dealloc
{
    for (NSWindowController *wc in [self windowControllers]) {
        [wc release];
    }
    [model release];
    [super dealloc];
}

/* For GUI Proxies */

- (PyDocument *)model
{
    return model;
}

/* Override */

- (void)close
{
    [[self model] close];
    // This must not happen in dealloc, because when quitting the app, the dealloc method might not be called
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    [ud synchronize];
    [super close];
}

- (BOOL)isDocumentEdited
{
    return [model isDirty];
}

- (void)makeWindowControllers 
{
    MGMainWindowController *controller = [[MGMainWindowController alloc] initWithDocument:[self model]];
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
    if ([url isFileURL]) {
        NSString *error = [model loadFromFile:[url path]];
        if (error == nil) {
            return YES;
        }
        else {
            NSDictionary *userInfo = [NSDictionary dictionaryWithObject:error forKey:NSLocalizedFailureReasonErrorKey];
            *outError = [NSError errorWithDomain:MGErrorDomain code:MGFileFormatErrorCode userInfo:userInfo];
        }
    }
    return NO;
}

- (BOOL)writeToURL:(NSURL *)url ofType:(NSString *)type error:(NSError **)outError
{
    if ([url isFileURL]) {
        [model saveToFile:[url path]];
        [[self windowForSheet] setDocumentEdited:[self isDocumentEdited]];
        return YES;
    }
    return NO;
}

/* Actions */

- (void)import
{
    NSOpenPanel *op = [NSOpenPanel openPanel];
    [op setCanChooseFiles:YES];
    [op setCanChooseDirectories:NO];
    [op setAllowsMultipleSelection:NO];
    [op setTitle:NSLocalizedString(@"Select a file to import", @"")];
    if ([op runModal] == NSOKButton) {
        NSString *filename = [[[op URLs] objectAtIndex:0] path];
        NSString *error = [model import:filename];
        if (error != nil) {
            [Dialogs showMessage:error];
        }
    }
}

/* Misc */
- (BOOL)isDirty
{
    return [model isDirty];
}

- (void)stopEdition
{
    [model stopEdition];
}

/* Python -> Cocoa */
// Returns ScheduleScope* const
- (NSInteger)queryForScheduleScope
{
    MGAppDelegate *app = [NSApp delegate];
    if (([[NSApp currentEvent] modifierFlags] & NSShiftKeyMask) == NSShiftKeyMask) {
        return ScheduleScopeGlobal;
    }
    else if (!app.model.showScheduleScopeDialog) {
        return ScheduleScopeLocal;
    }
    else {
        MGRecurrenceScopeDialog *dialog = [[MGRecurrenceScopeDialog alloc] init];
        NSInteger result = [dialog run];
        [app.model setShowScheduleScopeDialog:dialog.showDialogNextTime];
        [dialog release];
        return result;
    }
}

@end
