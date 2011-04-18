/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>

@interface PyReport : PyOutline {}
- (BOOL)canDeleteSelected;
- (BOOL)canMovePath:(NSArray *)sourcePath toPath:(NSArray *)destPath;
- (void)deleteSelected;
- (void)movePath:(NSArray *)sourcePath toPath:(NSArray *)destPath;
- (void)showSelectedAccount;
- (BOOL)canShowSelectedAccount;
- (void)toggleExcluded;
- (NSArray *)expandedPaths;
- (void)expandPath:(NSArray *)path;
- (void)collapsePath:(NSArray *)path;
@end
