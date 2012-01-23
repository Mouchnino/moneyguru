/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "MGPanel.h"
#import "PyMassEditionPanel.h"
#import "HSTextField.h"
#import "HSComboBox.h"

@class MGMainWindowController;

@interface MGMassEditionPanel : MGPanel {
    IBOutlet NSTextField *dateFieldView;
    IBOutlet NSTextField *descriptionFieldView;
    IBOutlet NSTextField *payeeFieldView;
    IBOutlet NSTextField *checknoFieldView;
    IBOutlet NSTextField *fromFieldView;
    IBOutlet NSTextField *toFieldView;
    IBOutlet NSTextField *amountFieldView;
    IBOutlet NSComboBox *currencyComboBoxView;
    IBOutlet NSButton *dateCheckBox;
    IBOutlet NSButton *descriptionCheckBox;
    IBOutlet NSButton *payeeCheckBox;
    IBOutlet NSButton *checknoCheckBox;
    IBOutlet NSButton *fromCheckBox;
    IBOutlet NSButton *toCheckBox;
    IBOutlet NSButton *amountCheckBox;
    IBOutlet NSButton *currencyCheckBox;
    
    HSTextField *dateField;
    HSTextField *descriptionField;
    HSTextField *payeeField;
    HSTextField *checknoField;
    HSTextField *fromField;
    HSTextField *toField;
    HSTextField *amountField;
    HSComboBox *currencyComboBox;
}
- (id)initWithParent:(MGMainWindowController *)aParent;
- (PyMassEditionPanel *)model;
@end
