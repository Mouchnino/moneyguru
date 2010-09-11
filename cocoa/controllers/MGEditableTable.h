/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "MGTableView.h"
#import "MGTable.h"
#import "MGFieldEditor.h"
#import "MGDateFieldEditor.h"

@interface MGEditableTable : MGTable
{
    MGFieldEditor *customFieldEditor;
    MGDateFieldEditor *customDateFieldEditor;
}
/* Virtual */
- (NSArray *)dateColumns;
- (NSArray *)completableColumns;
/* Public */
- (void)startEditing;
- (void)stopEditing;
- (NSString *)editedFieldname;
- (id)fieldEditorForObject:(id)asker;
@end
