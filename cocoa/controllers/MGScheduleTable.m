/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGScheduleTable.h"
#import "Utils.h"
#import "MGConst.h"
#import "MGFieldEditor.h"

@implementation MGScheduleTable

- (id)initWithDocument:(MGDocument *)aDocument
{
    self = [super initWithPyClassName:@"PyScheduleTable" pyParent:[aDocument py]];
    [NSBundle loadNibNamed:@"ScheduleTable" owner:self];
    customFieldEditor = [[MGFieldEditor alloc] init];
    return self;
}
        
- (void)dealloc
{
    [customFieldEditor release];
    [super dealloc];
}

/* Overrides */
- (PyScheduleTable *)py
{
    return (PyScheduleTable *)py;
}

/* Public */
- (id)fieldEditorForObject:(id)asker
{
    if (asker == tableView)
    {
        BOOL isDate = NO;
        int editedColumn = [tableView editedColumn];
        if (editedColumn > -1)
        {
            NSTableColumn *column = [[tableView tableColumns] objectAtIndex:editedColumn];
            NSString *name = [column identifier];
            isDate = [name isEqualTo:@"start_date"] || [name isEqualTo:@"end_date"];
        }
        [customFieldEditor setDateMode:isDate];
        return customFieldEditor;
    }
    return nil;
}

@end