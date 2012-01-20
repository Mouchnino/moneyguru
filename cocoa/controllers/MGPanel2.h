/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "MGDateFieldEditor.h"
#import "MGFieldEditor.h"
#import "PyPanel2.h"
#import "HSWindowController.h"

@interface MGPanel2 : NSWindowController {
    PyPanel2 *model;
    NSWindow *parentWindow;
    MGFieldEditor *customFieldEditor;
    MGDateFieldEditor *customDateFieldEditor;
}
- (id)initWithNibName:(NSString *)aNibName model:(PyPanel2 *)aModel parent:(HSWindowController *)aParent;
- (PyPanel2 *)model;
/* Virtual */
- (NSString *)completionAttrForField:(id)aField;
- (BOOL)isFieldDateField:(id)aField;
- (NSResponder *)firstField;
- (void)loadFields;
- (void)saveFields;
/* Public */
- (void)save;
/* Actions */
- (IBAction)cancel:(id)sender;
- (IBAction)save:(id)sender;
@end
