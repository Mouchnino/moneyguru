/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGDocument.h"
#import "MGMainWindow.h"
#import "MGConst.h"
#import "Utils.h"
#import "Dialogs.h"
#import "MGUndoManager.h"
#import "MGUtils.h"
#import "MGRecurrenceScopeDialog.h"
#import "MGUnreconciliationDialog.h"
#import "MGAppDelegate.h"
#import "MGPrintView.h"

@implementation MGDocument

- (id)init
{
    self = [super init];
    MGAppDelegate *app = [NSApp delegate];
    Class pyClass = [MGUtils classNamed:@"PyDocument"];
    py = [[pyClass alloc] initWithCocoa:self pyParent:[app py]];
    [self setUndoManager:[[[MGUndoManager alloc] initWithPy:[self py]] autorelease]];
    [self registerDefaults]; // register new file defaults
    return self;
}

- (void)dealloc
{
    // NSLog(@"Document dealloc");
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    [ud synchronize];
    [py release];
    [super dealloc];
}

- (oneway void)release
{
    // See MGGUIController
    if ([self retainCount] == 2)
    {
        [py free];
    }
    [super release];
}

/* Private */

// Register default values for document based preferences
- (void)registerDefaults
{
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    NSString *key = [self documentDefaultsKey];
    NSMutableDictionary *d = [NSMutableDictionary dictionary];
    NSArray *expandedItems = [NSArray arrayWithObjects:@"0", @"1",nil]; // the 2 top level nodes
    [d setObject:expandedItems forKey:[NSString stringWithFormat:@"%@.BalanceSheet.ExpandedItems",key]];
    [d setObject:expandedItems forKey:[NSString stringWithFormat:@"%@.IncomeStatement.ExpandedItems",key]];
    [[NSUserDefaultsController sharedUserDefaultsController] setInitialValues:d];
    [ud registerDefaults:d];
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
    [super close];
}

- (BOOL)isDocumentEdited
{
    return [py isDirty];
}

- (void)makeWindowControllers 
{
    MGMainWindow *controller = [[[MGMainWindow alloc] initWithWindowNibName:@"MainWindow"] autorelease];
    [controller setShouldCloseDocument:YES];
    [self addWindowController:controller];
}

- (NSPrintOperation *)printOperationWithSettings:(NSDictionary *)printSettings error:(NSError **)outError
{
    NSPrintInfo *pi = [self printInfo];
    [pi setHorizontalPagination:NSFitPagination];
    MGMainWindow *mw = [[self windowControllers] objectAtIndex:0];
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
        if (![[self py] isRegistered])
        {
            if ([py transactionCount] > 100)
            {
                error = @"You have reached the limits of this demo version. You must buy moneyGuru to save the document.";
                NSDictionary *userInfo = [NSDictionary dictionaryWithObject:error forKey:NSLocalizedFailureReasonErrorKey];
                *outError = [NSError errorWithDomain:MGErrorDomain code:MGDemoLimitErrorCode userInfo:userInfo];
                return NO;
            }
        }
        error = [py saveToFile:[url path]];
        if (error == nil)
            return YES;
        else
        {
            NSDictionary *userInfo = [NSDictionary dictionaryWithObject:error forKey:NSLocalizedFailureReasonErrorKey];
            *outError = [NSError errorWithDomain:MGErrorDomain code:MGUnknownErrorCode userInfo:userInfo];
        }
    }
    return NO;
}

- (void)setFileURL:(NSURL *)absoluteURL
{
    [super setFileURL:absoluteURL];
    [self registerDefaults];
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

- (void)selectMonthRange
{
    [py selectMonthRange];
}

- (void)selectQuarterRange
{
    [py selectQuarterRange];
}

- (void)selectYearRange
{
    [py selectYearRange];
}

- (void)selectYearToDateRange
{
    [py selectYearToDateRange];
}

- (void)selectRunningYearRange
{
    [py selectRunningYearRange];
}

- (void)selectCustomDateRange
{
    [py selectCustomDateRange];
}

- (void)stopEdition
{
    [py stopEdition];
}

- (NSString *)documentDefaultsKey
{
    NSURL *path = [self fileURL];
    NSString *strPath = path == nil ? @"NewFile" : [path absoluteString];
    return [NSString stringWithFormat:@"DocumentBased.%@",strPath];
}

- (id)defaultForKey:(NSString *)aKey
{
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    NSString *wholeKey = [NSString stringWithFormat:@"%@.%@",[self documentDefaultsKey],aKey];
    return [ud objectForKey:wholeKey];
}

- (void)setDefault:(id)aDefault forKey:(NSString *)aKey
{
    if ([self fileURL] == nil)
    {
        // Dont't write preferences for new files. They are always on default values.
        return;
    }
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    NSString *wholeKey = [NSString stringWithFormat:@"%@.%@",[self documentDefaultsKey],aKey];
    [ud setObject:aDefault forKey:wholeKey];
}

/* Python -> Cocoa */

- (int)confirmUnreconciliation:(int)affectedSplitCount
{
    return [MGUnreconciliationDialog shouldUnreconcileWithAffectedSplitCount:affectedSplitCount];
}

// YES: affects the rest of the recurrence 
// NO: affects just this instance
- (BOOL)queryForScheduleScope
{
    if (([[NSApp currentEvent] modifierFlags] & NSShiftKeyMask) == NSShiftKeyMask)
        return YES;
    else
        return [MGRecurrenceScopeDialog shouldUseGlobalScope];
}

@end
