//
//  NSGradient_AMButtonBar.m
//  ButtonBarTest
//
//  Created by Andreas on 09.02.07.
//  Copyright 2007 Andreas Mayer. All rights reserved.
//  Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
//

#import "NSGradient_AMButtonBar.h"

@implementation NSGradient (AMButtonBar)
+ (NSGradient *)blueButtonBarGradient
{
    NSColor *color1 = [NSColor colorWithDeviceRed:0.65 green:0.65 blue:0.85 alpha:1.0];
    NSColor *color2 = [NSColor colorWithDeviceRed:0.75 green:0.75 blue:0.95 alpha:1.0];
    return [[[NSGradient alloc] initWithStartingColor:color1 endingColor:color2] autorelease];
}

+ (NSGradient *)grayButtonBarGradient;
{
    NSColor *color1 = [NSColor colorWithDeviceRed:0.75 green:0.75 blue:0.75 alpha:1.0];
    NSColor *color2 = [NSColor colorWithDeviceRed:0.95 green:0.95 blue:0.95 alpha:1.0];
    return [[[NSGradient alloc] initWithStartingColor:color1 endingColor:color2] autorelease];
}

+ (NSGradient *)lightButtonBarGradient
{
    NSColor *color1 = [NSColor colorWithDeviceRed:0.85 green:0.85 blue:0.85 alpha:1.0];
    NSColor *color2 = [NSColor colorWithDeviceRed:0.95 green:0.95 blue:0.95 alpha:1.0];
    return [[[NSGradient alloc] initWithStartingColor:color1 endingColor:color2] autorelease];
}
@end