#import <Cocoa/Cocoa.h>

/* This is a hack to easily get around a cocoa limitation

In some weird circumstances, NSOutlineView calls [item indexPath] to the item instances given to
it. I guess is expects eveyone to give it NSTreeNode instances. Anyway, because in MG, simple
NSIndexPath are used, it causes problems. Not anymore.
*/

@interface NSIndexPath(NSIndexPathAdditions)
- (NSIndexPath *)indexPath;
@end