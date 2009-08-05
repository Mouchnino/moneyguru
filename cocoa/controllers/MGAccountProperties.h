/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "MGDocument.h"
#import "MGWindowController.h"
#import "PyAccountPanel.h"

@interface MGAccountProperties : MGWindowController {
    IBOutlet NSTextField *nameTextField;
    IBOutlet NSPopUpButton *typeSelector;
    IBOutlet NSComboBox *currencySelector;
    IBOutlet NSPopUpButton *budgetTargetSelector;
    
    NSArray *currencies;
}
- (id)initWithDocument:(MGDocument *)aDocument;
- (PyAccountPanel *)py;
/* Methods */
- (BOOL)canLoad;
- (void)load;
- (void)save;
/* Actions */
- (IBAction)cancel:(id)sender;
- (IBAction)save:(id)sender;
/* Properties */
- (int)typeIndex;
- (void)setTypeIndex:(int)typeIndex;
@end