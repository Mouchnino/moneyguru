from common import FieldLabel, TitleLabel

ownerclass = 'MGBudgetPanel'
ownerimport = 'MGBudgetPanel.h'

result = Window(342, 290, "")
titleLabel = TitleLabel(result, "Budget Info")
startDateLabel = FieldLabel(result, "Start Date")
startDateField = TextField(result, "")
repeatLabel = FieldLabel(result, "Repeat")
repeatPopup = Popup(result)
everyLabel = FieldLabel(result, "Every")
everyField = TextField(result, "")
everyDescLabel = Label(result, "")
stopDateLabel = FieldLabel(result, "Stop Date")
stopDateField = TextField(result, "")
accountLabel = FieldLabel(result, "Account")
accountPopup = Popup(result)
targetLabel = FieldLabel(result, "Target")
targetPopup = Popup(result)
amountLabel = FieldLabel(result, "Amount")
amountField = TextField(result, "")
notesLabel = FieldLabel(result, "Notes")
notesField = TextField(result, "")
cancelButton = Button(result, "Cancel", action=Action(owner, 'cancel:'))
saveButton = Button(result, "Save", action=Action(owner, 'save:'))

owner.accountSelector = accountPopup
owner.amountField = amountField
owner.notesField = notesField
owner.repeatEveryDescLabel = everyDescLabel
owner.repeatEveryField = everyField
owner.repeatTypePopUpView = repeatPopup
owner.startDateField = startDateField
owner.stopDateField = stopDateField
owner.targetSelector = targetPopup
startDateField.delegate = owner
everyField.delegate = owner
result.delegate = owner

result.canResize = False
cancelButton.keyEquivalent = '\\e'
saveButton.keyEquivalent = '\\r'
everyField.formatter = NumberFormatter(NumberStyle.Decimal)
everyField.formatter.maximumFractionDigits = 0

fields = [startDateField, repeatPopup, everyField, stopDateField, accountPopup, targetPopup,
    amountField, notesField]
for field in fields:
    field.controlSize = ControlSize.Small

labels = [startDateLabel, repeatLabel, everyLabel, everyDescLabel, stopDateLabel, accountLabel, 
    targetLabel, amountLabel, notesLabel]
for label in labels:
    label.width = 66
everyField.width = 50
everyDescLabel.width = 100
for field in [startDateField, stopDateField, amountField]:
    field.width = 111
notesField.height *= 2 # 2 lines
cancelButton.width = saveButton.width = 84

layout = VHLayout([
    [titleLabel],
    [startDateLabel, startDateField],
    [repeatLabel, repeatPopup],
    [everyLabel, everyField, everyDescLabel],
    [stopDateLabel, stopDateField],
    [accountLabel, accountPopup],
    [targetLabel, targetPopup],
    [amountLabel, amountField],
    [notesLabel, notesField],
    [None, cancelButton, saveButton],
], hfillers={repeatPopup, accountPopup, targetPopup, notesField}, vmargin=6, valign=Pack.Middle)
# We want to align the "Notes" label to the top instead of the middle
layout.subviews[-2].align = Pack.Above
layout.moveTo(Pack.UpperLeft, margin=11)
layout.fill(Pack.LowerRight)
