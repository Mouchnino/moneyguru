#import <Cocoa/Cocoa.h>
#import "MGDocument.h"
#import "PyPrintView.h"

@interface MGPrintView : NSView
{
    PyPrintView *py;
    
    int pageCount;
    float pageWidth;
    float pageHeight;
    
    int fontSize;
    NSFont *headerFont;
    NSDictionary *headerAttributes;
    float headerTextHeight;
    float headerHeight;
}
- (id)initWithPyParent:(id)pyParent;

+ (NSString *)pyClassName;
- (PyPrintView *)py;

- (void)setUpWithPrintInfo:(NSPrintInfo *)pi;
- (NSString *)pageTitle;
@end