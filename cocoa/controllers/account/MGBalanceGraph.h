/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "MGDocument.h"
#import "MGGraph.h"
#import "MGLineGraphView.h"
#import "PyBalanceGraph.h"


@interface MGBalanceGraph : MGGraph {}
- (id)initWithDocument:(MGDocument *)aDocument pyClassName:(NSString *)aClassName;
@end
