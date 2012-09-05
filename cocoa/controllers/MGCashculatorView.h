/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "PyCashculatorView.h"
#import "MGBaseView.h"
#import "MGCashculatorAccountTable.h"

@interface MGCashculatorView : MGBaseView
{
    MGTableView *accountTableView;
    
    MGCashculatorAccountTable *accountTable;
}

@property (readwrite, retain) MGTableView *accountTableView;

- (id)initWithPyRef:(PyObject *)aPyRef;
- (PyCashculatorView *)model;
@end