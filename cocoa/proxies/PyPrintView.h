/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>

// We don't subclass the PyGUI class because we don't need the whole connect/disconnect/callback
// mechanism of the normal GUI objects (it's a one shot object)
@interface PyPrintView : NSObject {}
- (id)initWithPyParent:(id)pyParent;

- (NSString *)startDate;
- (NSString *)endDate;
@end