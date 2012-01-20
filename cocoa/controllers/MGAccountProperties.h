/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "MGPanel2.h"
#import "HSPopUpList2.h"
#import "HSComboBox2.h"
#import "PyAccountPanel.h"

@class MGMainWindowController;

@interface MGAccountProperties : MGPanel2 {
    IBOutlet NSTextField *nameTextField;
    IBOutlet NSPopUpButton *typeSelector;
    IBOutlet NSComboBox *currencySelector;
    IBOutlet NSTextField *accountNumberTextField;
    IBOutlet NSTextField *notesTextField;
    
    HSPopUpList2 *typePopUp;
    HSComboBox2 *currencyComboBox;
}
- (id)initWithParent:(MGMainWindowController *)aParent;
- (PyAccountPanel *)model;
@end