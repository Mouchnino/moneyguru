ownerclass = 'MGCSVImportOptions'
ownerimport = 'MGCSVImportOptions.h'

result = Window(574, 414, "CSV Import Options")
promptLabel = Label(result, "Specify which CSV columns correspond to which transaction fields. You "
    "must also uncheck the \"Import\" column for lines that don't represent a transaction "
    "(header, footer, comments).")
layoutLabel = Label(result, "Layout:")
layoutPopup = Popup(result, []) 
targetLabel = Label(result, "Target:")
targetPopup = Popup(result, ["New Account"])
rescanBox = Box(result, "Rescan")
encodingLabel = Label(rescanBox, "Encoding:")
encodingPopup = Popup(rescanBox, [])
delimiterLabel = Label(rescanBox, "Delimiter:")
delimiterField = TextField(rescanBox, "")
rescanButton = Button(rescanBox, "Rescan")
csvDataTable = TableView(result)
cancelButton = Button(result, "Cancel")
continueButton = Button(result, "Continue Import")
columnMenu = Menu("")

owner.columnMenu = columnMenu
owner.csvDataTable = csvDataTable
owner.delimiterTextField = delimiterField
owner.encodingSelector = encodingPopup
owner.layoutSelector = layoutPopup
owner.targetSelector = targetPopup
csvDataTable.dataSource = owner
csvDataTable.delegate = owner

layoutPopup.menu.addItem("Default")
layoutPopup.menu.addSeparator()
layoutPopup.menu.addItem("New Layout...", action=Action(owner, 'newLayout'))
layoutPopup.menu.addItem("Rename Selected Layout...", action=Action(owner, 'renameSelectedLayout'))
item = layoutPopup.menu.addItem("Delete Selected Layout", action=Action(owner, 'deleteSelectedLayout'))
item.bind('enabled', owner, 'canDeleteLayout')

csvColumnNames = ["Date", "Description", "Payee", "Check #", "Transfer", "Amount", "Increase",
    "Decrease", "Currency", "Transaction ID"]
columnAction = Action(owner, 'setColumnField:')
columnMenu.addItem("None", action=columnAction, tag=0)
columnMenu.addSeparator()
for index, title in enumerate(csvColumnNames, start=1):
    columnMenu.addItem(title, action=columnAction, tag=index)

importColumn = csvDataTable.addColumn('import', "Import", 42)
importColumn.dataCell = Checkbox(None, "")
importColumn.dataCell.controlSize = ControlSize.Small
importColumn.dataCell.action = Action(owner, 'toggleLineExclusion')

encodingLabel.alignment = delimiterLabel.alignment = TextAlignment.Right
rescanButton.bezelStyle = const.NSRoundRectBezelStyle
rescanButton.action = Action(owner, 'rescan')
cancelButton.action = Action(owner, 'cancel')
cancelButton.keyEquivalent = '\\e'
continueButton.action = Action(owner, 'continueImport')
continueButton.keyEquivalent = '\\r'
targetPopup.action = Action(owner, 'selectTarget')

promptLabel.height *= 3 # 3 lines
layoutLabel.width = targetLabel.width = 41
layoutPopup.width = targetPopup.width = 219
rescanBox.width = 227
rescanBox.height = 85
encodingLabel.width = delimiterLabel.width = 71
delimiterField.width = 25
cancelButton.width = 84
continueButton.width = 157

encodingLabel.moveTo(Pack.Left, margin=8)
encodingLabel.moveTo(Pack.Above)
encodingPopup.moveNextTo(encodingLabel, Pack.Right)
encodingPopup.fill(Pack.Right)
delimiterField.moveNextTo(encodingPopup, Pack.Below)
rescanButton.moveNextTo(delimiterField, Pack.Right)
rescanButton.fill(Pack.Right)
delimiterLabel.moveNextTo(delimiterField, Pack.Left)

promptLabel.moveTo(Pack.UpperLeft)
promptLabel.fill(Pack.Right)

popupsLayout = VHLayout([
    [layoutLabel, layoutPopup],
    [targetLabel, targetPopup],
])
popupsLayout.moveNextTo(promptLabel, Pack.Below)

# Once again, very tight screen estate, hence the margin
rescanBox.moveNextTo(promptLabel, Pack.Below, align=Pack.Right, margin=0)

csvDataTable.moveNextTo(rescanBox, Pack.Below)
csvDataTable.fill(Pack.Left)
csvDataTable.fill(Pack.Right)
continueButton.moveNextTo(csvDataTable, Pack.Below, align=Pack.Right)
csvDataTable.fill(Pack.Below)
cancelButton.moveNextTo(continueButton, Pack.Left)

csvDataTable.setAnchor(Pack.UpperLeft, growX=True, growY=True)
cancelButton.setAnchor(Pack.LowerRight)
continueButton.setAnchor(Pack.LowerRight)
