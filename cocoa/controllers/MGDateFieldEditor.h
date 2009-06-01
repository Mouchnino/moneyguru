#import <Cocoa/Cocoa.h>
#import "PyDateWidget.h"

@interface MGDateFieldEditor : NSTextView 
{
    PyDateWidget *py;
}
- (id)init;

- (void)refresh;
@end