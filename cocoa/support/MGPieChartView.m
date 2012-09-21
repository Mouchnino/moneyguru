/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGPieChartView.h"
#import "Utils.h"
#import "MGConst.h"
#import "HSGeometry.h"

// Synced with core
#define FontIDTitle 1
#define FontIDLegend 2
#define BrushIDLegend 10

//0xrrggbb
static NSInteger PIE_CHART_COLORS[] = {
    0x5dbc56,
    0x3c5bce,
    0xb6181f,
    0xe99709,
    0x9521e9,
    0x808080, //# Only for "Others"
    -1 // Sentinel
};

static NSColor* intToColor(NSInteger i)
{
    CGFloat r = ((i >> 16) & 255) / 255.0;
    CGFloat g = ((i >> 8) & 255) / 255.0;
    CGFloat b = (i & 255) / 255.0;
    return [NSColor colorWithDeviceRed:r green:g blue:b alpha:1.0];
}

@implementation MGPieChartView
- (NSDictionary *)fontAttributesForID:(NSInteger)aFontID
{
    NSMutableParagraphStyle *pstyle = [[[NSMutableParagraphStyle alloc] init] autorelease];
    [pstyle setAlignment:NSCenterTextAlignment];
    if (aFontID == FontIDTitle) {
        NSFont *titleFont = [NSFont boldSystemFontOfSize:15.0];
        return [NSDictionary dictionaryWithObjectsAndKeys:
            titleFont, NSFontAttributeName,
            [NSColor grayColor], NSForegroundColorAttributeName,
            pstyle, NSParagraphStyleAttributeName,
            nil];
    }
    else {
        NSColor *legendColor = [NSColor blackColor];
        NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
        NSFont *legendFont = [NSFont systemFontOfSize:[ud integerForKey:TableFontSize]];
        return [NSDictionary dictionaryWithObjectsAndKeys:
            legendFont, NSFontAttributeName,
            legendColor, NSForegroundColorAttributeName,
            pstyle, NSParagraphStyleAttributeName,
            nil];
    }
}

- (MGPen *)penForID:(NSInteger)aPenID
{
    return [MGPen penWithColor:intToColor(PIE_CHART_COLORS[aPenID]) width:1.0];
}

- (MGBrush *)brushForID:(NSInteger)aBrushID
{
    if (aBrushID == BrushIDLegend) {
        return [MGBrush brushWithColor:backgroundColor isGradient:NO];
    }
    else {
        return [MGBrush brushWithColor:intToColor(PIE_CHART_COLORS[aBrushID]) isGradient:YES];
    }
}

/* Drawing */
- (void)drawRect:(NSRect)rect 
{	
    [super drawRect:rect];
    [self.model draw];
}
@end
