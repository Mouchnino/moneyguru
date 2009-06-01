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