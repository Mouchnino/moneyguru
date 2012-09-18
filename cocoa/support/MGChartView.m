/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGChartView.h"

@implementation MGChartView
- (id)init
{
    self = [super init];
    backgroundColor = [[NSColor whiteColor] retain];
    titleColor = [[NSColor grayColor] retain];
    return self;
}

- (void)dealloc
{
    [backgroundColor release];
    [titleColor release];
    [data release];
    [title release];
    [currency release];
    [model release];
    [super dealloc];
}

- (id)copyWithZone:(NSZone *)zone
{
    MGChartView *result = [[[self class] alloc] init];
    [result setModel:model];
    [result setData:data];
    [result setTitle:title];
    [result setCurrency:currency];
    return result;
}

- (void)drawRect:(NSRect)rect
{
    [backgroundColor setFill];
	[NSBezierPath fillRect:rect];
}

- (BOOL)isOpaque
{
	return YES;
}

- (void)setFrameSize:(NSSize)newSize
{
    [super setFrameSize:newSize];
    [[self model] setViewWidth:newSize.width height:newSize.height];
}

- (PyChart *)model
{
    return model;
}

- (void)setModel:(PyChart *)aModel
{
    [model release];
    model = [aModel retain];
}

- (void)setData:(NSArray *)aData
{
    [data autorelease];
    data = [aData retain];
}

- (void)setTitle:(NSString *)aTitle
{
    [title autorelease];
    title = [aTitle retain];
}

- (void)setCurrency:(NSString *)aCurrency
{
    [currency autorelease];
    currency = [aCurrency retain];
}

- (void)drawText:(NSString *)aText inRect:(NSRect)aRect withAttributes:(NSDictionary *)aAttrs
{
    [NSGraphicsContext saveGraphicsState];
    [aText drawInRect:aRect withAttributes:aAttrs];
    [NSGraphicsContext restoreGraphicsState];
}
@end