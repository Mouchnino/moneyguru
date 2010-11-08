/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGDocumentController.h"
#import "MGDocument.h"

@implementation MGDocumentController
- (id)openDocumentWithContentsOfURL:(NSURL *)absoluteURL display:(BOOL)displayDocument error:(NSError **)outError
{
    /* What we want to do here is to add special handling for importable documents. In Info.plist,
       all importable documents are listed so that it's possible to import them by double-clicking.
       However, we don't want to create a new document, we want to take the current document and tell
       it to import the URL. In Info.plist, we added importable documents with a NSDocumentClass
       attribute that doesn't exist (MGImport), so the way to recognize them is to check if
       typeForContentsOfURL:error: is not nil, and then if documentClassForType: is nil.
    */
    NSString *urlType = [self typeForContentsOfURL:absoluteURL error:outError];
    if ((urlType != nil) && ([self documentClassForType:urlType] == nil)) {
        MGDocument *doc = (MGDocument *)[self currentDocument];
        if (doc == nil) {
            if ([[self documents] count] > 0) {
                doc = [[self documents] objectAtIndex:0];
            }
            else {
                doc = [self openFirstDocument];
            }
        }
        [[doc py] import:[absoluteURL path]];
        return doc;
    }
    return [super openDocumentWithContentsOfURL:absoluteURL display:displayDocument error:outError];
}

- (id)openFirstDocument
{
    /* Try opening the most recently opened document if possible, or open a new document.
    */
    if ([[self documents] count] > 0) {
        return [self currentDocument];
    }
    NSArray *recentURLs = [self recentDocumentURLs];
    if ([recentURLs count] > 0) {
        NSError *error;
        NSURL *url = [recentURLs objectAtIndex:0];
        return [self openDocumentWithContentsOfURL:url display:YES error:&error];
    }
    else {
        return [self openUntitledDocumentOfType:@"moneyGuru Document" display:YES];
    }
}
@end