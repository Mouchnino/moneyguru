#import "MGPrintView.h"
#import "MGUtils.h"
#import "MGConst.h"

@implementation MGPrintView
- (id)initWithPyParent:(id)pyParent
{
    self = [super initWithFrame:NSZeroRect];
    Class pyClass = [MGUtils classNamed:[[self class] pyClassName]];
    py = [[pyClass alloc] initWithPyParent:pyParent];
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    fontSize = [ud integerForKey:TableFontSize];
    headerFont = [[NSFont boldSystemFontOfSize:fontSize] retain];
    headerAttributes = [[NSDictionary dictionaryWithObjectsAndKeys:headerFont, NSFontAttributeName,
        [NSColor blackColor], NSForegroundColorAttributeName, nil] retain];
    
    return self;
}

- (void)dealloc
{
    [py release];
    [headerFont release];
    [headerAttributes release];
    [super dealloc];
}

+ (NSString *)pyClassName
{
    return @"PyPrintView";
}

- (PyPrintView *)py
{
    return py;
}

- (void)setUpWithPrintInfo:(NSPrintInfo *)pi
{
    NSRect pageBounds = [pi imageablePageBounds];
    [self setFrame:pageBounds];
    pageHeight = NSHeight(pageBounds);
    pageWidth = NSWidth(pageBounds);
    
    pageCount = 1;
    
    headerTextHeight = [@"foo" sizeWithAttributes:headerAttributes].height;
    headerHeight = headerTextHeight + 2;
}

- (NSString *)pageTitle
{
    return @"Title";
}

- (void)drawRect:(NSRect)rect
{
    [super drawRect:rect];
    int pageNumber = [[NSPrintOperation currentOperation] currentPage];
    float titleY = 0;
    NSString *title = [self pageTitle];
    title = [NSString stringWithFormat:@"%@ (Page %d of %d)",title,pageNumber,pageCount];
    float titleWidth = [title sizeWithAttributes:headerAttributes].width;
    float titleX = (pageWidth - titleWidth) / 2;
    
    [title drawAtPoint:NSMakePoint(titleX, titleY) withAttributes:headerAttributes];
}
@end