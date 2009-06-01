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
