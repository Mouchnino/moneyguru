ownerclass = 'MGAccountSheetView'
ownerimport = 'MGAccountSheetView.h'

result = SplitView(None, 0, vertical=False)
subSplit = SplitView(result, 0, vertical=True)
outline = OutlineView(subSplit)
outline.OBJC_CLASS = 'HSOutlineView'
doubleView = View(subSplit, 329, 1)
doubleView.OBJC_CLASS = 'MGDoubleView'

owner.mainResponder = outline
owner.mainSplitView = result
owner.subSplitView = subSplit
owner.outlineView = outline
owner.pieChartsView = doubleView

result.dividerStyle = subSplit.dividerStyle = const.NSSplitViewDividerStyleThin
outline.allowsColumnReordering = True
outline.allowsColumnResizing = True
outline.allowsColumnSelection = False
outline.allowsEmptySelection = True
outline.allowsMultipleSelection = True
outline.allowsTypeSelect = True
outline.alternatingRows = False
outline.borderType = const.NSNoBorder
outline.focusRingType = const.NSFocusRingTypeNone
outline.bind('rowHeight', defaults, 'values.TableFontSize', valueTransformer='vtRowHeightOffset')

result.width = 760
result.height = 570
outline.width = 434

subSplit.fillAll(margin=0)
