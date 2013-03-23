/* 
Copyright 2013 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGPen.h"

@implementation MGPen
@synthesize color;
@synthesize width;

+ (id)penWithColor:(NSColor *)aColor width:(CGFloat)aWidth
{
    return [[[MGPen alloc] initWithColor:aColor width:aWidth] autorelease];
}

+ (id)nullPen
{
    return [MGPen penWithColor:nil width:0];
}

- (id)initWithColor:(NSColor *)aColor width:(CGFloat)aWidth
{
    self = [super init];
    self.color = aColor;
    self.width = aWidth;
    return self;
}

- (void)stroke:(NSBezierPath *)aPath
{
    if (self.color == nil) {
        return;
    }
    [aPath setLineWidth:self.width];
    [self.color setStroke];
    [aPath stroke];
}
@end
