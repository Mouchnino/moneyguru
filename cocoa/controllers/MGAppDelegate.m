/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGAppDelegate.h"
#import "MGPreferencesPanel_UI.h"
#import "MGDocument.h"
#import "HSPyUtil.h"
#import "Utils.h"
#import "HSFairwareReminder.h"
#import "Dialogs.h"
#import "ValueTransformers.h"
#import "MGDocumentController.h"

@implementation MGAppDelegate

@synthesize preferencesPanel;
@synthesize autoSaveIntervalField;
@synthesize autoDecimalPlaceButton;
@synthesize updater;
@synthesize customDateRangeItem1;
@synthesize customDateRangeItem2;
@synthesize customDateRangeItem3;

+ (void)initialize
{
    // Value Transformers
    HSVTAdd *vt = [[[HSVTAdd alloc] initWithValue:4] autorelease];
    [NSValueTransformer setValueTransformer:vt forName:@"vtRowHeightOffset"];
    // Register app-wide defaults
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    NSMutableDictionary *d = [NSMutableDictionary dictionary];
    // Others
    [d setObject:i2n(11) forKey:TableFontSize];
    [d setObject:i2n(11) forKey:PrintFontSize];
    
    [[NSUserDefaultsController sharedUserDefaultsController] setInitialValues:d];
    [ud registerDefaults:d];
}

- (id)init
{
    self = [super init];
    model = [[PyMoneyGuruApp alloc] init];
    [model bindCallback:createCallback(@"FairwareView", self)];
    self.updater = [SUUpdater sharedUpdater];
    self.updater.delegate = self;
    return self;
}

- (void)finalizeInit
{
    self.preferencesPanel = createMGPreferencesPanel_UI(self);
    if ([[NSUserDefaults standardUserDefaults] boolForKey:@"SUEnableAutomaticChecks"]) {
        [[SUUpdater sharedUpdater] checkForUpdatesInBackground];
    }
}

- (void)dealloc
{
    // NSLog(@"AppDelegate dealloc");
    [model release];
    [_aboutBox release];
    [super dealloc];
}

- (PyMoneyGuruApp *)model
{
    return model;
}

- (void)openExampleDocument
{
    // The goal here is to create a document that behaves as a new document (requires save as), but
    // has the content of the example file.
    NSBundle *bundle = [NSBundle bundleForClass:[self class]];
    NSString *filePath = [bundle pathForResource:@"example" ofType:@"moneyguru"];
    NSDocumentController *dc = [NSDocumentController sharedDocumentController];
    NSError *error;
    MGDocument *doc = [dc makeUntitledDocumentOfType:@"moneyGuru Document" error:&error];
    [doc readFromURL:[NSURL fileURLWithPath:filePath] ofType:@"moneyGuru Document" error:&error];
    [[doc model] adjustExampleFile];
    [dc addDocument:doc];
    [doc makeWindowControllers];
    [doc showWindows];
}

- (void)openWebsite
{
    [[NSWorkspace sharedWorkspace] openURL:[NSURL URLWithString:@"http://www.hardcoded.net/moneyguru/"]];
}

- (void)openHelp
{
    NSBundle *b = [NSBundle mainBundle];
    NSString *p = [b pathForResource:@"index" ofType:@"html" inDirectory:@"help"];
    NSURL *u = [NSURL fileURLWithPath:p];
    [[NSWorkspace sharedWorkspace] openURL:u];
}

- (void)showAboutBox
{
    if (_aboutBox == nil) {
        _aboutBox = [[HSAboutBox alloc] initWithApp:model];
    }
    [[_aboutBox window] makeKeyAndOrderFront:nil];
}

- (void)showPreferencesPanel
{
    [self.preferencesPanel makeKeyAndOrderFront:nil];
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
    [model initialRegistrationSetup];
    MGDocumentController *dc = [NSDocumentController sharedDocumentController];
    BOOL isFirstRun = [[self model] isFirstRun];
    if (isFirstRun) {
        NSString *msg = NSLocalizedString(@"This is your first time running moneyGuru. Do you want to open the example file?", @"");
        if ([Dialogs askYesNo:msg] == NSAlertFirstButtonReturn) {
            [self openExampleDocument];
        }
        else {
            NSError *error;
            [dc openUntitledDocumentAndDisplay:YES error:&error];
        }
    }
    else {
        [dc openFirstDocument];
    }
    // For some messed up reason, simply notifying of a 'model' change here crashes the app, so the 
    // binding cannot be done in the NIB, it has to be done manually here.
    [autoSaveIntervalField bind:@"value" toObject:self withKeyPath:@"model.autoSaveInterval" options:nil];
    [autoDecimalPlaceButton bind:@"value" toObject:self withKeyPath:@"model.autoDecimalPlace" options:nil];
}

- (void)applicationWillTerminate:(NSNotification *)aNotification
{
    [[self model] shutdown];
}

/* SUUpdater delegate */

- (BOOL)updater:(SUUpdater *)updater shouldPostponeRelaunchForUpdate:(SUAppcastItem *)update untilInvoking:(NSInvocation *)invocation;
{
    continueUpdate = [invocation retain];
    [[NSDocumentController sharedDocumentController] 
        reviewUnsavedDocumentsWithAlertTitle:NSLocalizedString(@"moneyGuru is about to restart", @"")
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
    [HSFairwareReminder showFairwareNagWithApp:[self model] prompt:prompt];
}

- (void)showDemoNagWithPrompt:(NSString *)prompt
{
    [HSFairwareReminder showDemoNagWithApp:[self model] prompt:prompt];
}

- (void)showMessage:(NSString *)msg
{
    [Dialogs showMessage:msg];
}
@end
