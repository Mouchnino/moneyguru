/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "MGPanel.h"
#import "MGDocument.h"
#import "PyBudgetPanel.h"

@interface MGBudgetPanel : MGPanel {
    IBOutlet NSTextField *startDateField;
    IBOutlet NSTextField *repeatEveryField;
    IBOutlet NSTextField *repeatEveryDescLabel;
    IBOutlet NSPopUpButton *repeatOptionsPopUp;
    IBOutlet NSTextField *stopDateField;
    IBOutlet NSPopUpButton *accountSelector;
    IBOutlet NSPopUpButton *targetSelector;
    IBOutlet NSTextField *amountField;
    IBOutlet NSTextField *notesField;
}
- (id)initWithParent:(HSWindowController *)aParent;
- (PyBudgetPanel *)py;
/* Actions */
- (IBAction)repeatTypeSelected:(id)sender;
/* Python --> Cocoa */
- (void)refreshRepeatEvery;
- (void)refreshRepeatOptions;
@end
