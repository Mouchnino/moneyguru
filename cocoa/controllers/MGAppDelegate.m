/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGAppDelegate.h"
#import "MGDocument.h"
#import "MGConst.h"
#import "Utils.h"
#import "HSFairwareReminder.h"
#import "Dialogs.h"
#import "ValueTransformers.h"
#import "MGDocumentController.h"
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
    [_aboutBox release];
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

- (IBAction)openHelp:(id)sender
{
    NSBundle *b = [NSBundle mainBundle];
    NSString *p = [b pathForResource:@"index" ofType:@"html" inDirectory:@"help"];
    NSURL *u = [NSURL fileURLWithPath:p];
    [[NSWorkspace sharedWorkspace] openURL:u];
}

- (IBAction)showAboutBox:(id)sender
{
    if (_aboutBox == nil) {
        _aboutBox = [[HSAboutBox alloc] initWithApp:py];
    }
    [[_aboutBox window] makeKeyAndOrderFront:sender];
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

- (void)applicationWillFinishLaunching:(NSNotification *)notification
{
    // We create the first NSDocumentController instance here, which sets the shared instance used
    // throughout the app.
    [[MGDocumentController alloc] init];
}

- (void)applicationDidFinishLaunching:(NSNotification *)notification
{
    [py initialRegistrationSetup];
    MGDocumentController *dc = [NSDocumentController sharedDocumentController];
    BOOL isFirstRun = [[self py] isFirstRun];
    if (isFirstRun) {
        if ([Dialogs askYesNo:TR(@"This is your first time running moneyGuru. Do you want to open the example file?")] == NSAlertFirstButtonReturn) {
            [self openExampleDocument:self];
        }
        else {
            NSError *error;
            [dc openUntitledDocumentAndDisplay:YES error:&error];
        }
    }
    else {
        [dc openFirstDocument];
    }
    // For some messed up reason, simply notifying of a 'py' change here crashes the app, so the 
    // binding cannot be done in the NIB, it has to be done manually here.
    [autoSaveIntervalField bind:@"value" toObject:self withKeyPath:@"py.autoSaveInterval" options:nil];
    [autoDecimalPlaceButton bind:@"value" toObject:self withKeyPath:@"py.autoDecimalPlace" options:nil];
}

/* SUUpdater delegate */

- (BOOL)updater:(SUUpdater *)updater shouldPostponeRelaunchForUpdate:(SUAppcastItem *)update untilInvoking:(NSInvocation *)invocation;
{
    continueUpdate = [invocation retain];
    [[NSDocumentController sharedDocumentController] 
        reviewUnsavedDocumentsWithAlertTitle:TR(@"moneyGuru is about to restart")
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

/* model --> view */
- (void)setupAsRegistered
{
    // Nothing to do.
}

- (void)showFairwareNagWithPrompt:(NSString *)prompt
{
    [HSFairwareReminder showFairwareNagWithApp:[self py] prompt:prompt];
}

- (void)showDemoNagWithPrompt:(NSString *)prompt
{
    [HSFairwareReminder showDemoNagWithApp:[self py] prompt:prompt];
}

- (void)showMessage:(NSString *)msg
{
    [Dialogs showMessage:msg];
}
@end
