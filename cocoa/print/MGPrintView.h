/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "MGDocument.h"
#import "PyPrintView.h"

@interface MGPrintView : NSView
{
    PyPrintView *py;
    
    NSInteger pageCount;
    CGFloat pageWidth;
    CGFloat pageHeight;
    
    NSInteger fontSize;
    NSFont *headerFont;
    NSDictionary *headerAttributes;
    CGFloat headerTextHeight;
    CGFloat headerHeight;
}
- (id)initWithPyParent:(id)pyParent;

+ (NSString *)pyClassName;
- (PyPrintView *)py;

- (void)setUpWithPrintInfo:(NSPrintInfo *)pi;
- (NSString *)pageTitle;
@end