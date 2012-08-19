ownerclass = 'MGExportPanel'
ownerimport = 'MGExportPanel.h'

result = Window(338, 458, "Export Options")
promptLabel = Label(result, "Which accounts do you want to export?")
scopeRadio = RadioButtons(result, ["All", "Selected"])
accountTable = TableView(result)
accountTable.OBJC_CLASS = 'MGTableView'
formatLabel = Label(result, "Export format:")
formatRadio = RadioButtons(result, ["QIF", "CSV"])
scopeLabel = Label(result, "Export scope:")
currentDateRangeOnlyCheckbox = Checkbox(result, "Current date range only")
cancelButton = Button(result, "Cancel", action=Action(owner, 'cancel:'))
exportButton = Button(result, "Export", action=Action(owner, 'export'))

owner.accountTableView = accountTable
owner.currentDateRangeOnlyButton = currentDateRangeOnlyCheckbox
owner.exportAllButtons = scopeRadio
owner.exportButton = exportButton
owner.exportFormatButtons = formatRadio

result.canMinimize = False
result.minSize = Size(result.width, result.height)
scopeRadio.action = Action(owner, 'exportAllToggled')
accountTable.allowsColumnReordering = False
accountTable.allowsColumnResizing = False
accountTable.allowsColumnSelection = False
accountTable.allowsEmptySelection = True
accountTable.allowsMultipleSelection = False
accountTable.allowsTypeSelect = False
exportButton.keyEquivalent = '\\r'
cancelButton.keyEquivalent = '\\e'

cancelButton.width = exportButton.width = 84

buttonLayout = HLayout([None, cancelButton, exportButton])
mainLayout = VLayout([promptLabel, scopeRadio, accountTable, formatLabel, formatRadio, scopeLabel,
    currentDateRangeOnlyCheckbox, buttonLayout], filler=accountTable)
mainLayout.moveTo(Pack.UpperLeft)
mainLayout.fill(Pack.LowerRight)
mainLayout.setAnchor(Pack.Left, growX=True)
