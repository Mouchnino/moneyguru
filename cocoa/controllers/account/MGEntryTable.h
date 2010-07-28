/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "PyEntryTable.h"
#import "MGEditableTable.h"
#import "MGFieldEditor.h"
#import "MGDateFieldEditor.h"

@interface MGEntryTable : MGEditableTable 
{   
    MGFieldEditor *customFieldEditor;
    MGDateFieldEditor *customDateFieldEditor;
}
- (id)initWithPyParent:(id)aPyParent view:(MGTableView *)aTableView;
- (void)initializeColumns;

/* Public */
- (PyEntryTable *)py;
- (id)fieldEditorForObject:(id)asker;
- (void)showTransferAccount:(id)sender;
@end
