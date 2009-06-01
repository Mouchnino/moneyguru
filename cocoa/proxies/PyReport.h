#import <Cocoa/Cocoa.h>

@interface PyReport : PyOutline {}
- (void)addAccount;
- (void)addAccountGroup;
- (BOOL)canDeleteSelected;
- (BOOL)canMovePath:(NSArray *)sourcePath toPath:(NSArray *)destPath;
- (void)deleteSelected;
- (void)movePath:(NSArray *)sourcePath toPath:(NSArray *)destPath;
- (void)showSelectedAccount;
- (BOOL)canShowSelectedAccount;
- (void)toggleExcluded;
- (void)expandPath:(NSArray *)path;
- (void)collapsePath:(NSArray *)path;
@end
