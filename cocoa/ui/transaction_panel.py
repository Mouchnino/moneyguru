from common import FieldLabel, TitleLabel

ownerclass = 'MGTransactionInspector'
ownerimport = 'MGTransactionInspector.h'

result = Window(485, 352, "")
titleLabel = TitleLabel(result, "Transaction Info")
tabView = TabView(result)
infoTab = tabView.addTab("Info")
notesTab = tabView.addTab("Notes")

dateLabel = FieldLabel(infoTab.view, "Date")
dateField = TextField(infoTab.view, "")
descriptionLabel = FieldLabel(infoTab.view, "Description")
descriptionField = TextField(infoTab.view, "")
payeeLabel = FieldLabel(infoTab.view, "Payee")
payeeField = TextField(infoTab.view, "")
checknoLabel = FieldLabel(infoTab.view, "Check #")
checknoField = TextField(infoTab.view, "")
transfersLabel = FieldLabel(infoTab.view, "Transfers")
transfersTable = TableView(infoTab.view)
transfersTable.OBJC_CLASS = 'MGTableView'
mctButton = Button(infoTab.view, "Multi-Currency Balance", action=Action(owner, 'mctBalance'))
addTransferButton = Button(infoTab.view, "", action=Action(owner, 'addSplit'))
removeTransferButton = Button(infoTab.view, "", action=Action(owner, 'deleteSplit'))
navigateNoticeLabel = FieldLabel(infoTab.view, "You can navigate tabs with ⌘⌥→ and ⌘⌥←")

notesField = TextField(notesTab.view, "")
notesNoticeLabel = FieldLabel(notesTab.view, "Use ⌥+Return to insert a new line.")

cancelButton = Button(result, "Cancel", action=Action(owner, 'cancel:'))
saveButton = Button(result, "Save", action=Action(owner, 'save:'))

prevTabButton = Button(result, "", action=Action(tabView, 'selectPreviousTabViewItem:'))
nextTabButton = Button(result, "", action=Action(tabView, 'selectNextTabViewItem:'))

owner.checknoField = checknoField
owner.descriptionField = descriptionField
owner.notesField = notesField
owner.splitTableView = transfersTable
owner.dateField = dateField
owner.mctBalanceButton = mctButton
owner.tabView = tabView
result.delegate = owner

result.minSize = Size(result.width, result.height)
cancelButton.shortcut = 'esc'
saveButton.shortcut = 'return'
transfersTable.allowsColumnReordering = False
transfersTable.allowsColumnResizing = True
transfersTable.allowsColumnSelection = False
transfersTable.allowsEmptySelection = False
transfersTable.allowsMultipleSelection = False
transfersTable.allowsTypeSelect = False
transfersTable.alternatingRows = True
transfersTable.gridStyleMask = const.NSTableViewSolidVerticalGridLineMask | const.NSTableViewSolidHorizontalGridLineMask
mctButton.controlSize = ControlSize.Small
addTransferButton.bezelStyle = removeTransferButton.bezelStyle = const.NSSmallSquareBezelStyle
addTransferButton.image = 'NSAddTemplate'
removeTransferButton.image = 'NSRemoveTemplate'
navigateNoticeLabel.alignment = TextAlignment.Center
notesNoticeLabel.alignment = TextAlignment.Center
notesField.fixedHeight = False
# The button to select prev/next tab views are invisible, so we just send them far away
prevTabButton.x = nextTabButton.x = -1000
prevTabButton.shortcut = 'cmd+alt+arrowleft'
nextTabButton.shortcut = 'cmd+alt+arrowright'

fields = [dateField, descriptionField, payeeField, checknoField, notesField]
for field in fields:
    field.controlSize = ControlSize.Small

labels = [dateLabel, descriptionLabel, payeeLabel, checknoLabel, transfersLabel]
for label in labels:
    label.width = 80
for field in [dateField, checknoField]:
    field.width = 111
transfersTable.height = 76
mctButton.width = 160
addTransferButton.width = removeTransferButton.width = 25
addTransferButton.height = removeTransferButton.height = 21
cancelButton.width = saveButton.width = 84

mainLayout = VLayout([
    titleLabel,
    tabView,
    HLayout([None, cancelButton, saveButton]),
], filler=tabView)
mainLayout.moveTo(Pack.Left)
mainLayout.moveTo(Pack.Above, margin=11)
mainLayout.fill(Pack.LowerRight)
mainLayout.setAnchor(Pack.Left, growX=True)

infoLayout = VHLayout([
    [dateLabel, dateField],
    [descriptionLabel, descriptionField],
    [payeeLabel, payeeField],
    [checknoLabel, checknoField],
    [transfersLabel, transfersTable],
    [None, mctButton, addTransferButton, removeTransferButton],
    [navigateNoticeLabel],
    ],
    hfillers={descriptionField, payeeField, transfersTable, navigateNoticeLabel},
    vfiller=transfersTable, vmargin=6, valign=Pack.Middle)
# The transfer row is aligned above
infoLayout.subviews[-3].align = Pack.Above
infoLayout.moveTo(Pack.UpperLeft, margin=0)
infoLayout.fill(Pack.Right)
infoLayout.fill(Pack.Below, margin=6)
infoLayout.setAnchor(Pack.Left, growX=True)

notesField.moveTo(Pack.UpperLeft)
notesNoticeLabel.moveNextTo(notesField, Pack.Below)
notesField.fill(Pack.Right)
notesField.fill(Pack.Below, margin=6)
notesNoticeLabel.fill(Pack.Right)
notesField.setAnchor(Pack.UpperLeft, growX=True, growY=True)
notesNoticeLabel.setAnchor(Pack.LowerLeft, growX=True)
