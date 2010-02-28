/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "MGDocument.h"
#import "HSWindowController.h"
#import "MGDateFieldEditor.h"
#import "MGFieldEditor.h"
#import "PyPanel.h"

@interface MGPanel : HSWindowController {
    NSWindow *parentWindow;
    MGFieldEditor *customFieldEditor;
    MGDateFieldEditor *customDateFieldEditor;
}
- (id)initWithNibName:aNibName pyClassName:aClassName document:aDocument;
- (PyPanel *)py;
/* Virtual */
- (NSString *)fieldOfTextField:(NSTextField *)textField;
- (BOOL)isFieldDateField:(NSTextField *)textField;
- (NSResponder *)firstField;
- (void)loadFields;
- (void)saveFields;
/* Public */
- (void)save;
/* Actions */
- (IBAction)cancel:(id)sender;
- (IBAction)save:(id)sender;
@end
