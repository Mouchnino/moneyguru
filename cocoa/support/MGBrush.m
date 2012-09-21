/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGBrush.h"

@implementation MGBrush
@synthesize color;
@synthesize gradient;

+ (id)brushWithColor:(NSColor *)aColor isGradient:(BOOL)aIsGradient
{
    return [[[MGBrush alloc] initWithColor:aColor isGradient:aIsGradient] autorelease];
}

- (id)initWithColor:(NSColor *)aColor isGradient:(BOOL)aIsGradient
{
    self = [super init];
    self.color = aColor;
    if (aIsGradient) {
        NSColor *light = [aColor blendedColorWithFraction:0.5 ofColor:[NSColor whiteColor]];
        self.gradient = [[[NSGradient alloc] initWithStartingColor:aColor endingColor:light] autorelease];
    }
    else {
        self.gradient = nil;
    }
    return self;
}
@end
