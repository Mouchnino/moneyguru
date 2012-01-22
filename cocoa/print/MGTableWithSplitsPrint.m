/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGTableWithSplitsPrint.h"

#define SPLIT_XOFFSET 50
#define SPLIT_XMARGIN 4
#define SPLIT_XPADDING 4
#define SPLIT_FIELD_COUNT 3

@implementation MGTableWithSplitsPrint
- (id)initWithPyParent:(PyGUIObject *)pyParent tableView:(NSTableView *)aTableView
{
    self = [super initWithPyParent:pyParent tableView:aTableView];
    
    splitFont = [[NSFont systemFontOfSize:fontSize-2] retain];
    splitAttributes = [[NSDictionary dictionaryWithObjectsAndKeys:splitFont, NSFontAttributeName,
        [NSColor blackColor], NSForegroundColorAttributeName, nil] retain];
    splitTextHeight = [@"foo" sizeWithAttributes:splitAttributes].height;
    splitHeight = splitTextHeight + 1;
    
    return self;
}

- (void)dealloc
{
    [splitFont release];
    [splitAttributes release];
    [super dealloc];
}

- (PySplitPrint *)py
{
    return (PySplitPrint *)py;
}

- (NSArray *)accountColumnNames
{
    return [NSArray array];
}

- (NSInteger)splitCountThreshold
{
    return 0;
}

- (id)objectValueForTableColumn:(NSTableColumn *)aColumn row:(NSInteger)aRow
{
    if ([[self accountColumnNames] containsObject:[aColumn identifier]])
    {
        NSInteger splitCount = [[self py] splitCountAtRow:aRow];
        if (splitCount >= [self splitCountThreshold])
            return @"--split--";
    }
    return [super objectValueForTableColumn:aColumn row:aRow];
}

- (CGFloat)heightForRow:(NSInteger)aRow
{
    NSInteger splitCount = [[self py] splitCountAtRow:aRow];
    if (splitCount >= [self splitCountThreshold])
        return (splitCount * splitHeight) + typicalRowHeight;
    else
        return typicalRowHeight;
}

- (void)drawRow:(NSInteger)aRow inRect:(NSRect)aRect
{
    [super drawRow:aRow inRect:aRect];
    NSInteger splitCount = [[self py] splitCountAtRow:aRow];
    if (splitCount < [self splitCountThreshold])
        return;
    NSMutableArray *rows = [NSMutableArray array];
    CGFloat maxwidths[SPLIT_FIELD_COUNT] = {0, 0, 0};
    for (NSInteger i=0; i<splitCount; i++)
    {
        NSArray *row = [[self py] splitValuesAtRow:aRow splitRow:i];
        for (NSInteger j=0; j<SPLIT_FIELD_COUNT; j++)
        {
            NSString *value = [row objectAtIndex:j];
            CGFloat width = [value sizeWithAttributes:splitAttributes].width + SPLIT_XPADDING;
            maxwidths[j] = MAX(maxwidths[j], width);
        }
        [rows addObject:row];
    }
    CGFloat sumwidth = maxwidths[0] + maxwidths[1] + maxwidths[2];
    CGFloat diff = NSWidth(aRect) - (sumwidth + SPLIT_XOFFSET);
    if (diff < 0) // we must reduce the memo column
        maxwidths[1] = maxwidths[1] + diff;
    NSCell *cell = [[NSCell alloc] initTextCell:@""];
    [cell setFont:splitFont];
    for (NSInteger i=0; i<splitCount; i++)
    {
        NSArray *row = [[self py] splitValuesAtRow:aRow splitRow:i];
        CGFloat splitY = NSMinY(aRect) + typicalRowHeight + (splitHeight * i);
        CGFloat splitX = NSMinX(aRect) + SPLIT_XOFFSET;
        for (NSInteger j=0; j<SPLIT_FIELD_COUNT; j++)
        {
            [cell setAlignment:j == 2 ? NSRightTextAlignment : NSLeftTextAlignment];
            CGFloat width = maxwidths[j];
            NSString *value = [row objectAtIndex:j];
            NSRect drawRect = NSMakeRect(splitX, splitY, width, splitHeight);
            [cell setStringValue:value];
            [cell drawInteriorWithFrame:drawRect inView:self];
            splitX += width + SPLIT_XMARGIN;
        }
    }
}
@end