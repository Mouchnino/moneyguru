/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGGradient.h"

typedef struct MGColor
{
    float red;
    float green;
    float blue;
    float alpha;
} MGColor;

static void MGLinearColorBlend(void *info, const float *input, float *output);

@implementation MGGradient

- (MGGradient *)initWithStartingColor:(NSColor *)color0 endingColor:(NSColor *)color1
{
    self = [super init];
    startingColor = [color0 retain];
    endingColor = [color1 retain];
    return self;
}

- (void)dealloc
{
    [startingColor release];
    [endingColor release];
    [super dealloc];
}

- (void)drawVerticallyInRect:(NSRect)rect
{
    // Convert the colors to a simple RGB representation
    MGColor colors[2];
    NSColor *color0 = [startingColor colorUsingColorSpaceName:NSDeviceRGBColorSpace];
    NSColor *color1 = [endingColor colorUsingColorSpaceName:NSDeviceRGBColorSpace];
    [color0 getRed:&colors[0].red green:&colors[0].green blue:&colors[0].blue alpha:&colors[0].alpha];
    [color1 getRed:&colors[1].red green:&colors[1].green blue:&colors[1].blue alpha:&colors[1].alpha];
    
    // Create the shading function
    static const float input_value_range[2] = { 0.0, 1.0 };
    static const float output_value_ranges[8] = { 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0 };
    static const CGFunctionCallbacks callbacks = { 0, MGLinearColorBlend, NULL };
    CGFunctionRef shadingFunction = CGFunctionCreate(colors, 1, input_value_range, 4, output_value_ranges, &callbacks);
    
    // Create the shading object
    CGPoint start = CGPointMake(0.0, NSMinY(rect));
    CGPoint end = CGPointMake(0.0, NSMaxY(rect));
    CGColorSpaceRef colorspace = CGColorSpaceCreateDeviceRGB();
    CGShadingRef shading = CGShadingCreateAxial(colorspace, start, end, shadingFunction, false, false);
    
    // Draw the shading
    [NSGraphicsContext saveGraphicsState];
    [NSBezierPath clipRect:rect];
    CGContextRef context = [[NSGraphicsContext currentContext] graphicsPort];
    CGContextDrawShading(context, shading);
    [NSGraphicsContext restoreGraphicsState];
    
    // Release the objects
    CGShadingRelease(shading);
    CGColorSpaceRelease(colorspace);
}

- (NSColor *)startingColor
{
    return startingColor;
}

- (NSColor *)endingColor
{
    return endingColor;
}
@end

static void MGLinearColorBlend(void *info, const float *input, float *output)
{
    MGColor *colors = (MGColor *)info;
    float value0 = 1.0 - *input;
    float value1 = *input;
    output[0] = value0 * colors[0].red + value1 * colors[1].red;
    output[1] = value0 * colors[0].green + value1 * colors[1].green;
    output[2] = value0 * colors[0].blue + value1 * colors[1].blue;
    output[3] = value0 * colors[0].alpha + value1 * colors[1].alpha;
}

