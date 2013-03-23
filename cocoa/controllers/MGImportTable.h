/* 
Copyright 2013 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import <Python.h>
#import "PyImportTable.h"
#import "PyImportWindow.h"
#import "MGEditableTable.h"
#import "MGTableView.h"

@interface MGImportTable : MGEditableTable {}
- (id)initWithPyRef:(PyObject *)aPyRef view:(MGTableView *)aTableView;
- (void)initializeColumns;
- (PyImportTable *)model;

- (void)updateOneOrTwoSided;
- (void)bindLockClick:(id)sender;
@end