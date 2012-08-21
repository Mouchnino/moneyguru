from common import FieldLabel

ownerclass = 'MGCustomDateRangePanel'
ownerimport = 'MGCustomDateRangePanel.h'

result = Window(362, 202, "Custom date range")
promptLabel = Label(result, "Select start and end dates for your custom range:")
startLabel = FieldLabel(result, "Start")
startField = TextField(result, "")
endLabel = FieldLabel(result, "End")
endField = TextField(result, "")
slotLabel = Label(result, "Save this custom range in slot:")
slotPopup = Popup(result, ["None", NLSTR("#1"), NLSTR("#2"), NLSTR("#3")])
slotNameLabel = Label(result, "Under the name:")
slotNameField = TextField(result, "")
okButton = Button(result, "OK")
cancelButton = Button(result, "Cancel")

owner.endDateField = endField
owner.slotIndexSelector = slotPopup
owner.slotNameField = slotNameField
owner.startDateField = startField
result.delegate = owner
startField.delegate = owner
endField.delegate = owner


result.canResize = result.canMinimize = False
for field in [startField, endField]:
    field.controlSize = ControlSize.Small
slotNameField.controlSize = ControlSize.Small

cancelButton.keyEquivalent = '\\e'
okButton.keyEquivalent = '\\r'
cancelButton.action = Action(owner, 'cancel:')
okButton.action = Action(owner, 'save:')

startLabel.width = endLabel.width = 50
startField.width = endField.width = 120
slotPopup.width = 95
slotNameLabel.width = 115
cancelButton.width = okButton.width = 84

promptLabel.moveTo(Pack.UpperLeft)
promptLabel.fill(Pack.Right)
fieldsLayout = VHLayout([
    [startLabel, startField],
    [endLabel, endField],
])
fieldsLayout.moveNextTo(promptLabel, Pack.Below)
# To leave enough space for localization, we cheat a bit on layouts and make the right aligned
# labels go beyound standard margins.
fieldsLayout.moveTo(Pack.Left, target=6)
slotLabel.moveNextTo(fieldsLayout, Pack.Below)
slotPopup.moveNextTo(slotLabel, Pack.Right)
slotLabel.fill(Pack.Left)
slotLabel.fill(Pack.Right)
# The margin between a push button (including popups) and a text field is 20. It's too big for us.
slotNameField.moveNextTo(slotPopup, Pack.Below, margin=5)
slotNameLabel.moveNextTo(slotNameField, Pack.Left)
slotNameField.fill(Pack.Left)
slotNameField.fill(Pack.Right)
okButton.moveNextTo(slotNameField, Pack.Below, align=Pack.Right)
cancelButton.moveNextTo(okButton, Pack.Left)
