ownerclass = 'MGTransactionView'
ownerimport = 'MGTransactionView.h'

result = View(None, 600, 300)
filterBar = View(result, 600, 24)
filterBar.OBJC_CLASS = 'AMButtonBar'
table = TableView(result)
table.OBJC_CLASS = 'MGTableView'

owner.mainResponder = table
owner.filterBarView = filterBar
owner.tableView = table

table.allowsColumnReordering = True
table.allowsColumnResizing = True
table.allowsColumnSelection = False
table.allowsEmptySelection = True
table.allowsMultipleSelection = True
table.allowsTypeSelect = False
table.alternatingRows = True
table.gridStyleMask = const.NSTableViewSolidVerticalGridLineMask | const.NSTableViewSolidHorizontalGridLineMask
table.bind('rowHeight', defaults, 'values.TableFontSize', valueTransformer='vtRowHeightOffset')

filterBar.moveTo(Pack.UpperLeft, margin=0)
filterBar.fill(Pack.Right, margin=0)
table.moveNextTo(filterBar, Pack.Below, margin=0)
table.fill(Pack.LowerRight, margin=0)
filterBar.setAnchor(Pack.UpperLeft, growX=True)
table.setAnchor(Pack.UpperLeft, growX=True, growY=True)
