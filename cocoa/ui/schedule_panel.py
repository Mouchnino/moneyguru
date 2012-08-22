from common import FieldLabel, PANEL_TITLE_FONT

ownerclass = 'MGSchedulePanel'
ownerimport = 'MGSchedulePanel.h'

result = Window(514, 426, "")
titleLabel = Label(result, "Schedule Info")
tabView = TabView(result)
infoTab = tabView.addTab("Info")
notesTab = tabView.addTab("Notes")

startDateLabel = FieldLabel(infoTab.view, "Start Date")
startDateField = TextField(infoTab.view, "")
repeatLabel = FieldLabel(infoTab.view, "Repeat")
repeatPopup = Popup(infoTab.view)
everyLabel = FieldLabel(infoTab.view, "Every")
everyField = TextField(infoTab.view, "")
everyDescLabel = Label(infoTab.view, "")
stopDateLabel = FieldLabel(infoTab.view, "Stop Date")
stopDateField = TextField(infoTab.view, "")
descriptionLabel = FieldLabel(infoTab.view, "Description")
descriptionField = TextField(infoTab.view, "")
payeeLabel = FieldLabel(infoTab.view, "Payee")
payeeField = TextField(infoTab.view, "")
checknoLabel = FieldLabel(infoTab.view, "Check #")
checknoField = TextField(infoTab.view, "")
transfersLabel = FieldLabel(infoTab.view, "Transfers")
transfersTable = TableView(infoTab.view)
transfersTable.OBJC_CLASS = 'MGTableView'
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
owner.repeatEveryDescLabel = everyDescLabel
owner.repeatEveryField = everyField
owner.repeatTypePopUpView = repeatPopup
owner.splitTableView = transfersTable
owner.startDateField = startDateField
owner.stopDateField = stopDateField
owner.tabView = tabView
startDateField.delegate = owner
everyField.delegate = owner
result.delegate = owner

result.minSize = Size(result.width, result.height)
cancelButton.shortcut = 'esc'
saveButton.shortcut = 'return'
titleLabel.font = PANEL_TITLE_FONT
titleLabel.alignment = TextAlignment.Center
everyField.formatter = NumberFormatter(NumberStyle.Decimal)
everyField.formatter.maximumFractionDigits = 0
transfersTable.allowsColumnReordering = False
transfersTable.allowsColumnResizing = True
transfersTable.allowsColumnSelection = False
transfersTable.allowsEmptySelection = False
transfersTable.allowsMultipleSelection = False
transfersTable.allowsTypeSelect = False
transfersTable.alternatingRows = True
transfersTable.gridStyleMask = const.NSTableViewSolidVerticalGridLineMask | const.NSTableViewSolidHorizontalGridLineMask
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

fields = [startDateField, repeatPopup, everyField, stopDateField, descriptionField, payeeField,
    checknoField, notesField]
for field in fields:
    field.controlSize = ControlSize.Small

titleLabel.height = 22
labels = [startDateLabel, repeatLabel, everyLabel, everyDescLabel, stopDateLabel, descriptionLabel, 
    payeeLabel, checknoLabel, transfersLabel]
for label in labels:
    label.width = 80
everyField.width = 50
everyDescLabel.width = 100
for field in [startDateField, stopDateField]:
    field.width = 111
repeatPopup.width = 222
transfersTable.height = 76
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
    [startDateLabel, startDateField],
    [repeatLabel, repeatPopup],
    [everyLabel, everyField, everyDescLabel],
    [stopDateLabel, stopDateField],
    [descriptionLabel, descriptionField],
    [payeeLabel, payeeField],
    [checknoLabel, checknoField],
    [transfersLabel, transfersTable],
    [None, addTransferButton, removeTransferButton],
    [navigateNoticeLabel],
], fillers={descriptionField, payeeField, transfersTable, navigateNoticeLabel}, vmargin=6, valign=Pack.Middle)
# The transfer row is aligned above
infoLayout.subviews[-3].align = Pack.Above
infoLayout.moveTo(Pack.UpperLeft, margin=0)
infoLayout.fill(Pack.LowerRight)
infoLayout.setAnchor(Pack.Left, growX=True)
transfersTable.setAnchor(Pack.UpperLeft, growX=True, growY=True)
addTransferButton.setAnchor(Pack.LowerRight)
removeTransferButton.setAnchor(Pack.LowerRight)
navigateNoticeLabel.setAnchor(Pack.LowerLeft, growX=True)

notesField.moveTo(Pack.UpperLeft)
notesNoticeLabel.moveNextTo(notesField, Pack.Below)
notesField.fill(Pack.Right)
notesField.fill(Pack.Below, margin=6)
notesNoticeLabel.fill(Pack.Right)
notesField.setAnchor(Pack.UpperLeft, growX=True, growY=True)
notesNoticeLabel.setAnchor(Pack.LowerLeft, growX=True)
