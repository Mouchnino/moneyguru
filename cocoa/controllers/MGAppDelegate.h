#import <Cocoa/Cocoa.h>
#import "PyMoneyGuruApp.h"

@interface MGAppDelegate : NSObject
{
    IBOutlet NSMenuItem *unlockMenuItem;
    IBOutlet NSPopUpButton *firstWeekdayPopup;
    IBOutlet NSPopUpButton *aheadMonthsPopup;
    IBOutlet NSButton *dontUnreconcileButton;
    
    NSWindowController *viewOptionsWindow;
    PyMoneyGuruApp *py;
}

- (PyMoneyGuruApp *)py;

- (IBAction)openExampleDocument:(id)sender;
- (IBAction)openWebsite:(id)sender;
- (IBAction)toggleViewOptionsVisible:(id)sender;
- (IBAction)unlockApp:(id)sender;
@end
