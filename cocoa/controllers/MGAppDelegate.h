/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import <Sparkle/SUUpdater.h>
#import "PyMoneyGuruApp.h"
#import "HSAboutBox.h"
#import "MGConst.h" // to have MG consts in the main_menu UI script.

@interface MGAppDelegate : NSObject
{
    NSWindow *preferencesPanel;
    NSTextField *autoSaveIntervalField;
    NSButton *autoDecimalPlaceButton;
    SUUpdater *updater;
    NSMenuItem *customDateRangeItem1;
    NSMenuItem *customDateRangeItem2;
    NSMenuItem *customDateRangeItem3;
    
    NSInvocation *continueUpdate;
    PyMoneyGuruApp *model;
    HSAboutBox *_aboutBox;
}

@property (readwrite, retain) NSWindow *preferencesPanel;
@property (readwrite, retain) NSTextField *autoSaveIntervalField;
@property (readwrite, retain) NSButton *autoDecimalPlaceButton;
@property (readwrite, retain) SUUpdater *updater;
@property (readwrite, retain) NSMenuItem *customDateRangeItem1;
@property (readwrite, retain) NSMenuItem *customDateRangeItem2;
@property (readwrite, retain) NSMenuItem *customDateRangeItem3;

- (PyMoneyGuruApp *)model;
- (void)finalizeInit;

- (void)openExampleDocument;
- (void)openWebsite;
- (void)openHelp;
- (void)showAboutBox;
- (void)showPreferencesPanel;

- (void)setCustomDateRangeName:(NSString *)aName atSlot:(NSInteger)aSlot;

/* model --> view */
- (void)setupAsRegistered;
- (void)showFairwareNagWithPrompt:(NSString *)prompt;
- (void)showDemoNagWithPrompt:(NSString *)prompt;
- (void)showMessage:(NSString *)msg;
@end
