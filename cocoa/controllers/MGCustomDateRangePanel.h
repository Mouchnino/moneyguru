/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "MGDocument.h"
#import "MGTextField.h"
#import "MGWindowController.h"
#import "PyCustomDateRangePanel.h"

@interface MGCustomDateRangePanel : MGWindowController {
    IBOutlet MGTextField *startDateField;
    IBOutlet MGTextField *endDateField;
    
    NSTextView *customDateFieldEditor;
}
- (id)initWithDocument:(MGDocument *)aDocument;
- (PyCustomDateRangePanel *)py;
/* Public */
- (void)load;
/* Actions */
- (IBAction)cancel:(id)sender;
- (IBAction)ok:(id)sender;
@end