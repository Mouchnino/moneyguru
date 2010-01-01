/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>

@interface MGCSVLayoutNameDialog : NSWindowController
{
    IBOutlet NSTextField *nameTextField;
}
+ (NSString *)askForLayoutName;
+ (NSString *)askForLayoutNameBasedOnOldName:(NSString *)oldName;

- (IBAction)ok:(id)sender;
- (IBAction)cancel:(id)sender;

- (NSString *)layoutName;
- (void)setLayoutName:(NSString *)name;
@end