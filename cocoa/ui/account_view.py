ownerclass = 'MGAccountView'
ownerimport = 'MGAccountView.h'

result = View(None, 670, 560)
filterBar = View(result, 600, 24)
filterBar.OBJC_CLASS = 'AMButtonBar'
reconciliationButton = Button(result, "Reconciliation", action=Action(owner, 'toggleReconciliationMode'))
split = SplitView(result, 0, vertical=False)
table = TableView(split)
table.OBJC_CLASS = 'MGTableView'

owner.mainResponder = table
owner.filterBarView = filterBar
owner.reconciliationModeButton = reconciliationButton
owner.splitView = split
owner.tableView = table

split.dividerStyle = const.NSSplitViewDividerStyleThin
reconciliationButton.controlSize = ControlSize.Small
reconciliationButton.buttonType = const.NSPushOnPushOffButton
table.allowsColumnReordering = True
table.allowsColumnResizing = True
table.allowsColumnSelection = False
table.allowsEmptySelection = True
table.allowsMultipleSelection = True
table.allowsTypeSelect = False
table.alternatingRows = True
table.gridStyleMask = const.NSTableViewSolidVerticalGridLineMask | const.NSTableViewSolidHorizontalGridLineMask
table.bind('rowHeight', defaults, 'values.TableFontSize', valueTransformer='vtRowHeightOffset')

reconciliationButton.width = 120
table.height = 300

filterBar.moveTo(Pack.UpperLeft, margin=0)
filterBar.fill(Pack.Right, margin=0)
reconciliationButton.moveTo(Pack.Above, margin=3)
reconciliationButton.moveTo(Pack.Right, margin=8)
split.moveNextTo(filterBar, Pack.Below, margin=0)
split.fill(Pack.LowerRight, margin=0)
table.fillAll(margin=0, setAnchor=True)
filterBar.setAnchor(Pack.UpperLeft, growX=True)
reconciliationButton.setAnchor(Pack.UpperRight)
split.setAnchor(Pack.UpperLeft, growX=True, growY=True)
