#import "MGImportTableOneSided.h"
#import "Utils.h"
#import "MGConst.h"

@implementation MGImportTableOneSided
- (id)initWithImportWindow:(PyImportWindow *)aWindow
{
    self = [super initWithPyClassName:@"PyImportTable" pyParent:aWindow];
    [NSBundle loadNibNamed:@"ImportTableOneSided" owner:self];
    return self;
}

- (PyImportTable *)py
{
    return (PyImportTable *)py;
}
@end