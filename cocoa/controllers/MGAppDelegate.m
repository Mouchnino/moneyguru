/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGAppDelegate.h"
#import "MGDocument.h"
#import "MGConst.h"
#import "Utils.h"
#import "HSFairwareReminder.h"
#import "Dialogs.h"
#import "ValueTransformers.h"
#import <Sparkle/SUUpdater.h>

@implementation MGAppDelegate

+ (void)initialize
{
    // Value Transformers
    HSVTAdd *vt = [[[HSVTAdd alloc] initWithValue:4] autorelease];
    [NSValueTransformer setValueTransformer:vt forName:@"vtRowHeightOffset"];
    // Register app-wide defaults
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    NSMutableDictionary *d = [NSMutableDictionary dictionary];
    // Visibility
    [d setObject:b2n(YES) forKey:NetWorthGraphVisible];
    [d setObject:b2n(YES) forKey:AssetLiabilityPieChartVisible];
    [d setObject:b2n(YES) forKey:ProfitGraphVisible];
    [d setObject:b2n(YES) forKey:IncomeExpensePieChartVisible];
    [d setObject:b2n(YES) forKey:AccountGraphVisible];
    // Others
    [d setObject:b2n(YES) forKey:ShowRecurrenceScopeDialog];
    [d setObject:i2n(11) forKey:TableFontSize];
    [d setObject:i2n(11) forKey:PrintFontSize];
    
    [[NSUserDefaultsController sharedUserDefaultsController] setInitialValues:d];
    [ud registerDefaults:d];
}

- (void)awakeFromNib
{
    Class pyClass = [Utils classNamed:@"PyMoneyGuruApp"];
    py = [[pyClass alloc] initWithCocoa:self];
    // Some weird bug showed up, and the first document instance (which get access to MGAppDelegate)
    // through [NSApp delegate] would be created before the NIB unarchiver would set the delegate
    // This is why we set it here.
    [NSApp setDelegate:self];
}

- (void)dealloc
{
    // NSLog(@"AppDelegate dealloc");
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

- (PyMoneyGuruApp *)py
{
    return py;
}

- (IBAction)openExampleDocument:(id)sender
{
    // The goal here is to create a document that behaves as a new document (requires save as), but
    // has the content of the example file.
    NSBundle *bundle = [NSBundle bundleForClass:[self class]];
    NSString *filePath = [bundle pathForResource:@"example" ofType:@"moneyguru"];
    NSDocumentController *dc = [NSDocumentController sharedDocumentController];
    NSError *error;
    MGDocument *doc = [dc makeUntitledDocumentOfType:@"moneyGuru Document" error:&error];
    [doc readFromURL:[NSURL fileURLWithPath:filePath] ofType:@"moneyGuru Document" error:&error];
    [[doc py] adjustExampleFile];
    [dc addDocument:doc];
    [doc makeWindowControllers];
    [doc showWindows];
}

- (IBAction)openWebsite:(id)sender
{
    [[NSWorkspace sharedWorkspace] openURL:[NSURL URLWithString:@"http://www.hardcoded.net/moneyguru/"]];
}

/* Public */
- (void)setCustomDateRangeName:(NSString *)aName atSlot:(NSInteger)aSlot
{
    // setting aName to nil disables the menu item
    NSMenuItem *item;
    if (aSlot == 0) {
        item = customDateRangeItem1;
    }
    else if (aSlot == 1) {
        item = customDateRangeItem2;
    }
    else {
        item = customDateRangeItem3;
    }
    if (aName != nil) {
        [item setHidden:NO];
        [item setEnabled:YES];
        [item setTitle:aName];
    }
    else {
        [item setHidden:YES];
        [item setEnabled:NO];
    }
}

/* delegate */
- (BOOL)applicationShouldOpenUntitledFile:(NSApplication *)sender
{
    return NO;
}

- (void)applicationDidFinishLaunching:(NSNotification *)notification
{
    [HSFairwareReminder showNagWithApp:[self py]];
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    NSDocumentController *dc = [NSDocumentController sharedDocumentController];
    BOOL hadFirstLaunch = [ud boolForKey:@"MGHadFirstLaunch"];
    if (hadFirstLaunch)
    {
        BOOL hasOpenedDocument = [[dc documents] count] > 0; // Could ave been opened through app arguments
        if (!hasOpenedDocument) {
            NSArray *recentURLs = [dc recentDocumentURLs];
            if ([recentURLs count] > 0) {
                NSError *error;
                NSURL *url = [recentURLs objectAtIndex:0];
                [dc openDocumentWithContentsOfURL:url display:YES error:&error];
            }
            else {
                [dc openUntitledDocumentOfType:@"moneyGuru Document" display:YES];
            }
        }
    }
    else {
        if ([Dialogs askYesNo:TR(@"FirstRunMsg")] == NSAlertFirstButtonReturn) {
            [self openExampleDocument:self];
        }
        else {
            [dc openUntitledDocumentOfType:@"moneyGuru Document" display:YES];
        }
        [ud setBool:YES forKey:@"MGHadFirstLaunch"];
    }
    // For some messed up reason, simply notifying of a 'py' change here crashes the app, so the 
    // binding cannot be done in the NIB, it has to be done manually here.
    [firstWeekdayPopup bind:@"selectedIndex" toObject:self withKeyPath:@"py.firstWeekday" options:nil];
    [aheadMonthsPopup bind:@"selectedIndex" toObject:self withKeyPath:@"py.aheadMonths" options:nil];
    [yearStartMonthPopup bind:@"selectedIndex" toObject:self withKeyPath:@"py.yearStartMonth" options:nil];
    [autoSaveIntervalField bind:@"value" toObject:self withKeyPath:@"py.autoSaveInterval" options:nil];
    [autoDecimalPlaceButton bind:@"value" toObject:self withKeyPath:@"py.autoDecimalPlace" options:nil];
}

/* SUUpdater delegate */

- (BOOL)updater:(SUUpdater *)updater shouldPostponeRelaunchForUpdate:(SUAppcastItem *)update untilInvoking:(NSInvocation *)invocation;
{
    continueUpdate = [invocation retain];
    [[NSDocumentController sharedDocumentController] 
        reviewUnsavedDocumentsWithAlertTitle:TR(@"AboutToRestartMsg")
        cancellable:NO delegate:self didReviewAllSelector:@selector(documentController:didReviewAll:contextInfo:)
        contextInfo:nil];
    return YES;
}

- (void)documentController:(NSDocumentController *)docController didReviewAll:(BOOL)didReviewAll contextInfo:(void *)contextInfo
{
    if (didReviewAll) {
        [continueUpdate invoke];
        [continueUpdate release];
    }
}
@end
