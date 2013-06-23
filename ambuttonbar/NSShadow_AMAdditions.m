//
//  NSShadow_AMAdditions.m
//  ButtonBarTest
//
//  Created by Andreas on 10.02.07.
//  Copyright 2007 Andreas Mayer. All rights reserved.
//  Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
//

#import "NSShadow_AMAdditions.h"

@implementation NSShadow (AMAdditions)
+ (NSShadow *)shadowWithColor:(NSColor *)color blurRadius:(CGFloat)radius offset:(NSSize)offset
{
	NSShadow *result = [[[NSShadow alloc] init] autorelease];
	[result setShadowOffset:offset];
	[result setShadowBlurRadius:radius];
	[result setShadowColor:color];
	return result;
}
@end
