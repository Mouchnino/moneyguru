/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
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
    [super dealloc];
}

- (id)copyWithZone:(NSZone *)zone
{
    MGChartView *result = [[[self class] alloc] init];
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
@end