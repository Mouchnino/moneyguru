//
//  NSFont_AMFixes.m
//  ButtonBarTest
//
//  Created by Andreas on 10.02.07.
//  Copyright 2007 Andreas Mayer. All rights reserved.
//  Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
//

#import "NSFont_AMFixes.h"


@implementation NSFont (AMFixes)

- (CGFloat)fixed_xHeight
{
	CGFloat result = [self xHeight];
	if ([[self familyName] isEqualToString:[[NSFont systemFontOfSize:[NSFont systemFontSize]] familyName]]) {
		switch (lrintf((int)[self pointSize])) {
			case 9: // mini
			{
				result = 5.655762;
				break;
			}
			case 11: // small
			{
				result = 6.912598;
				break;
			}
			case 13: // regular
			{
				result = 8.169434;
				break;
			}
		}
	}
	return result;
}

- (CGFloat)fixed_capHeight
{
	CGFloat result = [self capHeight];
	if (result == [self ascender]) { // instead of checking for appkit version
		if ([[self familyName] isEqualToString:[[NSFont systemFontOfSize:[NSFont systemFontSize]] familyName]]) { // we do have this info for the system font only 
			switch (lrintf((int)[self pointSize])) {
				case 9: // mini
				{
					result = 7.00;
					break;
				}
				case 11: // small
				{
					result = 8.00;
					break;
				}
				case 13: // regular
				{
					result = 9.50;
					break;
				}
			}
		}
	}
	return result;
}


@end
