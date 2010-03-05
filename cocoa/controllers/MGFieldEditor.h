/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "PyGUI.h"
#import "PyCompletableEdit.h"

@interface MGFieldEditor : NSTextView
{
    PyCompletableEdit *py;
    NSString *lastCompletion;
}
- (id)initWithPyParent:(id)aParent;
- (void)setAttrname:(NSString *)attrname;
/* Actions */
- (IBAction)lookupCompletion:(id)sender;
@end