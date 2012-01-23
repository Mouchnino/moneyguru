/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "HSTextField.h"

@interface MGSearchField : HSTextField {}
- (id)initWithPyRef:(PyObject *)aPyRef;
- (NSSearchField *)view;
- (void)setView:(NSSearchField *)aView;
- (IBAction)changeQuery:(id)sender;
@end