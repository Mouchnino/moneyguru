/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "MGDocument.h"
#import "MGTextField.h"
#import "MGWindowController.h"
#import "PyMassEditionPanel.h"

@interface MGMassEditionPanel : MGWindowController {
    IBOutlet NSTextField *dateField;
    IBOutlet MGTextField *descriptionField;
    IBOutlet MGTextField *payeeField;
    IBOutlet NSTextField *checknoField;
    IBOutlet MGTextField *fromField;
    IBOutlet MGTextField *toField;
    IBOutlet NSComboBox *currencySelector;
    
    NSArray *currencies;
    NSTextView *customFieldEditor;
    NSTextView *customDateFieldEditor;
}
- (id)initWithDocument:(MGDocument *)aDocument;
- (PyMassEditionPanel *)py;

/* Methods */
- (BOOL)canLoad;
- (void)load;
- (void)save;
- (void)refresh;

/* Actions */
- (IBAction)cancel:(id)sender;
- (IBAction)save:(id)sender;

@end
