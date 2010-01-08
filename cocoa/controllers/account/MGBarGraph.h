/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "MGBarGraphView.h"
#import "MGDocument.h"
#import "MGGraph.h"
#import "PyBarGraph.h"


@interface MGBarGraph : MGGraph {}
- (id)initWithDocument:(MGDocument *)aDocument pyClassName:(NSString *)aClassName;
@end
