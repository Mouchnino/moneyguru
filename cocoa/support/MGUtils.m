#import "MGUtils.h"

@implementation MGUtils
+ (Class)classNamed:(NSString *)className
{
    NSString *pluginPath = [[NSBundle mainBundle] pathForResource:@"mg_cocoa" ofType:@"plugin"];
    NSBundle *pluginBundle = [NSBundle bundleWithPath:pluginPath];
    return [pluginBundle classNamed:className];
}
@end