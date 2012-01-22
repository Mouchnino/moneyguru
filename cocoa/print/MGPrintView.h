/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "MGDocument.h"
#import "PyPrintView.h"

NSDictionary* changeAttributesAlignment(NSDictionary *attrs, NSTextAlignment align);

@interface MGPrintView : NSView
{
    PyPrintView *py;
    
    NSInteger pageCount;
    CGFloat pageWidth;
    CGFloat pageHeight;
    
    NSInteger fontSize;
    NSFont *headerFont;
    NSDictionary *headerAttributes;
    CGFloat baseHeaderTextHeight; // header text height for one line
    CGFloat headerTextHeight; // header text height
    CGFloat headerHeight;
    NSString *baseTitle;
}
- (id)initWithPyParent:(PyGUIObject2 *)pyParent;

+ (Class)pyClass;
- (PyPrintView *)py;

- (void)setUpWithPrintInfo:(NSPrintInfo *)pi;
@end