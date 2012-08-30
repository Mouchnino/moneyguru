from common import FieldLabel, TitleLabel

ownerclass = 'MGAccountProperties'
ownerimport = 'MGAccountProperties.h'

result = Window(300, 255, "")
titleLabel = TitleLabel(result, "Account Info")
nameLabel = FieldLabel(result, "Name")
nameField = TextField(result)
typeLabel = FieldLabel(result, "Type")
typePopup = Popup(result)
currencyLabel = FieldLabel(result, "Currency")
currencyCombo = Combobox(result)
accountnoLabel = FieldLabel(result, "Account #")
accountnoField = TextField(result)
notesLabel = FieldLabel(result, "Notes")
notesField = TextField(result)
cancelButton = Button(result, "Cancel", action=Action(owner, 'cancel:'))
saveButton = Button(result, "Save", action=Action(owner, 'save:'))

owner.accountNumberTextField = accountnoField
owner.currencySelector = currencyCombo
owner.nameTextField = nameField
owner.notesTextField = notesField
owner.typeSelector = typePopup
result.delegate = owner

result.minSize = Size(result.width, result.height)
cancelButton.shortcut = 'esc'
saveButton.shortcut = 'return'
notesField.fixedHeight = False

typePopup.width = accountnoField.width = 110
for label in [nameLabel, typeLabel, currencyLabel, accountnoLabel, notesLabel]:
    label.width = 60

layout = VHLayout([
    [titleLabel],
    [nameLabel, nameField],
    [typeLabel, typePopup],
    [currencyLabel, currencyCombo],
    [accountnoLabel, accountnoField],
    [notesLabel, notesField],
    [None, cancelButton, saveButton],
    ], hfillers={nameField, currencyCombo, notesField}, vfiller=notesField)
# The notes row is aligned above
layout.subviews[-2].align = Pack.Above
layout.moveTo(Pack.Left)
layout.moveTo(Pack.Above, margin=11)
layout.fill(Pack.LowerRight)
layout.setAnchor(Pack.Left, growX=True)
