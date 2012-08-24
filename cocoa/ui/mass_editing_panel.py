from collections import namedtuple
from common import FieldLabel, TitleLabel

ownerclass = 'MGMassEditionPanel'
ownerimport = 'MGMassEditionPanel.h'

Field = namedtuple('Field', 'label checkbox textfield')

FIELDDATA = [
    ('date', 'Date'),
    ('description', 'Description'),
    ('payee', 'Payee'),
    ('checkno', 'Check #'),
    ('from', 'From'),
    ('to', 'To'),
    ('amount', 'Amount'),
]
# Currency is special because it's a combobox

result = Window(377, 289, "")
titleLabel = TitleLabel(result, "Mass Editing")
fields = []
for name, label in FIELDDATA:
    label = FieldLabel(result, label)
    checkbox = Checkbox(result, "")
    textfield = TextField(result, "")
    textfield.controlSize = ControlSize.Small
    setattr(owner, '{}CheckBox'.format(name), checkbox)
    setattr(owner, '{}FieldView'.format(name), textfield)
    fields.append(Field(label, checkbox, textfield))
fields.append(Field(FieldLabel(result, "Currency"), Checkbox(result, ""), Combobox(result)))
owner.currencyCheckBox = fields[-1].checkbox
owner.currencyComboBoxView = fields[-1].textfield
cancelButton = Button(result, "Cancel", action=Action(owner, 'cancel:'))
saveButton = Button(result, "Save", action=Action(owner, 'save:'))

result.delegate = owner

result.canResize = False
saveButton.shortcut = 'return'
cancelButton.shortcut = 'esc'

for label, checkbox, textfield in fields:
    label.width = 66
    checkbox.width = 18
    textfield.width = 120
#... except the currency combo's, who's width is different
fields[-1].textfield.width = 200
saveButton.width = cancelButton.width = 84

titleLabel.moveTo(Pack.Left)
titleLabel.moveTo(Pack.Above, margin=11)
titleLabel.fill(Pack.Right)

layoutGrid = [[f.label, f.checkbox, f.textfield] for f in fields]
# fields[1] and fields[2] (description and payee) are hfillers because their field take up all
# the panel's width
fieldLayout = VHLayout(layoutGrid, hfillers={fields[1].textfield, fields[2].textfield}, vmargin=6)
fieldLayout.moveNextTo(titleLabel, Pack.Below)
fieldLayout.fill(Pack.Right)
saveButton.moveTo(Pack.LowerRight)
cancelButton.moveNextTo(saveButton, Pack.Left)
