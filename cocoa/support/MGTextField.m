/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGTextField.h"

@implementation MGTextField

- (NSString *)fieldEditor:(MGFieldEditor *)fieldEditor wantsCompletionFor:(NSString *)text
{
    return [[self delegate] autoCompletionForTextField:self partialWord:text];
}

- (NSString *)fieldEditorWantsCurrentValue:(MGFieldEditor *)fieldEditor
{
    return [[self delegate] currentValueForTextField:self];
}

- (NSString *)fieldEditorWantsNextValue:(MGFieldEditor *)fieldEditor
{
    return [[self delegate] nextValueForTextField:self];
}

- (NSString *)fieldEditorWantsPrevValue:(MGFieldEditor *)fieldEditor
{
    return [[self delegate] prevValueForTextField:self];
}

@end
