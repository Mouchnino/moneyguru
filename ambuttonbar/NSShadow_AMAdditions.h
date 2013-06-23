//
//  NSShadow_AMAdditions.h
//  ButtonBarTest
//
//  Created by Andreas on 10.02.07.
//  Copyright 2007 Andreas Mayer. All rights reserved.
//  Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
//

#import <Cocoa/Cocoa.h>


@interface NSShadow (AMAdditions)
+ (NSShadow *)shadowWithColor:(NSColor *)color blurRadius:(CGFloat)radius offset:(NSSize)offset;
@end
