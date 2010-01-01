/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>

@interface MGFieldEditor : NSTextView {}
- (void)completeWith:(NSString *)proposition;
- (void)replaceWith:(NSString *)text;
@end

@interface NSObject(MGFieldEditorDelegate)
- (NSString *)fieldEditor:(MGFieldEditor *)fieldEditor wantsCompletionFor:(NSString *)text;
- (NSString *)fieldEditorWantsCurrentValue:(MGFieldEditor *)fieldEditor;
- (NSString *)fieldEditorWantsPrevValue:(MGFieldEditor *)fieldEditor;
- (NSString *)fieldEditorWantsNextValue:(MGFieldEditor *)fieldEditor;
@end
