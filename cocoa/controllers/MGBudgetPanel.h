/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "MGPanel2.h"
#import "HSPopUpList2.h"
#import "PyBudgetPanel.h"

@class MGMainWindowController;

@interface MGBudgetPanel : MGPanel2 {
    IBOutlet NSTextField *startDateField;
    IBOutlet NSTextField *repeatEveryField;
    IBOutlet NSTextField *repeatEveryDescLabel;
    IBOutlet NSPopUpButton *repeatTypePopUpView;
    IBOutlet NSTextField *stopDateField;
    IBOutlet NSPopUpButton *accountSelector;
    IBOutlet NSPopUpButton *targetSelector;
    IBOutlet NSTextField *amountField;
    IBOutlet NSTextField *notesField;
    
    HSPopUpList2 *repeatTypePopUp;
    HSPopUpList2 *accountPopUp;
    HSPopUpList2 *targetPopUp;
}
- (id)initWithParent:(MGMainWindowController *)aParent;
- (PyBudgetPanel *)model;
/* Python --> Cocoa */
- (void)refreshRepeatEvery;
@end
