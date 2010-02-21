/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGSplitTable.h"

@implementation MGSplitTable
- (id)initWithTransactionPanel:(PyPanel *)aPanel view:(MGTableView *)aTableView
{
    self = [super initWithPyClassName:@"PySplitTable" pyParent:aPanel view:aTableView];
    return self;
}

- (PySplitTable *)py
{
    return (PySplitTable *)py;
}

- (void)tableView:(NSTableView *)aTableView willDisplayCell:(id)aCell forTableColumn:(NSTableColumn *)column row:(NSInteger)row
{
    if ([aCell isKindOfClass:[NSTextFieldCell class]]) {
        BOOL isMain = [[self py] isRowMainAtIndex:row];
        NSTextFieldCell *cell = aCell;
        NSFont *font = [cell font];
        NSFontManager *fontManager = [NSFontManager sharedFontManager];
        if (isMain) {
            font = [fontManager convertFont:font toHaveTrait:NSFontBoldTrait];
        }
        else {
            font = [fontManager convertFont:font toNotHaveTrait:NSFontBoldTrait];
        }
        [cell setFont:font];
    }
}
@end