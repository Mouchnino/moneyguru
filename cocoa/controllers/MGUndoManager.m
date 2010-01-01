/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGUndoManager.h"

@implementation MGUndoManager
- (id)initWithPy:(PyDocument *)aDocument
{
    self = [super init];
    document = [aDocument retain];
    return self;
}

- (void)dealloc
{
    [document release];
    [super dealloc];
}

- (BOOL)canUndo
{
    return [document canUndo];
}

- (NSString *)undoActionName
{
    return [document undoDescription];
}

- (void)undo
{
    [document undo];
}

- (BOOL)canRedo
{
    return [document canRedo];
}

- (NSString *)redoActionName
{
    return [document redoDescription];
}

- (void)redo
{
    [document redo];
}

@end