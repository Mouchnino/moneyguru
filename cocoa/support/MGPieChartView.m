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

#define FontIDTitle 1
#define FontIDLegend 2
#define ColorIndexLegendBackground 7

@implementation MGPieChartView
- (id)init
{
    self = [super init];
    colors = nil;
    return self;
}

- (void)dealloc
{
    [colors release];
    [super dealloc];
}

- (id)copyWithZone:(NSZone *)zone
{
    MGPieChartView *result = [super copyWithZone:zone];
    [result setColors:colors];
    return result;
}

- (void)setColors:(NSArray *)aColors
{
    [colors release];
    colors = [aColors retain];
}

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

- (NSColor *)colorForIndex:(NSInteger)aColorIndex
{
    if (aColorIndex == ColorIndexLegendBackground) {
        return backgroundColor;
    }
    else {
        return [colors objectAtIndex:aColorIndex];
    }
}

/* Drawing */
- (void)drawRect:(NSRect)rect 
{	
    [super drawRect:rect];
    [self.model draw];
}
@end
