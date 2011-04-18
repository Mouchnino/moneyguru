/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "PyMoneyGuruApp.h"
#import "HSAboutBox.h"

@interface MGAppDelegate : NSObject
{
    IBOutlet NSPopUpButton *firstWeekdayPopup;
    IBOutlet NSPopUpButton *aheadMonthsPopup;
    IBOutlet NSPopUpButton *yearStartMonthPopup;
    IBOutlet NSTextField *autoSaveIntervalField;
    IBOutlet NSButton *autoDecimalPlaceButton;
    IBOutlet NSMenuItem *customDateRangeItem1;
    IBOutlet NSMenuItem *customDateRangeItem2;
    IBOutlet NSMenuItem *customDateRangeItem3;
    
    NSInvocation *continueUpdate;
    PyMoneyGuruApp *py;
    HSAboutBox *_aboutBox;
}

- (PyMoneyGuruApp *)py;

- (IBAction)openExampleDocument:(id)sender;
- (IBAction)openWebsite:(id)sender;
- (IBAction)openHelp:(id)sender;
- (IBAction)showAboutBox:(id)sender;

- (void)setCustomDateRangeName:(NSString *)aName atSlot:(NSInteger)aSlot;
@end
