ownerclass = 'MGLookup'
ownerimport = 'MGLookup.h'

result = Panel(251, 379, "Lookup")
searchField = SearchField(result, "")
namesList = ListView(result)

result.style = PanelStyle.Utility

owner.namesTable = namesList
owner.searchField = searchField
searchField.action = Action(owner, 'updateQuery')

searchField.packToCorner(Pack.UpperLeft, margin=0)
searchField.fill(Pack.Right, margin=0)
namesList.packRelativeTo(searchField, Pack.Below, margin=0)
namesList.fill(Pack.LowerRight, margin=0)
